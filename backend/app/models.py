from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_listings_source_source_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumb_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    junk_score: Mapped[int] = mapped_column(Integer, default=0)
    junk_flags: Mapped[str | None] = mapped_column(Text, default="")
