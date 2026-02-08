from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import Career as CareerDomain
from upskills.domain import PathStep as PathStepDomain
from upskills.domain import PathStepDependency
from upskills.domain import PathTemplate as PathTemplateDomain
from upskills.repositories.base import BaseRepository

from .models import PathTemplate, PathTemplateStep


class PathTemplateRepository(BaseRepository[PathTemplate]):
    async def get_by_id(self, id_value: int, id_column: str = "path_template_id") -> PathTemplate | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(
                    selectinload(PathTemplate.career),
                    selectinload(PathTemplate.steps).selectinload(PathTemplateStep.dependencies),
                )
                .where(PathTemplate.path_template_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career(self, career_id: int) -> list[PathTemplateDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(selectinload(PathTemplate.steps))
                .where(PathTemplate.career_id == career_id)
                .order_by(PathTemplate.default_start_offset_days)
            )
            result = await session.execute(stmt)
            return [self.to_domain(p) for p in result.scalars().all()]

    async def get_all_with_details(self, *, skip: int = 0, limit: int = 100) -> list[PathTemplateDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(
                    selectinload(PathTemplate.career),
                    selectinload(PathTemplate.steps),
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return [self.to_domain(p) for p in result.scalars().all()]

    @staticmethod
    def to_domain(path: PathTemplate, *, include_steps: bool = False) -> PathTemplateDomain:
        steps: list[PathStepDomain] = []
        if include_steps and path.steps:
            for step in path.steps:
                deps: list[PathStepDependency] = []
                if step.dependencies:
                    deps = [
                        PathStepDependency(step=PathStepDomain.model_validate(dep.depends_on_step))
                        for dep in step.dependencies
                        if dep.depends_on_step
                    ]
                steps.append(PathStepDomain.model_validate(step).model_copy(update={"dependencies": deps}))

        career = CareerDomain.model_validate(path.career) if path.career else None

        return PathTemplateDomain(
            path_template_id=path.path_template_id,
            career=career,
            name=path.name,
            description=path.description,
            duration_hours=path.duration_hours,
            default_start_offset_days=path.default_start_offset_days,
            default_deadline_offset_days=path.default_deadline_offset_days,
            steps=steps,
        )
