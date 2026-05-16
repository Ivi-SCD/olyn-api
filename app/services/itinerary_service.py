import asyncio
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AIGenerationError, NotFoundException
from app.domain.models.cached_place import CachedPlace
from app.domain.models.itinerary import Itinerary
from app.domain.models.itinerary_day import ItineraryDay
from app.domain.models.itinerary_item import ItineraryItem
from app.domain.models.traveler_profile import TravelerProfile
from app.prompts.itinerary_prompt import build_itinerary_prompt
from app.services.google_places_service import GooglePlacesService
from app.services.groq_service import GroqService

logger = logging.getLogger(__name__)


class ItineraryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.groq = GroqService()
        self.google = GooglePlacesService()

    async def generate(self, session_id: UUID) -> Itinerary:
        profile = await self._get_profile(session_id)
        prompt = build_itinerary_prompt(
            num_days=profile.num_days,
            start_time=profile.start_time,
            end_time=profile.end_time,
            start_date=profile.start_date,
            companion_type=profile.companion_type,
            interests=profile.interests,
            budget=profile.budget,
        )

        raw = await self.groq.generate_itinerary(prompt)
        days_data = raw.get("days", [])
        if not days_data:
            raise AIGenerationError(detail="LLM returned no days")

        place_names = self._extract_place_names(days_data)
        place_info = await self._enrich_places(place_names)

        itinerary = await self._persist(session_id, raw, days_data, place_info)
        return itinerary

    async def get_by_id(self, itinerary_id: UUID) -> Itinerary:
        result = await self.db.execute(
            select(Itinerary)
            .where(Itinerary.id == itinerary_id)
            .options(
                selectinload(Itinerary.days).selectinload(ItineraryDay.items)
            )
        )
        itinerary = result.scalar_one_or_none()
        if not itinerary:
            raise NotFoundException(f"Itinerary {itinerary_id} not found")
        return itinerary

    async def _get_profile(self, session_id: UUID) -> TravelerProfile:
        result = await self.db.execute(
            select(TravelerProfile).where(TravelerProfile.session_id == session_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundException("No traveler profile found for this session")
        return profile

    def _extract_place_names(self, days_data: list[dict]) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for day in days_data:
            for item in day.get("items", []):
                name = item.get("place_name", "")
                if name and name not in seen:
                    names.append(name)
                    seen.add(name)
        return names

    async def _enrich_places(self, place_names: list[str]) -> dict[str, dict]:
        results: dict[str, dict] = {}
        to_fetch: list[str] = []

        for name in place_names:
            cached = await self._get_cached(name)
            if cached:
                results[name] = cached
            else:
                to_fetch.append(name)

        async def fetch_from_google(name: str) -> tuple[str, dict]:
            search = await self.google.search_place(name)
            if not search:
                return name, {}

            place_id = search["place_id"]
            details = await self.google.get_place_details(place_id)
            info = self.google.extract_place_info(details)
            info["google_place_id"] = place_id
            info["google_maps_url"] = self.google.build_maps_url(
                info["latitude"], info["longitude"]
            )
            info["_raw_details"] = details
            return name, info

        fetched = await asyncio.gather(*(fetch_from_google(n) for n in to_fetch))

        for name, info in fetched:
            if info and info.get("google_place_id"):
                raw = info.pop("_raw_details", {})
                await self._cache_place(info["google_place_id"], info, raw)
            results[name] = info

        return results

    async def _get_cached(self, name: str) -> dict | None:
        result = await self.db.execute(
            select(CachedPlace).where(CachedPlace.name == name)
        )
        cached = result.scalar_one_or_none()
        if not cached:
            return None
        return {
            "google_place_id": cached.google_place_id,
            "name": cached.name,
            "rating": cached.rating,
            "review_count": cached.review_count,
            "latitude": cached.latitude,
            "longitude": cached.longitude,
            "main_photo_url": cached.main_photo_url,
            "additional_photo_urls": cached.additional_photo_urls or [],
            "opening_hours": cached.opening_hours or [],
            "description": cached.description,
            "google_maps_url": self.google.build_maps_url(
                cached.latitude or 0, cached.longitude or 0
            ),
        }

    async def _cache_place(
        self, place_id: str, info: dict, raw_details: dict
    ) -> None:
        existing = await self.db.execute(
            select(CachedPlace).where(CachedPlace.google_place_id == place_id)
        )
        if existing.scalar_one_or_none():
            return

        cached = CachedPlace(
            google_place_id=place_id,
            name=info["name"],
            rating=info.get("rating"),
            review_count=info.get("review_count"),
            latitude=info.get("latitude"),
            longitude=info.get("longitude"),
            main_photo_url=info.get("main_photo_url"),
            additional_photo_urls=info.get("additional_photo_urls"),
            opening_hours=info.get("opening_hours"),
            description=info.get("description"),
            raw_json=raw_details,
        )
        self.db.add(cached)

    async def _compute_travel_times(
        self, items_data: list[dict], place_info: dict[str, dict]
    ) -> list[int | None]:
        times: list[int | None] = [None]
        for i in range(1, len(items_data)):
            prev_name = items_data[i - 1].get("place_name", "")
            curr_name = items_data[i].get("place_name", "")
            prev = place_info.get(prev_name, {})
            curr = place_info.get(curr_name, {})

            if prev.get("latitude") and curr.get("latitude"):
                t = await self.google.get_travel_time(
                    prev["latitude"],
                    prev["longitude"],
                    curr["latitude"],
                    curr["longitude"],
                    mode="walking",
                )
                times.append(t)
            else:
                times.append(None)
        return times

    async def _persist(
        self,
        session_id: UUID,
        raw: dict,
        days_data: list[dict],
        place_info: dict[str, dict],
    ) -> Itinerary:
        itinerary = Itinerary(
            session_id=session_id,
            title=raw.get("title", "Olinda Itinerary"),
        )
        self.db.add(itinerary)
        await self.db.flush()

        for day_data in days_data:
            day = ItineraryDay(
                itinerary_id=itinerary.id,
                day_number=day_data["day_number"],
                date=datetime.strptime(day_data["date"], "%Y-%m-%d").date(),
                weekday=day_data.get("weekday", ""),
            )
            self.db.add(day)
            await self.db.flush()

            items_data = day_data.get("items", [])
            travel_times = await self._compute_travel_times(items_data, place_info)

            for idx, item_data in enumerate(items_data):
                pname = item_data.get("place_name", "")
                pinfo = place_info.get(pname, {})

                item = ItineraryItem(
                    day_id=day.id,
                    start_time=item_data.get("start_time", ""),
                    end_time=item_data.get("end_time", ""),
                    place_name=pname,
                    description=item_data.get("description"),
                    historical_context=item_data.get("historical_context"),
                    rating=pinfo.get("rating"),
                    review_count=pinfo.get("review_count"),
                    photo_url=pinfo.get("main_photo_url"),
                    additional_photo_urls=pinfo.get("additional_photo_urls"),
                    opening_hours=pinfo.get("opening_hours"),
                    travel_mode=item_data.get("travel_mode", "WALKING"),
                    travel_time_minutes=travel_times[idx],
                    estimated_cost=item_data.get("estimated_cost", 0),
                    latitude=pinfo.get("latitude"),
                    longitude=pinfo.get("longitude"),
                    google_maps_url=pinfo.get("google_maps_url"),
                    google_place_id=pinfo.get("google_place_id"),
                )
                self.db.add(item)

        await self.db.commit()

        result = await self.db.execute(
            select(Itinerary)
            .where(Itinerary.id == itinerary.id)
            .options(
                selectinload(Itinerary.days).selectinload(ItineraryDay.items)
            )
        )
        return result.scalar_one()
