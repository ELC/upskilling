"""Career and path template repositories."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from upskills.models.db.career import (
    Career,
    PathStepDependency,
    PathTemplate,
    PathTemplateStep,
)
from upskills.repositories.base import BaseRepository


class CareerRepository(BaseRepository[Career]):
    """Repository for Career operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Career)

    async def get_by_id(
        self, career_id: int, id_column: str = "career_id"
    ) -> Career | None:
        """Get career by ID with path templates."""
        stmt = (
            select(Career)
            .options(selectinload(Career.path_templates))
            .where(Career.career_id == career_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_paths(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[Career]:
        """Get all careers with their path templates."""
        stmt = (
            select(Career)
            .options(selectinload(Career.path_templates))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class PathTemplateRepository(BaseRepository[PathTemplate]):
    """Repository for PathTemplate operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PathTemplate)

    async def get_by_id(
        self, path_template_id: int, id_column: str = "path_template_id"
    ) -> PathTemplate | None:
        """Get path template by ID with steps."""
        stmt = (
            select(PathTemplate)
            .options(
                selectinload(PathTemplate.career),
                selectinload(PathTemplate.steps).selectinload(
                    PathTemplateStep.dependencies
                ),
            )
            .where(PathTemplate.path_template_id == path_template_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_career(self, career_id: int) -> list[PathTemplate]:
        """Get all path templates for a career."""
        stmt = (
            select(PathTemplate)
            .options(selectinload(PathTemplate.steps))
            .where(PathTemplate.career_id == career_id)
            .order_by(PathTemplate.default_start_offset_days)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_with_details(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[PathTemplate]:
        """Get all path templates with career and steps."""
        stmt = (
            select(PathTemplate)
            .options(
                selectinload(PathTemplate.career),
                selectinload(PathTemplate.steps),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class PathStepRepository(BaseRepository[PathTemplateStep]):
    """Repository for PathTemplateStep operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PathTemplateStep)

    async def get_by_id(
        self, step_id: int, id_column: str = "step_id"
    ) -> PathTemplateStep | None:
        """Get step by ID with dependencies."""
        stmt = (
            select(PathTemplateStep)
            .options(selectinload(PathTemplateStep.dependencies))
            .where(PathTemplateStep.step_id == step_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_path_template(
        self, path_template_id: int
    ) -> list[PathTemplateStep]:
        """Get all steps for a path template, ordered by step_order."""
        stmt = (
            select(PathTemplateStep)
            .options(selectinload(PathTemplateStep.dependencies))
            .where(PathTemplateStep.path_template_id == path_template_id)
            .order_by(PathTemplateStep.step_order)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        """Add a dependency between steps."""
        dep = PathStepDependency(step_id=step_id, depends_on_step_id=depends_on_step_id)
        self._session.add(dep)
        await self._session.flush()

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        """Remove a dependency between steps."""
        stmt = select(PathStepDependency).where(
            PathStepDependency.step_id == step_id,
            PathStepDependency.depends_on_step_id == depends_on_step_id,
        )
        result = await self._session.execute(stmt)
        dep = result.scalar_one_or_none()
        if dep:
            await self._session.delete(dep)
            await self._session.flush()
