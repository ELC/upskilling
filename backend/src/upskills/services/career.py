from dependency_injector.wiring import Provide, inject

from upskills.domain import Career
from upskills.repositories import CareerRepository


class CareerService:
    @inject
    def __init__(
        self,
        career_repository: CareerRepository = Provide["career_repository"],
    ) -> None:
        self._career_repository = career_repository

    async def get_career(self, career_id: int) -> Career | None:
        return await self._career_repository.get_by_id_with_paths(career_id)

    async def get_all_careers(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Career], int]:
        careers = await self._career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self._career_repository.count()
        return careers, total

    async def create_career(self, data: Career) -> Career:
        db_model = await self._career_repository.create(data)
        return self._career_repository.to_domain(db_model)

    async def update_career(self, career_id: int, data: Career) -> Career | None:
        db_model = await self._career_repository.get_by_id(career_id, id_column="career_id")
        if not db_model:
            return None
        updated = await self._career_repository.update(db_model, data)
        return self._career_repository.to_domain(updated)

    async def delete_career(self, career_id: int) -> bool:
        db_model = await self._career_repository.get_by_id(career_id, id_column="career_id")
        if not db_model:
            return False
        await self._career_repository.delete(db_model)
        return True
