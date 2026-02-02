from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import Career
from upskills.repositories import CareerRepository


@dataclass
class CareerService:
    career_repository: CareerRepository = Provide["career_repository"]

    async def get(self, career_id: int) -> Career | None:
        return await self.career_repository.get_by_id_with_paths(career_id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Career], int]:
        careers = await self.career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self.career_repository.count()
        return careers, total

    async def create(self, data: Career) -> Career:
        db_model = await self.career_repository.create(data)
        return self.career_repository.to_domain(db_model)

    async def update(self, career_id: int, data: Career) -> Career | None:
        db_model = await self.career_repository.get_by_id(career_id, id_column="career_id")
        if not db_model:
            return None
        updated = await self.career_repository.update(db_model, data)
        return self.career_repository.to_domain(updated)

    async def delete(self, career_id: int) -> bool:
        db_model = await self.career_repository.get_by_id(career_id, id_column="career_id")
        if not db_model:
            return False
        await self.career_repository.delete(db_model)
        return True
