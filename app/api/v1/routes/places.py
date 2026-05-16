from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.domain.models.cached_place import CachedPlace
from app.domain.schemas.place import PlaceResponse
from app.services.google_places_service import GooglePlacesService

router = APIRouter()


@router.get("/places/{place_id}", response_model=PlaceResponse)
async def get_place(
    place_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlaceResponse:
    result = await db.execute(
        select(CachedPlace).where(CachedPlace.google_place_id == place_id)
    )
    cached = result.scalar_one_or_none()

    if cached:
        google = GooglePlacesService()
        return PlaceResponse(
            google_place_id=cached.google_place_id,
            name=cached.name,
            rating=cached.rating,
            review_count=cached.review_count,
            latitude=cached.latitude,
            longitude=cached.longitude,
            main_photo_url=cached.main_photo_url,
            additional_photo_urls=cached.additional_photo_urls,
            opening_hours=cached.opening_hours,
            description=cached.description,
            google_maps_url=google.build_maps_url(
                cached.latitude or 0, cached.longitude or 0
            ),
        )

    google = GooglePlacesService()
    details = await google.get_place_details(place_id)
    info = google.extract_place_info(details)

    return PlaceResponse(
        google_place_id=place_id,
        google_maps_url=google.build_maps_url(
            info.get("latitude") or 0, info.get("longitude") or 0
        ),
        **info,
    )
