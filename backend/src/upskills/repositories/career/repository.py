from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import Career as CareerDomain
from upskills.repositories.base import BaseRepository

from .models import Career


class CareerRepository(BaseRepository[Career]):
    async def get_by_id_with_paths(self, career_id: int) -> CareerDomain | None:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).where(Career.career_id == career_id)
            result = await session.execute(stmt)
            career = result.scalar_one_or_none()
            return self.to_domain(career, include_paths=True) if career else None

    async def get_all_with_paths(self, *, skip: int = 0, limit: int = 100) -> list[CareerDomain]:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return [self.to_domain(c) for c in result.scalars().all()]

    @staticmethod
    def to_domain(career: Career, *, include_paths: bool = False) -> CareerDomain:
        career_dict = career.model_dump()
        if not include_paths:
            career_dict.pop("path_templates")
        return CareerDomain.model_validate(career_dict)
