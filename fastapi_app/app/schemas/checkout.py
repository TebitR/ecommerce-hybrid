from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal


class CartItemInput(BaseModel):
    product_postgres_id: int
    quantity: int = Field(ge=1, le=100)


class CheckoutRequest(BaseModel):
    user_id: str
    items: List[CartItemInput]
    shipping_address_id: Optional[int] = None
    billing_address_id: Optional[int] = None


class CheckoutValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    stock_issues: List[dict] = []
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    total_amount: Decimal
    total_items: int


class OrderConfirmation(BaseModel):
    order_id: int
    order_number: str
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: str
