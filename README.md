# Olyn API

AI-powered travel planner for Olinda, Pernambuco, Brazil — built for the Olinda 500 Years Hackathon.

## Tech Stack

- **Python 3.12+** with **FastAPI** and **Pydantic v2**
- **SQLAlchemy 2.0** (async)
- **Groq API** (llama-3.3-70b-versatile) for AI itinerary generation
- **Google Maps APIs** (Places, Distance Matrix) for place enrichment
- **PostgreSQL** (Supabase-compatible)

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required keys:
- `DATABASE_URL` — PostgreSQL async connection string
- `GROQ_API_KEY` — from console.groq.com
- `GOOGLE_MAPS_API_KEY` — with Places, Distance Matrix, and Geocoding APIs enabled

### 3. Run with Docker Compose

```bash
docker compose up --build
```

### 4. Or run locally

```bash
# Start PostgreSQL (e.g. via Docker)
docker compose up db -d

# Start the server
uvicorn app.main:app --reload
```

### 5. Open API docs

Visit [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) for the interactive Swagger UI.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/onboarding` | Save traveler profile |
| `POST` | `/api/v1/itineraries/generate` | Generate AI itinerary |
| `GET` | `/api/v1/itineraries/{id}` | Retrieve itinerary |
| `GET` | `/api/v1/places/{place_id}` | Get place details |
| `GET` | `/api/v1/health` | Health check |

## Flow

1. **POST /onboarding** — Send travel preferences (days, dates, interests, budget, companions)
2. **POST /itineraries/generate** — Pass the `session_id` from step 1 to generate the itinerary
3. **GET /itineraries/{id}** — Fetch the full itinerary with enriched Google Places data
