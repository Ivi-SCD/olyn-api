import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class Itinerary(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "itineraries"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_sessions.id"))
    title: Mapped[str] = mapped_column(String(255))

    session: Mapped["UserSession"] = relationship(back_populates="itineraries")
    days: Mapped[list["ItineraryDay"]] = relationship(
        back_populates="itinerary", lazy="selectin", order_by="ItineraryDay.day_number"
    )


from app.domain.models.user_session import UserSession  # noqa: E402
from app.domain.models.itinerary_day import ItineraryDay  # noqa: E402
