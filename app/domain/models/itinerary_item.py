import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class ItineraryItem(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "itinerary_items"

    day_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("itinerary_days.id"))
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str] = mapped_column(String(5))
    place_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    historical_context: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None]
    photo_url: Mapped[str | None] = mapped_column(Text)
    additional_photo_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    opening_hours: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    travel_mode: Mapped[str | None] = mapped_column(String(20))
    travel_time_minutes: Mapped[int | None]
    estimated_cost: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    google_maps_url: Mapped[str | None] = mapped_column(Text)
    google_place_id: Mapped[str | None] = mapped_column(String(255))

    day: Mapped["ItineraryDay"] = relationship(back_populates="items")


from app.domain.models.itinerary_day import ItineraryDay  # noqa: E402
