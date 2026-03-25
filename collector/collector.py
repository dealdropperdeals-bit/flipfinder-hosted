from datetime import datetime
from sqlalchemy import text
from db import SessionLocal
from scoring import score_listing

SAMPLE_LISTINGS = [
    {
        "source": "facebook",
        "source_id": "sample-1",
        "url": "https://example.com/listing/1",
        "title": "2014 Honda Civic EX",
        "description": "Clean car. Private seller. 168k miles.",
        "price": 5200,
        "location": "Orlando, FL",
        "seller_name": "John R",
        "image_url": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8",
        "thumb_url": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=640",
        "year": 2014,
        "mileage": 168000,
    },
    {
        "source": "facebook",
        "source_id": "sample-2",
        "url": "https://example.com/listing/2",
        "title": "2017 Toyota Camry SE",
        "description": "Low down payment. Easy financing. Call today.",
        "price": 2400,
        "location": "Kissimmee, FL",
        "seller_name": "Sunshine Auto Sales",
        "image_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70",
        "thumb_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=640",
        "year": 2017,
        "mileage": 114000,
    },
]

UPSERT_SQL = text("""
INSERT INTO listings (
    source, source_id, url, title, description, price, location, seller_name,
    image_url, thumb_url, year, mileage, created_at, first_seen, last_seen,
    is_stale, junk_score, junk_flags
)
VALUES (
    :source, :source_id, :url, :title, :description, :price, :location, :seller_name,
    :image_url, :thumb_url, :year, :mileage, :created_at, :first_seen, :last_seen,
    :is_stale, :junk_score, :junk_flags
)
ON CONFLICT (source, source_id)
DO UPDATE SET
    url = EXCLUDED.url,
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    location = EXCLUDED.location,
    seller_name = EXCLUDED.seller_name,
    image_url = EXCLUDED.image_url,
    thumb_url = EXCLUDED.thumb_url,
    year = EXCLUDED.year,
    mileage = EXCLUDED.mileage,
    last_seen = EXCLUDED.last_seen,
    is_stale = EXCLUDED.is_stale,
    junk_score = EXCLUDED.junk_score,
    junk_flags = EXCLUDED.junk_flags
""")

def enrich_listing(payload: dict) -> dict:
    now = datetime.utcnow()
    score, flags = score_listing(payload)
    payload = payload.copy()
    payload["junk_score"] = score
    payload["junk_flags"] = flags
    payload["created_at"] = payload.get("created_at") or now
    payload["first_seen"] = payload.get("first_seen") or now
    payload["last_seen"] = now
    payload["is_stale"] = bool(payload.get("is_stale", False))
    return payload

def main():
    session = SessionLocal()
    try:
        for raw in SAMPLE_LISTINGS:
            session.execute(UPSERT_SQL, enrich_listing(raw))
        session.commit()
        print(f"Upserted {len(SAMPLE_LISTINGS)} sample listings")
    finally:
        session.close()

if __name__ == "__main__":
    main()
