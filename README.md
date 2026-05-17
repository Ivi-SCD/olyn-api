# Olyn - API

Backend da plataforma Olyn: roteiros inteligentes com IA e marketplace de guias turisticos para Olinda, PE.

Desenvolvido para o **Hackathon Olinda 500 Anos**.

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (async) + asyncpg
- Groq API (LLM: meta-llama/llama-4-scout-17b-16e-instruct)
- Google Maps APIs (Places, Distance Matrix)
- PostgreSQL
- uv (package manager)

## Funcionalidades

- **Onboarding** — Coleta preferencias do viajante (dias, interesses, orcamento, companhia)
- **Geracao de Roteiro com IA** — Prompt estruturado enviado ao Groq, retorna JSON com itinerario completo
- **Enriquecimento de Dados** — Google Places API adiciona fotos, avaliacoes, horarios, coordenadas
- **Calculo de Rotas** — Google Distance Matrix calcula tempo entre pontos
- **CRUD de Roteiros** — Listar, visualizar, editar titulo, excluir
- **Marketplace de Guias** — Listagem com filtros (especialidade, avaliacao, preco), seed de dados mock

## Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/onboarding` | Submeter preferencias |
| POST | `/api/v1/itineraries/generate` | Gerar roteiro com IA |
| GET | `/api/v1/itineraries` | Listar roteiros |
| GET | `/api/v1/itineraries/{id}` | Detalhe do roteiro |
| PATCH | `/api/v1/itineraries/{id}` | Atualizar titulo |
| DELETE | `/api/v1/itineraries/{id}` | Excluir roteiro |
| GET | `/api/v1/guides` | Listar guias (filtros: specialty, sort_by, available_only) |
| GET | `/api/v1/guides/{id}` | Detalhe do guia |
| POST | `/api/v1/guides/seed` | Popular guias mock |
| GET | `/api/v1/places/{place_id}` | Buscar local no Google Places |

## Desenvolvimento

```bash
# Instalar dependencias
uv sync

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com suas chaves

# Subir banco de dados (Podman/Docker)
docker compose up -d db

# Rodar servidor (tabelas criadas automaticamente)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Variaveis de Ambiente

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/olyn
GROQ_API_KEY=gsk_...
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
GOOGLE_MAPS_API_KEY=AIza...
```

## Estrutura

```
app/
  api/v1/routes/    # Endpoints REST
  core/             # Config, database, exceptions, logging
  domain/
    models/         # SQLAlchemy ORM models
    schemas/        # Pydantic v2 schemas
  services/         # Business logic (itinerary, google_places)
  prompts/          # Templates de prompt para o LLM
  main.py           # FastAPI app entry point
```

## Deploy

```bash
# Build da imagem
docker build -t olyn-api .

# Rodar com Docker Compose (API + PostgreSQL)
docker compose up
```

## Arquitetura

```
[Frontend] → /api/* proxy → [FastAPI Backend]
                                   ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              [Groq LLM]    [Google Maps]    [PostgreSQL]
              Gera roteiro   Enriquece dados  Persiste tudo
```
