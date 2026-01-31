"""Career and path template services."""

from typing import Any

from dependency_injector.wiring import Provide, inject

from upskills.models.db.career import Career, PathTemplate, PathTemplateStep
from upskills.models.domain.career import (
    CareerResponse,
    CareerWithPathsResponse,
    PathStepCreateInput,
    PathStepDependencyResponse,
    PathStepResponse,
    PathStepUpdateInput,
    PathTemplateCreateInput,
    PathTemplateResponse,
    PathTemplateUpdateInput,
    PathTemplateWithStepsResponse,
)
from upskills.repositories.career import (
    CareerRepository,
    PathStepRepository,
    PathTemplateRepository,
)


class CareerService:
    """Service for career operations."""

    @inject
    def __init__(
        self,
        career_repository: CareerRepository = Provide["career_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._career_repository = career_repository
        self._path_template_repository = path_template_repository

    async def get_career(self, career_id: int) -> CareerWithPathsResponse | None:
        """Get a career by ID with its paths."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return None
        return self._career_to_response_with_paths(career)

    async def get_all_careers(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[CareerResponse], int]:
        """Get all careers."""
        careers = await self._career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self._career_repository.count()

        return [self._career_to_response(c) for c in careers], total

    async def create_career(
        self,
        name: str,
        specialization: str | None = None,
    ) -> CareerResponse:
        """Create a new career."""
        career = await self._career_repository.create({
            "name": name,
            "specialization": specialization,
        })
        return self._career_to_response(career)

    async def update_career(
        self,
        career_id: int,
        name: str | None = None,
        specialization: str | None = None,
    ) -> CareerResponse | None:
        """Update a career."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return None

        update_data: dict[str, Any] = {}
        if name is not None:
            update_data["name"] = name
        if specialization is not None:
            update_data["specialization"] = specialization

        if update_data:
            career = await self._career_repository.update(career, update_data)

        return self._career_to_response(career)

    async def delete_career(self, career_id: int) -> bool:
        """Delete a career."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return False

        await self._career_repository.delete(career)
        return True

    @staticmethod
    def _career_to_response(career: Career) -> CareerResponse:
        """Convert Career to CareerResponse."""
        return CareerResponse(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
        )

    @staticmethod
    def _career_to_response_with_paths(career: Career) -> CareerWithPathsResponse:
        """Convert Career to CareerWithPathsResponse."""
        paths = []
        if career.path_templates:
            paths = [
                PathTemplateResponse(
                    path_template_id=p.path_template_id,
                    career_id=p.career_id,
                    name=p.name,
                    description=p.description,
                    duration_hours=p.duration_hours,
                    default_start_offset_days=p.default_start_offset_days,
                    default_deadline_offset_days=p.default_deadline_offset_days,
                )
                for p in career.path_templates
            ]

        return CareerWithPathsResponse(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
            path_templates=paths,
        )


class PathTemplateService:
    """Service for path template operations."""

    @inject
    def __init__(
        self,
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
        path_step_repository: PathStepRepository = Provide["path_step_repository"],
        career_repository: CareerRepository = Provide["career_repository"],
    ) -> None:
        self._path_template_repository = path_template_repository
        self._path_step_repository = path_step_repository
        self._career_repository = career_repository

    async def get_path(self, path_template_id: int) -> PathTemplateWithStepsResponse | None:
        """Get a path template by ID with steps."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return None
        return self._path_to_response_with_steps(path)

    async def get_all_paths(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplateResponse], int]:
        """Get all path templates."""
        if career_id:
            paths = await self._path_template_repository.get_by_career(career_id)
            return [self._path_to_response(p) for p in paths], len(paths)

        paths = await self._path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._path_template_repository.count()

        return [self._path_to_response(p) for p in paths], total

    async def create_path(
        self,
        data: PathTemplateCreateInput,
    ) -> PathTemplateResponse:
        """Create a new path template."""
        # Verify career exists
        career = await self._career_repository.get_by_id(data.career_id)
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        path = await self._path_template_repository.create(data.model_dump())
        return self._path_to_response(path)

    async def update_path(
        self,
        path_template_id: int,
        data: PathTemplateUpdateInput,
    ) -> PathTemplateResponse | None:
        """Update a path template."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            path = await self._path_template_repository.update(path, update_data)

        return self._path_to_response(path)

    async def delete_path(self, path_template_id: int) -> bool:
        """Delete a path template."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return False

        await self._path_template_repository.delete(path)
        return True

    @staticmethod
    def _path_to_response(path: PathTemplate) -> PathTemplateResponse:
        """Convert PathTemplate to PathTemplateResponse."""
        return PathTemplateResponse(
            path_template_id=path.path_template_id,
            career_id=path.career_id,
            name=path.name,
            description=path.description,
            duration_hours=path.duration_hours,
            default_start_offset_days=path.default_start_offset_days,
            default_deadline_offset_days=path.default_deadline_offset_days,
        )

    @staticmethod
    def _path_to_response_with_steps(path: PathTemplate) -> PathTemplateWithStepsResponse:
        """Convert PathTemplate to PathTemplateWithStepsResponse."""
        steps: list[PathStepResponse] = []
        if path.steps:
            for step in path.steps:
                deps: list[PathStepDependencyResponse] = []
                if step.dependencies:
                    deps.extend(
                        PathStepDependencyResponse(
                            depends_on_step_id=dep.depends_on_step_id,
                            depends_on_step_name=dep.depends_on_step.name
                            if dep.depends_on_step
                            else "",
                        )
                        for dep in step.dependencies
                    )

                steps.append(
                    PathStepResponse(
                        step_id=step.step_id,
                        path_template_id=step.path_template_id,
                        step_order=step.step_order,
                        name=step.name,
                        description=step.description,
                        duration_hours=step.duration_hours,
                        course_link=step.course_link,
                        dependencies=deps,
                    )
                )

        return PathTemplateWithStepsResponse(
            path_template_id=path.path_template_id,
            career_id=path.career_id,
            name=path.name,
            description=path.description,
            duration_hours=path.duration_hours,
            default_start_offset_days=path.default_start_offset_days,
            default_deadline_offset_days=path.default_deadline_offset_days,
            steps=steps,
        )


class PathStepService:
    """Service for path step operations."""

    @inject
    def __init__(
        self,
        path_step_repository: PathStepRepository = Provide["path_step_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._path_step_repository = path_step_repository
        self._path_template_repository = path_template_repository

    async def get_step(self, step_id: int) -> PathStepResponse | None:
        """Get a step by ID."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return None
        return self._step_to_response(step)

    async def get_steps_for_path(self, path_template_id: int) -> list[PathStepResponse]:
        """Get all steps for a path template."""
        steps = await self._path_step_repository.get_by_path_template(path_template_id)
        return [self._step_to_response(s) for s in steps]

    async def create_step(
        self,
        data: PathStepCreateInput,
    ) -> PathStepResponse:
        """Create a new step."""
        # Verify path exists
        path = await self._path_template_repository.get_by_id(data.path_template_id)
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        step = await self._path_step_repository.create(data.model_dump())
        return self._step_to_response(step)

    async def update_step(
        self,
        step_id: int,
        data: PathStepUpdateInput,
    ) -> PathStepResponse | None:
        """Update a step."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            step = await self._path_step_repository.update(step, update_data)

        return self._step_to_response(step)

    async def delete_step(self, step_id: int) -> bool:
        """Delete a step."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return False

        await self._path_step_repository.delete(step)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Add a dependency between steps."""
        await self._path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Remove a dependency between steps."""
        await self._path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True

    @staticmethod
    def _step_to_response(step: PathTemplateStep) -> PathStepResponse:
        """Convert PathTemplateStep to PathStepResponse."""
        deps: list[PathStepDependencyResponse] = []
        if step.dependencies:
            deps.extend(
                PathStepDependencyResponse(
                    depends_on_step_id=dep.depends_on_step_id,
                    depends_on_step_name=dep.depends_on_step.name if dep.depends_on_step else "",
                )
                for dep in step.dependencies
            )

        return PathStepResponse(
            step_id=step.step_id,
            path_template_id=step.path_template_id,
            step_order=step.step_order,
            name=step.name,
            description=step.description,
            duration_hours=step.duration_hours,
            course_link=step.course_link,
            dependencies=deps,
        )
