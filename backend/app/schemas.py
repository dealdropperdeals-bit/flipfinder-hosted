from datetime import datetime
from pydantic import BaseModel

class ListingOut(BaseModel):
    id: int
    source: str | None = None
    source_id: str | None = None
    url: str | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    location: str | None = None
    seller_name: str | None = None
    image_url: str | None = None
    thumb_url: str | None = None
    year: int | None = None
    mileage: int | None = None
    created_at: datetime | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    is_stale: bool = False
    junk_score: int = 0
    junk_flags: str | None = ""

    class Config:
        from_attributes = True
