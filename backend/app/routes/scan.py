from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import random

from ..db import get_db
from ..models import Listing
from ..services.scoring import score_listing

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("")
def run_scan(db: Session = Depends(get_db)):
    created = 0

    sample_titles = [
        "2012 Honda Accord LX",
        "2015 Toyota Camry SE",
        "2010 Ford Focus",
        "2018 Nissan Altima",
        "2013 Chevy Malibu"
    ]

    for i in range(10):
        title = random.choice(sample_titles)
        price = random.randint(800, 6000)
        year = random.randint(2008, 2018)

        payload = {
            "title": title,
            "description": "Runs good, clean title",
            "price": price,
            "year": year,
            "seller_name": "Private Seller",
            "location": "Orlando, FL"
        }

        junk_score, junk_flags = score_listing(payload)

        # Prevent duplicates using source_id
        source_id = f"demo-{title}-{price}-{i}"

        exists = db.query(Listing).filter_by(source="demo", source_id=source_id).first()
        if exists:
            continue

        listing = Listing(
            source="demo",
            source_id=source_id,
            url="https://example.com",
            title=title,
            description=payload["description"],
            price=price,
            location=payload["location"],
            seller_name=payload["seller_name"],
            image_url=None,
            thumb_url=None,
            year=year,
            mileage=random.randint(80000, 180000),
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