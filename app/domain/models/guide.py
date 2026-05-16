from sqlalchemy import Float, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class TourGuide(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "tour_guides"

    name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    total_tours: Mapped[int] = mapped_column(Integer, default=0)
    languages: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    specialties: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    hourly_rate: Mapped[float] = mapped_column(Float, default=50.0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp: Mapped[str | None] = mapped_column(String(20))
    instagram: Mapped[str | None] = mapped_column(String(100))
    featured_places: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    response_time_minutes: Mapped[int] = mapped_column(Integer, default=30)
