from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from app.database import get_db
from app.schemas.product import ProductOut, ProductListResponse, ProductDetailResponse

router = APIRouter(prefix="/products", tags=["Catalogue"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncIOMotorDatabase = Depends(get_db),
    q: Optional[str] = Query(None, description="Recherche texte dans nom/SKU"),
    category_slug: Optional[str] = Query(None, description="Filtrer par catégorie"),
    is_active: bool = True,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Liste les produits avec filtres, recherche et pagination."""
    # Construire le filtre MongoDB
    filter_query = {"is_active": is_active}
    if q:
        filter_query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"sku": {"$regex": q, "$options": "i"}},
        ]
    if category_slug:
        filter_query["category.slug"] = category_slug

    # Pagination
    skip = (page - 1) * per_page

    # Exécuter la requête
    cursor = db["products"].find(filter_query).skip(skip).limit(per_page)
    products = await cursor.to_list(length=per_page)

    # Compter le total (sans pagination)
    total = await db["products"].count_documents(filter_query)

    # Convertir ObjectId → str pour JSON
    for p in products:
        p["_id"] = str(p["_id"])

    return ProductListResponse(
        products=[ProductOut.model_validate(p) for p in products],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{slug}", response_model=ProductDetailResponse)
async def get_product_by_slug(
    slug: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Récupère un produit par son slug (URL friendly)."""
    product = await db["products"].find_one({"slug": slug, "is_active": True})

    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Convertir ObjectId → str
    product["_id"] = str(product["_id"])

    return ProductDetailResponse(product=ProductOut.model_validate(product))
