import logging
from typing import Any

import aiohttp

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"
DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


class GooglePlacesService:
    def __init__(self) -> None:
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    async def search_place(self, name: str) -> dict[str, Any] | None:
        params = {
            "input": f"{name}, Olinda, Pernambuco",
            "inputtype": "textquery",
            "fields": "place_id,name,geometry,formatted_address",
            "key": self.api_key,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(PLACES_SEARCH_URL, params=params) as resp:
                data = await resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            logger.warning("No Google Places result for: %s", name)
            return None
        return candidates[0]

    async def get_place_details(self, place_id: str) -> dict[str, Any]:
        params = {
            "place_id": place_id,
            "fields": (
                "name,rating,user_ratings_total,geometry,photos,"
                "opening_hours,formatted_address,editorial_summary,types"
            ),
            "key": self.api_key,
            "language": "pt-BR",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(PLACE_DETAILS_URL, params=params) as resp:
                data = await resp.json()

        result = data.get("result")
        if not result:
            raise ExternalServiceError("Google Places", f"No details for {place_id}")
        return result

    def build_photo_url(self, photo_reference: str, max_width: int = 800) -> str:
        return (
            f"{PHOTO_URL}?maxwidth={max_width}"
            f"&photo_reference={photo_reference}"
            f"&key={self.api_key}"
        )

    def build_maps_url(self, lat: float, lng: float) -> str:
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"

    async def get_travel_time(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving",
    ) -> int | None:
        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "mode": mode,
            "key": self.api_key,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(DISTANCE_MATRIX_URL, params=params) as resp:
                data = await resp.json()

        try:
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                return element["duration"]["value"] // 60
        except (KeyError, IndexError):
            pass
        return None

    def extract_place_info(self, details: dict[str, Any]) -> dict[str, Any]:
        photos = details.get("photos", [])
        photo_refs = [p["photo_reference"] for p in photos[:5]]
        location = details.get("geometry", {}).get("location", {})

        opening_hours_raw = details.get("opening_hours", {})
        weekday_text = opening_hours_raw.get("weekday_text", [])

        return {
            "name": details.get("name", ""),
            "rating": details.get("rating"),
            "review_count": details.get("user_ratings_total"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "main_photo_url": self.build_photo_url(photo_refs[0]) if photo_refs else None,
            "additional_photo_urls": [self.build_photo_url(r) for r in photo_refs[1:]],
            "opening_hours": weekday_text,
            "description": details.get("editorial_summary", {}).get("overview", ""),
        }
