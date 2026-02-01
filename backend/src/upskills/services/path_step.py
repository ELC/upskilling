from dependency_injector.wiring import Provide, inject

from upskills.domain import PathStep
from upskills.repositories import PathStepRepository, PathTemplateRepository


class PathStepService:
    @inject
    def __init__(
        self,
        path_step_repository: PathStepRepository = Provide["path_step_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._path_step_repository = path_step_repository
        self._path_template_repository = path_template_repository

    async def get_step(self, step_id: int) -> PathStep | None:
        return await self._path_step_repository.get_by_id_with_deps(step_id)

    async def get_steps_for_path(self, path_template_id: int) -> list[PathStep]:
        return await self._path_step_repository.get_by_path_template(path_template_id)

    async def create_step(self, data: PathStep) -> PathStep:
        path = await self._path_template_repository.get_by_id(data.path_template_id, id_column="path_template_id")
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        db_model = await self._path_step_repository.create(data)
        return self._path_step_repository.to_domain(db_model)

    async def update_step(self, step_id: int, data: PathStep) -> PathStep | None:
        db_model = await self._path_step_repository.get_by_id(step_id, id_column="step_id")
        if not db_model:
            return None
        updated = await self._path_step_repository.update(db_model, data)
        return self._path_step_repository.to_domain(updated)

    async def delete_step(self, step_id: int) -> bool:
        db_model = await self._path_step_repository.get_by_id(step_id, id_column="step_id")
        if not db_model:
            return False
        await self._path_step_repository.delete(db_model)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self._path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self._path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True
