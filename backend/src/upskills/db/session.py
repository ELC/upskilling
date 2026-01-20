"""Database session utilities."""

from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from upskills.db.provider import DatabaseProvider


async def get_db_session(
    db_provider: DatabaseProvider,
) -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for getting a database session.

    This is typically wired through the DI container.

    Yields:
        An async database session.
    """
    session = await db_provider.get_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
