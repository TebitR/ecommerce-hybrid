from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import lifespan
from app.config import get_settings, Settings
from app.routers import catalog, cart, search


# Factory d'application (pour tests + prod)
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="API haute performance pour le catalogue e-commerce",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS (développement)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Enregistrement des routers
    app.include_router(catalog.router, prefix="/api/v2")
    app.include_router(cart.router, prefix="/api/v2")
    app.include_router(search.router, prefix="/api/v2")

    # Healthcheck endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "fastapi-catalog"}

    return app


# Instance pour uvicorn
app = create_app()


# Point d'entrée direct (optionnel)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
