from dependency_injector.wiring import Provide, inject

from upskills.domain import PathStep
from upskills.repositories import PathStepRepository, PathTemplateRepository

CREATE_FIELDS = {"step_order", "name", "description", "duration_hours", "course_link"}
UPDATE_FIELDS = {"step_order", "name", "description", "duration_hours", "course_link"}


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
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return None
        return self._path_step_repository.to_domain(step)

    async def get_steps_for_path(self, path_template_id: int) -> list[PathStep]:
        steps = await self._path_step_repository.get_by_path_template(path_template_id)
        return [self._path_step_repository.to_domain(s) for s in steps]

    async def create_step(self, path_template_id: int, step: PathStep) -> PathStep:
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        create_data = step.model_dump(include=CREATE_FIELDS)
        create_data["path_template_id"] = path_template_id

        created = await self._path_step_repository.create(create_data)
        return self._path_step_repository.to_domain(created)

    async def update_step(self, step_id: int, step: PathStep) -> PathStep | None:
        step_db = await self._path_step_repository.get_by_id(step_id)
        if not step_db:
            return None

        update_data = step.model_dump(include=UPDATE_FIELDS, exclude_none=True)

        if update_data:
            step_db = await self._path_step_repository.update(step_db, update_data)

        return self._path_step_repository.to_domain(step_db)

    async def delete_step(self, step_id: int) -> bool:
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return False
        await self._path_step_repository.delete(step)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self._path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self._path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True
