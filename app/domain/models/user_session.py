from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class UserSession(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "user_sessions"

    device_fingerprint: Mapped[str | None] = mapped_column()

    traveler_profile: Mapped["TravelerProfile | None"] = relationship(
        back_populates="session", lazy="selectin"
    )
    itineraries: Mapped[list["Itinerary"]] = relationship(
        back_populates="session", lazy="selectin"
    )


from app.domain.models.traveler_profile import TravelerProfile  # noqa: E402
from app.domain.models.itinerary import Itinerary  # noqa: E402
