from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser

router = APIRouter(prefix="/cart", tags=["Panier"])


@router.get("/me")
async def get_user_cart(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Récupère le panier de l'utilisateur authentifié."""
    cart = await db["carts"].find_one({"user_id": current_user.user_id})

    if not cart:
        # Panier vide ou inexistant
        return {"user_id": current_user.user_id, "items": [], "total_ht": 0.0}

    # Convertir ObjectId pour JSON
    cart["_id"] = str(cart["_id"])
    return cart


@router.post("/clear")
async def clear_user_cart(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Supprime le panier de l'utilisateur (exige token valide)."""
    result = await db["carts"].delete_one({"user_id": current_user.user_id})

    if result.deleted_count == 0:
        return {"status": "already_empty", "user_id": current_user.user_id}

    return {"status": "cleared", "user_id": current_user.user_id}
