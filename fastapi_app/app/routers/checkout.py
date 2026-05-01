import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.checkout import CheckoutRequest, CheckoutValidationResult, OrderConfirmation

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/validate", response_model=CheckoutValidationResult)
async def validate_cart(request: CheckoutRequest, current_user: CurrentUser = Depends(get_current_user)):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post("http://django:8000/api/v1/orders/validate/", json=request.model_dump())
    if resp.status_code == 400:
        return CheckoutValidationResult(valid=False, errors=[resp.text], subtotal=0, tax_amount=0, shipping_cost=0, total_amount=0, total_items=0)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Erreur validation Django")
    return CheckoutValidationResult(**resp.json())


@router.post("/confirm", response_model=OrderConfirmation)
async def confirm_order(request: CheckoutRequest, current_user: CurrentUser = Depends(get_current_user)):
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post("http://django:8000/api/v1/orders/create/", json=request.model_dump())
    if resp.status_code != 201:
        raise HTTPException(status_code=400, detail=resp.text)
    return OrderConfirmation(**resp.json())
