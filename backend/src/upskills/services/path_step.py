from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import PathStep
from upskills.repositories import PathStepRepository, PathTemplateRepository


@dataclass
class PathStepService:
    path_step_repository: PathStepRepository = Provide["path_step_repository"]
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]

    async def get(self, step_id: int) -> PathStep:
        step = await self.path_step_repository.get_by_id(step_id)
        if not step:
            msg = "Step not found"
            raise ValueError(msg)
        return self.path_step_repository.to_domain(step)

    async def get_for_path(self, path_template_id: int) -> list[PathStep]:
        steps = await self.path_step_repository.get_by_path_template(path_template_id)
        return [self.path_step_repository.to_domain(s) for s in steps]

    async def create(self, path_step: PathStep) -> PathStep:
        if path_step.path_template and path_step.path_template.path_template_id:
            path = await self.path_template_repository.get_by_id(path_step.path_template.path_template_id)
            if not path:
                msg = "Path template not found"
                raise ValueError(msg)

        created_step = await self.path_step_repository.create(path_step)
        return self.path_step_repository.to_domain(created_step)

    async def update(self, path_step: PathStep) -> PathStep:
        existing_step = await self.path_step_repository.get_by_id(path_step.step_id)
        if not existing_step:
            msg = "Step not found"
            raise ValueError(msg)

        if path_step.path_template and path_step.path_template.path_template_id:
            path = await self.path_template_repository.get_by_id(path_step.path_template.path_template_id)
            if not path:
                msg = "Path template not found"
                raise ValueError(msg)

        updated_step = await self.path_step_repository.update(existing_step, path_step)
        return self.path_step_repository.to_domain(updated_step)

    async def delete(self, step_id: int) -> None:
        path_step = await self.path_step_repository.get_by_id(step_id)
        if not path_step:
            msg = "Step not found"
            raise ValueError(msg)
        await self.path_step_repository.delete(path_step)

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        step = await self.path_step_repository.get_by_id(step_id)
        if not step:
            msg = "Step not found"
            raise ValueError(msg)
        depends_on = await self.path_step_repository.get_by_id(depends_on_step_id)
        if not depends_on:
            msg = "Dependent step not found"
            raise ValueError(msg)
        await self.path_step_repository.add_dependency(step_id, depends_on_step_id)

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        step = await self.path_step_repository.get_by_id(step_id)
        if not step:
            msg = "Step not found"
            raise ValueError(msg)
        await self.path_step_repository.remove_dependency(step_id, depends_on_step_id)
