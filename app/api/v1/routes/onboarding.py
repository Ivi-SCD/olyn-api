from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.models.traveler_profile import TravelerProfile
from app.domain.models.user_session import UserSession
from app.domain.schemas.onboarding import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.post("/onboarding", response_model=OnboardingResponse)
async def create_profile(
    body: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    session = UserSession(device_fingerprint=body.device_fingerprint)
    db.add(session)
    await db.flush()

    profile = TravelerProfile(
        session_id=session.id,
        num_days=body.num_days,
        start_time=body.start_time,
        end_time=body.end_time,
        start_date=body.start_date,
        end_date=body.end_date,
        companion_type=body.companion_type.value,
        interests=body.interests.model_dump(),
        budget=body.budget.value,
    )
    db.add(profile)
    await db.commit()

    return OnboardingResponse(
        session_id=str(session.id),
        profile_id=str(profile.id),
    )
