from datetime import date
from uuid import UUID

from pydantic import BaseModel


class ItineraryItemSchema(BaseModel):
    start_time: str
    end_time: str
    place_name: str
    description: str | None = None
    historical_context: str | None = None
    rating: float | None = None
    review_count: int | None = None
    photo_url: str | None = None
    additional_photo_urls: list[str] | None = None
    opening_hours: list[str] | None = None
    travel_mode: str | None = None
    travel_time_minutes: int | None = None
    estimated_cost: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    google_maps_url: str | None = None


class ItineraryDaySchema(BaseModel):
    day_number: int
    date: date
    weekday: str
    items: list[ItineraryItemSchema]


class ItineraryResponse(BaseModel):
    id: UUID
    title: str
    days: list[ItineraryDaySchema]


class ItinerarySummary(BaseModel):
    id: UUID
    title: str
    num_days: int
    total_stops: int
    created_at: str


class ItineraryListResponse(BaseModel):
    itineraries: list[ItinerarySummary]


class GenerateRequest(BaseModel):
    session_id: UUID


class UpdateTitleRequest(BaseModel):
    title: str
