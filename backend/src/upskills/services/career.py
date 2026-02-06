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
        career_db = await self._career_repository.get_by_id(career_id)
        if not career_db:
            return None
        return self._career_repository.to_domain(career_db, include_paths=True)

    async def get_all_careers(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Career], int]:
        careers_db = await self._career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self._career_repository.count()
        return [self._career_repository.to_domain(c) for c in careers_db], total

    async def create_career(self, career: Career) -> Career:
        career_db = await self._career_repository.create(career.model_dump(include={"name", "specialization"}))
        return self._career_repository.to_domain(career_db)

    async def update_career(self, career_id: int, career: Career) -> Career | None:
        career_db = await self._career_repository.get_by_id(career_id)
        if not career_db:
            return None

        update_data = career.model_dump(include={"name", "specialization"}, exclude_none=True)

        if update_data:
            updated_db = await self._career_repository.update(career_db, update_data)
            return self._career_repository.to_domain(updated_db)
        return self._career_repository.to_domain(career_db)

    async def delete_career(self, career_id: int) -> bool:
        career_db = await self._career_repository.get_by_id(career_id)
        if not career_db:
            return False
        await self._career_repository.delete(career_db)
        return True
