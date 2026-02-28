from typing import Any, ClassVar, get_args

from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel
from sqlalchemy import exists as sql_exists
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from upskills.db import DatabaseProvider

from .mapper import BaseMapper
from .models import Base


class BaseRepository[ModelT: Base, DomainT: BaseModel, MapperT: BaseMapper]:
    _id_column: ClassVar[str] = "id"

    @inject
    def __init__(
        self,
        db_provider: DatabaseProvider = Provide["db_provider"],
    ) -> None:
        self._db_provider = db_provider

    @property
    def _model(self) -> type[ModelT]:
        return get_args(self.__class__.__orig_bases__[0])[0]  # type: ignore[attr-defined, return-value]

    @property
    def _mapper(self) -> type[MapperT]:
        return get_args(self.__class__.__orig_bases__[0])[2]  # type: ignore[attr-defined, return-value]

    async def get_by_id(self, id_value: int) -> ModelT | None:
        async with self._db_provider.session() as session:
            column = getattr(self._model, self._id_column)
            stmt = select(self._model).where(column == id_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[ModelT]:
        async with self._db_provider.session() as session:
            stmt = select(self._model)

            if order_by:
                column = getattr(self._model, order_by)
                stmt = stmt.order_by(column.desc() if descending else column)

            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count(self) -> int:
        async with self._db_provider.session() as session:
            stmt = select(count()).select_from(self._model)  # pylint: disable=no-member E1101
            result = await session.execute(stmt)
            return result.scalar() or 0

    async def create(self, data: DomainT) -> ModelT:
        async with self._db_provider.session() as session:
            instance = self._mapper.to_model(data)  # type: ignore[assignment]
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def update(
        self,
        instance: ModelT,
        data: DomainT,
    ) -> ModelT:
        async with self._db_provider.session() as session:
            instance = await session.merge(instance)
            self._mapper.update_model(instance, data)  # type: ignore[arg-type]
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def delete(self, instance: ModelT) -> None:
        async with self._db_provider.session() as session:
            instance = await session.merge(instance)
            await session.delete(instance)
            await session.flush()
            await session.commit()

    async def exists(self, **kwargs: Any) -> bool:
        async with self._db_provider.session() as session:
            conditions = [getattr(self._model, key) == value for key, value in kwargs.items()]
            stmt = select(sql_exists().where(*conditions))
            result = await session.execute(stmt)
            return result.scalar() or False
