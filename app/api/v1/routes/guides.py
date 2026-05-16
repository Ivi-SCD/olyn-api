from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.domain.models.guide import TourGuide
from app.domain.schemas.guide import GuideListResponse, GuideResponse

router = APIRouter()


@router.get("/guides", response_model=GuideListResponse)
async def list_guides(
    specialty: str | None = Query(None),
    available_only: bool = Query(True),
    sort_by: str = Query("rating"),
    db: AsyncSession = Depends(get_db),
) -> GuideListResponse:
    query = select(TourGuide)
    if available_only:
        query = query.where(TourGuide.is_available.is_(True))
    if specialty:
        query = query.where(TourGuide.specialties.contains([specialty]))
    if sort_by == "rating":
        query = query.order_by(TourGuide.rating.desc())
    elif sort_by == "price_low":
        query = query.order_by(TourGuide.hourly_rate.asc())
    elif sort_by == "reviews":
        query = query.order_by(TourGuide.total_reviews.desc())

    result = await db.execute(query)
    guides = result.scalars().all()

    count_result = await db.execute(select(func.count(TourGuide.id)))
    total = count_result.scalar() or 0

    return GuideListResponse(
        guides=[
            GuideResponse(
                id=g.id,
                name=g.name,
                bio=g.bio,
                avatar_url=g.avatar_url,
                rating=g.rating,
                total_reviews=g.total_reviews,
                total_tours=g.total_tours,
                languages=g.languages,
                specialties=g.specialties,
                hourly_rate=g.hourly_rate,
                is_available=g.is_available,
                verified=g.verified,
                whatsapp=g.whatsapp,
                instagram=g.instagram,
                featured_places=g.featured_places,
                response_time_minutes=g.response_time_minutes,
            )
            for g in guides
        ],
        total=total,
    )


@router.get("/guides/{guide_id}", response_model=GuideResponse)
async def get_guide(
    guide_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> GuideResponse:
    result = await db.execute(select(TourGuide).where(TourGuide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise NotFoundException("Guide not found")

    return GuideResponse(
        id=guide.id,
        name=guide.name,
        bio=guide.bio,
        avatar_url=guide.avatar_url,
        rating=guide.rating,
        total_reviews=guide.total_reviews,
        total_tours=guide.total_tours,
        languages=guide.languages,
        specialties=guide.specialties,
        hourly_rate=guide.hourly_rate,
        is_available=guide.is_available,
        verified=guide.verified,
        whatsapp=guide.whatsapp,
        instagram=guide.instagram,
        featured_places=guide.featured_places,
        response_time_minutes=guide.response_time_minutes,
    )


@router.post("/guides/seed")
async def seed_guides(db: AsyncSession = Depends(get_db)) -> dict:
    """Seed mock tour guides for demonstration."""
    existing = await db.execute(select(func.count(TourGuide.id)))
    if (existing.scalar() or 0) > 0:
        return {"message": "Guides already seeded"}

    mock_guides = [
        TourGuide(
            name="Maria do Carmo Silva",
            bio="Historiadora e guia certificada há 12 anos. Especialista em arquitetura colonial e arte sacra barroca de Olinda.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=maria",
            rating=4.9,
            total_reviews=234,
            total_tours=580,
            languages=["Português", "Inglês", "Espanhol"],
            specialties=["História", "Arte e Cultura", "Arquitetura"],
            hourly_rate=80.0,
            is_available=True,
            verified=True,
            whatsapp="+5581999990001",
            instagram="@mariadocarmo.olinda",
            featured_places=["Alto da Sé", "Mosteiro de São Bento", "Convento de São Francisco"],
            response_time_minutes=15,
        ),
        TourGuide(
            name="João Pedro Santos",
            bio="Nascido e criado em Olinda. Conheço cada beco, cada ladeira e cada história que as paredes contam. Tour gastronômico é minha especialidade.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=joao",
            rating=4.8,
            total_reviews=187,
            total_tours=420,
            languages=["Português", "Inglês"],
            specialties=["Gastronomia", "Vida Noturna", "Cultura Popular"],
            hourly_rate=60.0,
            is_available=True,
            verified=True,
            whatsapp="+5581999990002",
            instagram="@jp.olindaturismo",
            featured_places=["Mercado da Ribeira", "Bodega do Véio", "Alto da Sé"],
            response_time_minutes=10,
        ),
        TourGuide(
            name="Ana Beatriz Freitas",
            bio="Artista plástica e arte-educadora. Levo visitantes pelos ateliês, galerias e espaços criativos de Olinda.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=ana",
            rating=4.9,
            total_reviews=156,
            total_tours=310,
            languages=["Português", "Francês", "Inglês"],
            specialties=["Arte e Cultura", "Artesanato", "Ateliês"],
            hourly_rate=70.0,
            is_available=True,
            verified=True,
            whatsapp="+5581999990003",
            instagram="@anabeatriz.arte",
            featured_places=["Ateliê Bajado", "Mercado Eufrásio Barbosa", "Rua do Amparo"],
            response_time_minutes=20,
        ),
        TourGuide(
            name="Ricardo Mendonça",
            bio="Fotógrafo e guia de ecoturismo. Trilhas, mirantes e praias secretas fazem parte dos meus roteiros.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=ricardo",
            rating=4.7,
            total_reviews=98,
            total_tours=190,
            languages=["Português", "Inglês"],
            specialties=["Natureza", "Fotografia", "Praias"],
            hourly_rate=55.0,
            is_available=True,
            verified=False,
            whatsapp="+5581999990004",
            instagram="@ricardo.olindanature",
            featured_places=["Praia do Farol", "Jardim Botânico", "Rio Beberibe"],
            response_time_minutes=25,
        ),
        TourGuide(
            name="Dona Lúcia Cavalcanti",
            bio="70 anos de Olinda na bagagem. Contadora de histórias, benzedeira e guardiã da memória do frevo e maracatu.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=lucia",
            rating=5.0,
            total_reviews=312,
            total_tours=800,
            languages=["Português"],
            specialties=["História", "Carnaval", "Tradições Populares"],
            hourly_rate=45.0,
            is_available=True,
            verified=True,
            whatsapp="+5581999990005",
            instagram="@donalucia.olinda",
            featured_places=["Casa dos Bonecos Gigantes", "Sede do Homem da Meia-Noite", "Ladeira da Misericórdia"],
            response_time_minutes=45,
        ),
        TourGuide(
            name="Felipe Albuquerque",
            bio="Guia de compras e artesanato local. Conheço todos os artesãos, ateliês de barro e lojas de renda renascença da região.",
            avatar_url="https://api.dicebear.com/9.x/personas/svg?seed=felipe",
            rating=4.6,
            total_reviews=67,
            total_tours=145,
            languages=["Português", "Espanhol"],
            specialties=["Compras", "Artesanato", "Economia Criativa"],
            hourly_rate=50.0,
            is_available=False,
            verified=False,
            whatsapp="+5581999990006",
            instagram="@felipe.artesanato",
            featured_places=["Mercado Eufrásio Barbosa", "Rua de São Bento", "Casa Estação da Luz"],
            response_time_minutes=30,
        ),
    ]

    for g in mock_guides:
        db.add(g)
    await db.commit()
    return {"message": f"Seeded {len(mock_guides)} guides"}
