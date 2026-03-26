from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from ..db import get_db
from ..models import Listing
from ..services.scoring import score_listing

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("")
def run_scan(db: Session = Depends(get_db)):
    url = "https://orlando.craigslist.org/search/cta?max_price=6000"

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select(".result-row")

    created = 0

    for row in rows[:20]:
        title_el = row.select_one(".result-title")
        price_el = row.select_one(".result-price")

        if not title_el or not price_el:
            continue

        title = title_el.text.strip()
        price = int(price_el.text.replace("$", "").replace(",", ""))

        link = title_el["href"]

        payload = {
            "title": title,
            "description": "",
            "price": price,
            "year": 0,
            "seller_name": "",
            "location": "Orlando, FL"
        }

        junk_score, junk_flags = score_listing(payload)

        source_id = link

        exists = db.query(Listing).filter_by(source="craigslist", source_id=source_id).first()
        if exists:
            continue

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
            year=None,
            mileage=None,
            created_at=datetime.utcnow(),
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            is_stale=False,
            junk_score=junk_score,
            junk_flags=junk_flags
        )

        db.add(listing)
        created += 1

    db.commit()

    return {"created": created}