"""
Dépendances d'authentification JWT pour FastAPI.
Lecture DIRECTE des variables d'environnement (aucun cache).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from app.schemas.auth import CurrentUser

# Schéma Bearer standard
security = HTTPBearer()

# Lecture UNIQUE et DIRECTE des secrets au chargement du module
# Pas de fonction, pas de cache, pas de Pydantic Settings
_JWT_SECRET = os.environ.get("JWT_SECRET_KEY")
_JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Valide le token JWT signé par Django et retourne les claims utilisateur.
    Aucune requête base de données → 100% stateless.
    """
    token = credentials.credentials

    # Vérification minimale : token et secret présents
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _JWT_SECRET:
        # En dev, on log l'erreur pour débogage
        print("JWT_SECRET_KEY non définie dans l'environnement")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration serveur invalide",
        )

    try:
        # Décodage avec la clé lue DIRECTEMENT depuis os.environ
        payload = jwt.decode(
            token,
            _JWT_SECRET,  # Variable module, lue UNE fois au startup
            algorithms=[_JWT_ALGORITHM],
        )
    except JWTError as e:
        # Log l'erreur exacte pour débogage (à retirer en prod)
        print(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extraire les claims requis
    user_id = payload.get("user_id")
    username = payload.get("username")

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incomplet",
        )

    return CurrentUser(
        user_id=str(user_id),
        username=username,
        email=payload.get("email"),
        is_staff=payload.get("is_staff", False),
        is_superuser=payload.get("is_superuser", False),
    )


def require_staff(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dépendance qui exige is_staff=True."""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au personnel",
        )
    return current_user
