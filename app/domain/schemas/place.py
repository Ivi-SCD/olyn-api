from pydantic import BaseModel


class PlaceResponse(BaseModel):
    google_place_id: str
    name: str
    rating: float | None = None
    review_count: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    main_photo_url: str | None = None
    additional_photo_urls: list[str] | None = None
    opening_hours: list[str] | None = None
    description: str | None = None
    google_maps_url: str | None = None
