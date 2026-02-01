from dependency_injector.wiring import Provide, inject

from upskills.domain import PathTemplate
from upskills.repositories import CareerRepository, PathTemplateRepository


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
        return await self._path_template_repository.get_by_id_with_steps(path_template_id)

    async def get_all_paths(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplate], int]:
        if career_id:
            paths = await self._path_template_repository.get_by_career(career_id)
            return paths, len(paths)

        paths = await self._path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._path_template_repository.count()
        return paths, total

    async def create_path(self, data: PathTemplate) -> PathTemplate:
        career = await self._career_repository.get_by_id_with_paths(data.career_id)
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        db_model = await self._path_template_repository.create(data)
        return self._path_template_repository.to_domain(db_model)

    async def update_path(self, path_template_id: int, data: PathTemplate) -> PathTemplate | None:
        db_model = await self._path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not db_model:
            return None
        updated = await self._path_template_repository.update(db_model, data)
        return self._path_template_repository.to_domain(updated)

    async def delete_path(self, path_template_id: int) -> bool:
        db_model = await self._path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not db_model:
            return False
        await self._path_template_repository.delete(db_model)
        return True
