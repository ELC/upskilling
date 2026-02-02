"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from upskills.api import (
    auth_router,
    careers_router,
    logbook_router,
    path_steps_router,
    path_templates_router,
    progress_router,
    teams_router,
    users_router,
)
from upskills.core import get_settings
from upskills.db import DatabaseProvider
from upskills.injections import Container

@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,
    db_provider: DatabaseProvider = Provide["db_provider"],
) -> AsyncIterator[None]:
    await db_provider.init_db()
    yield
    await db_provider.close()


def app_factory() -> FastAPI:
    settings = get_settings()

    container = Container()
    container.config.from_pydantic(settings)
    container.wire(packages=["upskills"])

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(teams_router, prefix="/api/v1/teams", tags=["Teams"])
    app.include_router(careers_router, prefix="/api/v1/careers", tags=["Careers"])
    app.include_router(path_templates_router, prefix="/api/v1/paths", tags=["Path Templates"])
    app.include_router(path_steps_router, prefix="/api/v1/steps", tags=["Path Steps"])
    app.include_router(progress_router, prefix="/api/v1/progress", tags=["Progress"])
    app.include_router(logbook_router, prefix="/api/v1/logbook", tags=["Logbook"])

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app
