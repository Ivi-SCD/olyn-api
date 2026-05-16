from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.domain.models import Base
from app.api.v1.routes import guides, health, itineraries, onboarding, places


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(onboarding.router, prefix="/api/v1", tags=["onboarding"])
app.include_router(itineraries.router, prefix="/api/v1", tags=["itineraries"])
app.include_router(places.router, prefix="/api/v1", tags=["places"])
app.include_router(guides.router, prefix="/api/v1", tags=["guides"])
