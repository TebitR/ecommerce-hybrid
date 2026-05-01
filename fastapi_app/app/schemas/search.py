from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class SearchQuery(BaseModel):
    """Paramètres de recherche validés par Pydantic."""
    q: Optional[str] = Field(None, description="Recherche texte dans nom/SKU/description")
    category_slug: Optional[str] = Field(None, description="Filtrer par catégorie")
    price_min: Optional[Decimal] = Field(None, ge=0, description="Prix minimum HT")
    price_max: Optional[Decimal] = Field(None, ge=0, description="Prix maximum HT")
    tags: Optional[List[str]] = Field(default=None, description="Filtrer par tags")
    is_active: bool = True
    sort_by: str = Field("relevance", pattern="^(relevance|price|rating|created_at)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

    @field_validator("q")
    @classmethod
    def sanitize_query(cls, v: Optional[str]) -> Optional[str]:
        """Nettoie la requête de recherche (prévention injection regex)."""
        if v:
            # Échapper les caractères spéciaux regex
            return v.replace(r"[-[\]{}()*+?.,\\^$|#\s]", r"\\\g<0>")
        return v


class SearchProductItem(BaseModel):
    """Produit dans les résultats de recherche."""
    id: str = Field(alias="_id")
    postgres_id: str
    sku: str
    name: str
    slug: Optional[str] = None
    category: Optional[dict] = None
    price_ht: Decimal
    price_ttc: Decimal
    stock_available: int
    is_active: bool
    rating: dict = Field(default_factory=lambda: {"average": 0.0, "count": 0})
    tags: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None  # Score de pertinence (si recherche texte)

    class Config:
        from_attributes = True
        populate_by_name = True


class SearchResponse(BaseModel):
    """Réponse paginée de recherche."""
    query: dict  # Requête appliquée (pour débogage)
    results: List[SearchProductItem]
    pagination: dict
    filters_applied: dict
    execution_time_ms: Optional[float] = None
