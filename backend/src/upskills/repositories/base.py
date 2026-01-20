"""Base repository with common CRUD operations."""

from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from upskills.models.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType: Base]:
    """Base repository providing common CRUD operations.

    This follows the Repository pattern to abstract data access logic.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        """Initialize the repository.

        Args:
            session: The database session.
            model: The SQLAlchemy model class.
        """
        self._session = session
        self._model = model

    async def get_by_id(self, id_value: int, id_column: str = "id") -> ModelType | None:
        """Get a single record by its primary key.

        Args:
            id_value: The primary key value.
            id_column: The name of the primary key column.

        Returns:
            The model instance or None if not found.
        """
        column = getattr(self._model, id_column)
        stmt = select(self._model).where(column == id_value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[ModelType]:
        """Get all records with optional pagination and ordering.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            order_by: Column name to order by.
            descending: Whether to sort in descending order.

        Returns:
            List of model instances.
        """
        stmt = select(self._model)

        if order_by:
            column = getattr(self._model, order_by)
            stmt = stmt.order_by(column.desc() if descending else column)

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Get the total count of records.

        Returns:
            The total number of records.
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self._model)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record.

        Args:
            data: Dictionary of column values.

        Returns:
            The created model instance.
        """
        instance = self._model(**data)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(
        self,
        instance: ModelType,
        data: dict[str, Any],
    ) -> ModelType:
        """Update an existing record.

        Args:
            instance: The model instance to update.
            data: Dictionary of column values to update.

        Returns:
            The updated model instance.
        """
        for key, value in data.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Delete a record.

        Args:
            instance: The model instance to delete.
        """
        await self._session.delete(instance)
        await self._session.flush()

    async def exists(self, **kwargs: Any) -> bool:
        """Check if a record exists with the given criteria.

        Args:
            **kwargs: Column-value pairs to filter by.

        Returns:
            True if a matching record exists.
        """
        from sqlalchemy import exists as sql_exists

        conditions = [getattr(self._model, key) == value for key, value in kwargs.items()]
        stmt = select(sql_exists().where(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar() or False
