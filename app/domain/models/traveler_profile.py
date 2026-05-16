import uuid
from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin, UUIDPrimaryKey


class TravelerProfile(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "traveler_profiles"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_sessions.id"), unique=True
    )
    num_days: Mapped[int]
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str] = mapped_column(String(5))
    start_date: Mapped[date]
    end_date: Mapped[date]
    companion_type: Mapped[str] = mapped_column(String(20))
    interests: Mapped[dict] = mapped_column(JSONB, default=dict)
    budget: Mapped[str] = mapped_column(String(20))

    session: Mapped["UserSession"] = relationship(back_populates="traveler_profile")


from app.domain.models.user_session import UserSession  # noqa: E402
