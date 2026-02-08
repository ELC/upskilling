from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import Career as CareerDomain
from upskills.domain import PathTemplate as PathTemplateDomain
from upskills.repositories.base import BaseRepository

from .models import Career


class CareerRepository(BaseRepository[Career]):
    async def get_by_id(self, id_value: int, id_column: str = "career_id") -> Career | None:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).where(Career.career_id == id_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all_with_paths(self, *, skip: int = 0, limit: int = 100) -> list[Career]:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    def to_domain(career: Career, *, include_paths: bool = False) -> CareerDomain:
        path_templates = []
        if include_paths and career.path_templates:
            path_templates = [PathTemplateDomain.model_validate(pt) for pt in career.path_templates]

        return CareerDomain(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
            path_templates=path_templates,
        )
