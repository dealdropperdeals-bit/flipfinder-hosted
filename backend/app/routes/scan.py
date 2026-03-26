from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup
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


def clean_price(price_text: str) -> int | None:
    if not price_text:
        return None
    match = re.search(r"[\d,]+", price_text)
    if not match:
        return None
    try:
        return int(match.group(0).replace(",", ""))
    except ValueError:
        return None


@router.post("")
def run_scan(
    max_price: int = Query(default=6000, ge=1, le=50000),
    limit: int = Query(default=25, ge=1, le=100),
    query: str = Query(default="used cars"),
    db: Session = Depends(get_db),
):
    url = "https://www.ebay.com/sch/i.html"

    params = {
        "_nkw": query,
        "_udhi": max_price,
        "LH_BIN": "1",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=20)
        res.raise_for_status()
    except requests.RequestException as e:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "ebay",
            "query": query,
            "max_price": max_price,
            "limit": limit,
            "error": f"Request failed: {str(e)}",
        }

    html = res.text
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("li.s-item")

    if not rows:
        return {
            "created": 0,
            "checked": 0,
            "skipped_existing": 0,
            "skipped_invalid": 0,
            "source": "ebay",
            "query": query,
            "max_price": max_price,
            "limit": limit,
            "error": "No rows found",
            "status_code": res.status_code,
            "html_length": len(html),
            "html_preview": html[:1000],
        }

    created = 0
    checked = 0
    skipped_existing = 0
    skipped_invalid = 0

    for row in rows[:limit]:
        checked += 1

        title_el = row.select_one(".s-item__title")
        link_el = row.select_one(".s-item__link")
        price_el = row.select_one(".s-item__price")
        image_el = row.select_one(".s-item__image-img")

        if not title_el or not link_el or not price_el:
            skipped_invalid += 1
            continue

        title = title_el.get_text(strip=True)
        link = link_el.get("href", "").strip()
        price = clean_price(price_el.get_text(strip=True))

        if (
            not title
            or not link
            or not price
            or title.lower() == "shop on ebay"
        ):
            skipped_invalid += 1
            continue

        year = extract_year(title)
        image_url = image_el.get("src") if image_el else None

        payload = {
            "title": title,
            "description": "",
            "price": price,
            "year": year or 0,
            "seller_name": "eBay Seller",
            "location": "",
        }

        junk_score, junk_flags = score_listing(payload)

        source_id = link

        exists = (
            db.query(Listing)
            .filter_by(source="ebay", source_id=source_id)
            .first()
        )
        if exists:
            skipped_existing += 1
            continue

        now = datetime.utcnow()

        listing = Listing(
            source="ebay",
            source_id=source_id,
            url=link,
            title=title,
            description="",
            price=price,
            location="",
            seller_name="eBay Seller",
            image_url=image_url,
            thumb_url=image_url,
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
        "source": "ebay",
        "query": query,
        "max_price": max_price,
        "limit": limit,
        "status_code": res.status_code,
        "html_length": len(html),
    }