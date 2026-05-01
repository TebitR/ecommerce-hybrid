from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
import os

# Client MongoDB global (lazy init)
_mongo_client: AsyncIOMotorClient | None = None
_mongo_db: AsyncIOMotorDatabase | None = None


def get_mongo_url() -> str:
    """Récupère l'URL MongoDB depuis les variables d'environnement."""
    return os.environ.get(
        "MONGODB_URL",
        "mongodb://admin:MongoPass123@mongodb:27017/ecommerce_catalog?authSource=admin",
    )


def get_db_name() -> str:
    """Récupère le nom de la base MongoDB."""
    return os.environ.get("MONGO_DB_NAME", "ecommerce_catalog")


@asynccontextmanager
async def lifespan(app):
    """Gestionnaire de cycle de vie : connexion/déconnexion MongoDB."""
    global _mongo_client, _mongo_db
    # Connexion au démarrage
    _mongo_client = AsyncIOMotorClient(get_mongo_url())
    _mongo_db = _mongo_client[get_db_name()]
    # Test de connexion
    await _mongo_db.command("ping")
    print(f"✅ MongoDB connecté : {get_db_name()}")
    yield
    # Déconnexion à l'arrêt
    if _mongo_client:
        _mongo_client.close()
        print("✅ MongoDB déconnecté")


def get_db() -> AsyncIOMotorDatabase:
    """Dépendance FastAPI pour injecter la DB dans les routes."""
    if _mongo_db is None:
        raise RuntimeError("MongoDB not initialized. Call lifespan first.")
    return _mongo_db
