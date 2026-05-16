import uuid
from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class ItineraryDay(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "itinerary_days"

    itinerary_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("itineraries.id"))
    day_number: Mapped[int]
    date: Mapped[date]
    weekday: Mapped[str] = mapped_column(String(20))

    itinerary: Mapped["Itinerary"] = relationship(back_populates="days")
    items: Mapped[list["ItineraryItem"]] = relationship(
        back_populates="day", lazy="selectin", order_by="ItineraryItem.start_time"
    )


from app.domain.models.itinerary import Itinerary  # noqa: E402
from app.domain.models.itinerary_item import ItineraryItem  # noqa: E402
