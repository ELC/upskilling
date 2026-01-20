"""Dependency injection container using dependency-injector."""

from dependency_injector import containers, providers

from upskills.core.config import Settings
from upskills.db.provider import DatabaseProvider
from upskills.db.sqlite import SQLiteProvider


class Container(containers.DeclarativeContainer):
    """Main DI container for the application."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "upskills.api.routers.auth",
            "upskills.api.routers.users",
            "upskills.api.routers.teams",
            "upskills.api.routers.careers",
            "upskills.api.routers.paths",
            "upskills.api.routers.progress",
            "upskills.api.routers.logbook",
            "upskills.core.security",
        ]
    )

    # Configuration
    config = providers.Configuration()

    # Database provider
    db_provider = providers.Singleton(
        SQLiteProvider,
        db_path=config.database_path,
    )

    # Repositories (factory - new instance per request)
    # These are created with a session, which is request-scoped

    # Services will be added here as we implement them
