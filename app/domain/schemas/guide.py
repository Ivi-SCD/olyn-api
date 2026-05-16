from uuid import UUID

from pydantic import BaseModel


class GuideResponse(BaseModel):
    id: UUID
    name: str
    bio: str | None = None
    avatar_url: str | None = None
    rating: float
    total_reviews: int
    total_tours: int
    languages: list[str] | None = None
    specialties: list[str] | None = None
    hourly_rate: float
    is_available: bool
    verified: bool
    whatsapp: str | None = None
    instagram: str | None = None
    featured_places: list[str] | None = None
    response_time_minutes: int


class GuideListResponse(BaseModel):
    guides: list[GuideResponse]
    total: int
