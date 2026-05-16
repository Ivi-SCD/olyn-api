from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums.travel import BudgetLevel, CompanionType


class InterestsSchema(BaseModel):
    history: float = Field(0.5, ge=0.0, le=1.0)
    art_and_culture: float = Field(0.5, ge=0.0, le=1.0)
    handicrafts: float = Field(0.5, ge=0.0, le=1.0)
    nature: float = Field(0.5, ge=0.0, le=1.0)
    shopping: float = Field(0.5, ge=0.0, le=1.0)
    gastronomy: float = Field(0.5, ge=0.0, le=1.0)
    nightlife: float = Field(0.5, ge=0.0, le=1.0)


class OnboardingRequest(BaseModel):
    num_days: int = Field(..., ge=1, le=30)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    start_date: date
    end_date: date
    companion_type: CompanionType
    interests: InterestsSchema
    budget: BudgetLevel
    device_fingerprint: str | None = None


class OnboardingResponse(BaseModel):
    session_id: str
    profile_id: str
    message: str = "Profile saved successfully"
