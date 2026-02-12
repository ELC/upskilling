from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import PathTemplate
from upskills.repositories import CareerRepository, PathTemplateRepository


@dataclass
class PathTemplateService:
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]
    career_repository: CareerRepository = Provide["career_repository"]

    async def get(self, path_template_id: int) -> PathTemplate | None:
        return await self.path_template_repository.get_by_id_with_steps(path_template_id)

    async def get_all(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplate], int]:
        if career_id:
            paths = await self.path_template_repository.get_by_career(career_id)
            return paths, len(paths)

        paths = await self.path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self.path_template_repository.count()
        return paths, total

    async def create(self, data: PathTemplate) -> PathTemplate:
        career = await self.career_repository.get_by_id_with_paths(data.career_id)
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        db_model = await self.path_template_repository.create(data)
        return self.path_template_repository.to_domain(db_model)

    async def update(self, path_template_id: int, data: PathTemplate) -> PathTemplate | None:
        db_model = await self.path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not db_model:
            return None
        updated = await self.path_template_repository.update(db_model, data)
        return self.path_template_repository.to_domain(updated)

    async def delete(self, path_template_id: int) -> bool:
        db_model = await self.path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not db_model:
            return False
        await self.path_template_repository.delete(db_model)
        return True
