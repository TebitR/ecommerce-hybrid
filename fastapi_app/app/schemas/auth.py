from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    is_staff: bool = False
    is_superuser: bool = False


class CurrentUser(TokenData):
    """Utilisateur extrait du JWT après validation."""

    pass
