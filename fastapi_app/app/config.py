from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://admin:MongoPass123@mongodb:27017/ecommerce_catalog?authSource=admin"
    mongo_db_name: str = "ecommerce_catalog"

    # JWT (pour validation des tokens Django)
    jwt_secret_key: str = "jwt-fallback"
    jwt_algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["*"]  # Dev uniquement

    # API Metadata
    api_title: str = "E-Commerce API v2"
    api_version: str = "2.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Singleton pour les settings (performance)."""
    return Settings()
