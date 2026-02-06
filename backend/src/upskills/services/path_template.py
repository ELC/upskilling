from dependency_injector.wiring import Provide, inject

from upskills.domain import PathTemplate
from upskills.repositories import CareerRepository, PathTemplateRepository

CREATE_FIELDS = {
    "career_id",
    "name",
    "description",
    "duration_hours",
    "default_start_offset_days",
    "default_deadline_offset_days",
}
UPDATE_FIELDS = {"name", "description", "duration_hours", "default_start_offset_days", "default_deadline_offset_days"}


class PathTemplateService:
    @inject
    def __init__(
        self,
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
        career_repository: CareerRepository = Provide["career_repository"],
    ) -> None:
        self._path_template_repository = path_template_repository
        self._career_repository = career_repository

    async def get_path(self, path_template_id: int) -> PathTemplate | None:
        path_db = await self._path_template_repository.get_by_id(path_template_id)
        if not path_db:
            return None
        return self._path_template_repository.to_domain(path_db, include_steps=True)

    async def get_all_paths(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplate], int]:
        if career_id:
            paths = await self._path_template_repository.get_by_career(career_id)
            return paths, len(paths)

        paths = await self._path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._path_template_repository.count()
        return paths, total

    async def create_path(self, path: PathTemplate) -> PathTemplate:
        if path.career_id is None:
            msg = "Career ID is required"
            raise ValueError(msg)

        career = await self._career_repository.get_by_id(path.career_id)
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        db_model = await self._path_template_repository.create(path.model_dump(include=CREATE_FIELDS))
        return self._path_template_repository.to_domain(db_model)

    async def update_path(self, path_template_id: int, path: PathTemplate) -> PathTemplate | None:
        path_db = await self._path_template_repository.get_by_id(path_template_id)
        if not path_db:
            return None

        update_data = path.model_dump(include=UPDATE_FIELDS, exclude_none=True)

        if update_data:
            updated = await self._path_template_repository.update(path_db, update_data)
            return self._path_template_repository.to_domain(updated)
        return self._path_template_repository.to_domain(path_db)

    async def delete_path(self, path_template_id: int) -> bool:
        path_db = await self._path_template_repository.get_by_id(path_template_id)
        if not path_db:
            return False
        await self._path_template_repository.delete(path_db)
        return True
