from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import PathStep
from upskills.repositories import PathStepRepository, PathTemplateRepository


@dataclass
class PathStepService:
    path_step_repository: PathStepRepository = Provide["path_step_repository"]
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]

    async def get(self, step_id: int) -> PathStep | None:
        return await self.path_step_repository.get_by_id_with_deps(step_id)

    async def get_for_path(self, path_template_id: int) -> list[PathStep]:
        return await self.path_step_repository.get_by_path_template(path_template_id)

    async def create(self, data: PathStep) -> PathStep:
        path = await self.path_template_repository.get_by_id(data.path_template_id, id_column="path_template_id")
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        db_model = await self.path_step_repository.create(data)
        return self.path_step_repository.to_domain(db_model)

    async def update(self, step_id: int, data: PathStep) -> PathStep | None:
        db_model = await self.path_step_repository.get_by_id(step_id, id_column="step_id")
        if not db_model:
            return None
        updated = await self.path_step_repository.update(db_model, data)
        return self.path_step_repository.to_domain(updated)

    async def delete(self, step_id: int) -> bool:
        db_model = await self.path_step_repository.get_by_id(step_id, id_column="step_id")
        if not db_model:
            return False
        await self.path_step_repository.delete(db_model)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self.path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self.path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True
