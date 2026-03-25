from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Listing
from ..schemas import ListingOut
from ..services.scoring import opportunity_bucket

router = APIRouter(prefix="/listings", tags=["listings"])

@router.get("", response_model=list[ListingOut])
def get_listings(
    min_price: int = Query(default=0),
    max_price: int = Query(default=1_000_000),
    max_junk_score: int = Query(default=100),
    hide_stale: bool = Query(default=True),
    bucket: str | None = Query(default=None, pattern="^(best|review|junk)?$"),
    sort: str = Query(default="last_seen"),
    direction: str = Query(default="desc"),
    db: Session = Depends(get_db),
):
    stmt = select(Listing).where(
        Listing.price.is_not(None),
        Listing.price >= min_price,
        Listing.price <= max_price,
        Listing.junk_score <= max_junk_score,
    )
    if hide_stale:
        stmt = stmt.where(or_(Listing.is_stale.is_(False), Listing.is_stale.is_(None)))
    rows = list(db.execute(stmt).scalars().all())
    if bucket:
        rows = [row for row in rows if opportunity_bucket(row.junk_score or 0) == bucket]
    sort_attr = {
        "price": Listing.price,
        "year": Listing.year,
        "mileage": Listing.mileage,
        "junk_score": Listing.junk_score,
        "last_seen": Listing.last_seen,
    }.get(sort, Listing.last_seen)
    stmt = select(Listing).where(Listing.id.in_([row.id for row in rows] or [-1]))
    stmt = stmt.order_by(desc(sort_attr) if direction == "desc" else asc(sort_attr))
    return list(db.execute(stmt).scalars().all())
