from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class CachedPlace(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "cached_places"

    google_place_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None]
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    main_photo_url: Mapped[str | None] = mapped_column(Text)
    additional_photo_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    opening_hours: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    description: Mapped[str | None] = mapped_column(Text)
    raw_json: Mapped[dict | None] = mapped_column(JSONB)
