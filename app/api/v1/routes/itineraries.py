from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.domain.models.itinerary import Itinerary
from app.domain.models.itinerary_day import ItineraryDay
from app.domain.models.itinerary_item import ItineraryItem
from app.domain.schemas.itinerary import (
    GenerateRequest,
    ItineraryDaySchema,
    ItineraryItemSchema,
    ItineraryListResponse,
    ItineraryResponse,
    ItinerarySummary,
    UpdateTitleRequest,
)
from app.services.itinerary_service import ItineraryService

router = APIRouter()


def _to_response(itinerary) -> ItineraryResponse:
    days = []
    for day in itinerary.days:
        items = [
            ItineraryItemSchema(
                start_time=item.start_time,
                end_time=item.end_time,
                place_name=item.place_name,
                description=item.description,
                historical_context=item.historical_context,
                rating=item.rating,
                review_count=item.review_count,
                photo_url=item.photo_url,
                additional_photo_urls=item.additional_photo_urls,
                opening_hours=item.opening_hours,
                travel_mode=item.travel_mode,
                travel_time_minutes=item.travel_time_minutes,
                estimated_cost=item.estimated_cost,
                latitude=item.latitude,
                longitude=item.longitude,
                google_maps_url=item.google_maps_url,
            )
            for item in day.items
        ]
        days.append(
            ItineraryDaySchema(
                day_number=day.day_number,
                date=day.date,
                weekday=day.weekday,
                items=items,
            )
        )
    return ItineraryResponse(id=itinerary.id, title=itinerary.title, days=days)


@router.get("/itineraries", response_model=ItineraryListResponse)
async def list_itineraries(
    session_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ItineraryListResponse:
    query = (
        select(Itinerary)
        .options(selectinload(Itinerary.days).selectinload(ItineraryDay.items))
        .order_by(Itinerary.created_at.desc())
    )
    if session_id:
        query = query.where(Itinerary.session_id == session_id)

    result = await db.execute(query)
    itineraries = result.scalars().all()

    summaries = []
    for it in itineraries:
        total_stops = sum(len(d.items) for d in it.days)
        summaries.append(
            ItinerarySummary(
                id=it.id,
                title=it.title,
                num_days=len(it.days),
                total_stops=total_stops,
                created_at=it.created_at.isoformat() if it.created_at else "",
            )
        )

    return ItineraryListResponse(itineraries=summaries)


@router.post("/itineraries/generate", response_model=ItineraryResponse)
async def generate_itinerary(
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    service = ItineraryService(db)
    itinerary = await service.generate(body.session_id)
    return _to_response(itinerary)


@router.get("/itineraries/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    service = ItineraryService(db)
    itinerary = await service.get_by_id(itinerary_id)
    return _to_response(itinerary)


@router.patch("/itineraries/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(
    itinerary_id: UUID,
    body: UpdateTitleRequest,
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .options(selectinload(Itinerary.days).selectinload(ItineraryDay.items))
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise NotFoundException(f"Itinerary {itinerary_id} not found")

    itinerary.title = body.title
    await db.commit()
    await db.refresh(itinerary)

    result2 = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .options(selectinload(Itinerary.days).selectinload(ItineraryDay.items))
    )
    return _to_response(result2.scalar_one())


@router.delete("/itineraries/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .options(selectinload(Itinerary.days).selectinload(ItineraryDay.items))
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise NotFoundException(f"Itinerary {itinerary_id} not found")

    for day in itinerary.days:
        for item in day.items:
            await db.delete(item)
        await db.delete(day)
    await db.delete(itinerary)
    await db.commit()
    return {"message": "Itinerary deleted"}
