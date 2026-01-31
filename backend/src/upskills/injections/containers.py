from dependency_injector import containers, providers

from upskills.db.sqlite import SQLiteProvider


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_provider = providers.Singleton(
        SQLiteProvider,
        db_path=config.database_path,
    )
