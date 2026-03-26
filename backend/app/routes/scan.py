from datetime import datetime
import json
import re

import requests
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Listing
from ..services.scoring import score_listing

router = APIRouter(prefix="/scan", tags=["scan"])


def extract_year(text: str) -> int | None:
    match = re.search(r"\b(19[89]\d|20[0-2]\d)\b", text or "")
    if match:
        year = int(match.group(1))
        if 1980 <= year <= 2029:
            return year
    return None


@router.post("")
def run_scan(
    max_price: int = Query(default=6000, ge=1, le=50000),
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    url = f"https://orlando.craigslist.org/search/cta?sort=date&max_price={max_price}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    try:
        res = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as e:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "craigslist",
            "max_price": max_price,
            "limit": limit,
            "scan_url": url,
            "error": f"Request failed: {str(e)}",
        }

    html = res.text

    if "captcha" in html.lower() or "blocked" in html.lower():
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "craigslist",
            "max_price": max_price,
            "limit": limit,
            "scan_url": url,
            "error": "Blocked or captcha detected",
            "status_code": res.status_code,
            "html_length": len(html),
            "html_preview": html[:1000],
        }

    start = html.find('id="ld_searchpage_data"')
    if start == -1:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "craigslist",
            "max_price": max_price,
            "limit": limit,
            "scan_url": url,
            "error": "JSON data not found",
            "status_code": res.status_code,
            "html_length": len(html),
            "html_preview": html[:1000],
        }

    script_start = html.find(">", start) + 1
    script_end = html.find("</script>", script_start)
    json_text = html[script_start:script_end].strip()

    try:
        data = json.loads(json_text)
    except Exception as e:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "craigslist",
            "max_price": max_price,
            "limit": limit,
            "scan_url": url,
            "error": f"JSON parse failed: {str(e)}",
            "status_code": res.status_code,
            "json_preview": json_text[:500],
        }

    items = data.get("itemListElement", [])
    if not items:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "craigslist",
            "max_price": max_price,
            "limit": limit,
            "scan_url": url,
            "error": "No items in JSON",
            "status_code": res.status_code,
            "json_preview": json_text[:500],
        }

    created = 0
    checked = 0
    skipped_existing = 0
    skipped_invalid = 0

    for item in items[:limit]:
        checked += 1

        listing_data = item.get("item", {})
        title = listing_data.get("name", "")
        link = listing_data.get("url", "")

        offers = listing_data.get("offers", {})
        price = offers.get("price")

        if not title or not link or price is None:
            skipped_invalid += 1
            continue

        try:
            price = int(float(price))
        except (ValueError, TypeError):
            skipped_invalid += 1
            continue

        year = extract_year(title)

        payload = {
            "title": title,
            "description": "",
            "price": price,
            "year": year or 0,
            "seller_name": "",
            "location": "Orlando, FL",
        }

        junk_score, junk_flags = score_listing(payload)

        source_id = link

        exists = (
            db.query(Listing)
            .filter_by(source="craigslist", source_id=source_id)
            .first()
        )
        if exists:
            skipped_existing += 1
            continue

        now = datetime.utcnow()

        listing = Listing(
            source="craigslist",
            source_id=source_id,
            url=link,
            title=title,
            description="",
            price=price,
            location="Orlando, FL",
            seller_name="",
            image_url=None,
            thumb_url=None,
            year=year,
            mileage=None,
            created_at=now,
            first_seen=now,
            last_seen=now,
            is_stale=False,
            junk_score=junk_score,
            junk_flags=junk_flags,
        )

        db.add(listing)
        created += 1

    db.commit()

    return {
        "created": created,
        "checked": checked,
        "skipped_existing": skipped_existing,
        "skipped_invalid": skipped_invalid,
        "source": "craigslist",
        "max_price": max_price,
        "limit": limit,
        "scan_url": url,
        "status_code": res.status_code,
        "html_length": len(html),
    }