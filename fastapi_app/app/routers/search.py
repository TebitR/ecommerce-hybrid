import time
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.schemas.search import SearchQuery, SearchResponse, SearchProductItem
from app.utils.aggregations import build_search_pipeline

router = APIRouter(prefix="/search", tags=["Recherche Avancée"])


@router.get("", response_model=SearchResponse)
async def search_products(
    search_params: SearchQuery = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Recherche avancée avec filtres, tri et pagination.
    Utilise les agrégations MongoDB pour des performances optimales.
    """
    start_time = time.time()

    # Construire le pipeline d'agrégation
    pipeline = build_search_pipeline(
        query=search_params.q,
        category_slug=search_params.category_slug,
        price_min=search_params.price_min,
        price_max=search_params.price_max,
        tags=search_params.tags,
        is_active=search_params.is_active,
        sort_by=search_params.sort_by,
        sort_order=search_params.sort_order,
        page=search_params.page,
        per_page=search_params.per_page
    )

    # Exécuter l'agrégation
    cursor = db["products"].aggregate(pipeline)
    agg_result = await cursor.to_list(length=1)

    if not agg_result:
        return SearchResponse(
            query=search_params.model_dump(),
            results=[],
            pagination={"total": 0, "page": 1, "per_page": search_params.per_page, "total_pages": 0},
            filters_applied={k: v for k, v in search_params.model_dump().items() if v is not None},
            execution_time_ms=0
        )

    result = agg_result[0]
    total = result.get("total", 0) or 0
    raw_products = result.get("results", [])

    # Convertir ObjectId → str pour JSON serialization
    for p in raw_products:
        if "_id" in p:
            p["_id"] = str(p["_id"])

    # Mapper vers le schéma Pydantic
    products = [SearchProductItem.model_validate(p) for p in raw_products]

    # Calculer le temps d'exécution
    execution_time_ms = round((time.time() - start_time) * 1000, 2)

    return SearchResponse(
        query=search_params.model_dump(),
        results=products,
        pagination={
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        },
        filters_applied={k: v for k, v in search_params.model_dump().items() if v is not None},
        execution_time_ms=execution_time_ms
    )
