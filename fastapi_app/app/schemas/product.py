from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: str = Field(alias="_id")
    postgres_id: str
    sku: str
    name: str
    slug: Optional[str] = None
    category: Optional[CategoryOut] = None
    price_ht: Decimal
    tax_rate: Decimal
    price_ttc: Decimal
    stock_quantity: int
    stock_reserved: int
    stock_available: int
    is_active: bool
    attributes: dict = Field(default_factory=dict)
    image: Optional[str] = None
    images: list = Field(default_factory=list)
    rating: dict = Field(default_factory=lambda: {"average": 0.0, "count": 0})
    tags: list = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True  # Pour gérer l'alias _id → id

    @field_validator("price_ht", "price_ttc", "tax_rate", mode="before")
    @classmethod
    def convert_decimal(cls, v):
        """Convertit float/int en Decimal pour la précision financière."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class ProductListResponse(BaseModel):
    products: list[ProductOut]
    total: int
    page: int = 1
    per_page: int = 20


class ProductDetailResponse(BaseModel):
    product: ProductOut
