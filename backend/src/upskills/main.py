"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from upskills.containers import Container
from upskills.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler."""
    # Startup
    container = app.state.container
    await container.db_provider().init_db()
    yield
    # Shutdown
    await container.db_provider().close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    container = Container()
    container.config.from_pydantic(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Store container in app state
    app.state.container = container

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from upskills.api.routers import (
        auth,
        careers,
        logbook,
        paths,
        progress,
        teams,
        users,
    )

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
    app.include_router(careers.router, prefix="/api/v1/careers", tags=["Careers"])
    app.include_router(paths.router, prefix="/api/v1/paths", tags=["Paths"])
    app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])
    app.include_router(logbook.router, prefix="/api/v1/logbook", tags=["Logbook"])

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()
