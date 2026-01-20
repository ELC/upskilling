"""Career and path template services."""

from sqlalchemy.ext.asyncio import AsyncSession

from upskills.models.db.career import Career, PathTemplate, PathTemplateStep
from upskills.models.domain.career import (
    CareerResponse,
    CareerWithPathsResponse,
    PathStepDependencyResponse,
    PathStepResponse,
    PathTemplateResponse,
    PathTemplateWithStepsResponse,
)
from upskills.repositories.career import (
    CareerRepository,
    PathStepRepository,
    PathTemplateRepository,
)


class CareerService:
    """Service for career operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._career_repo = CareerRepository(session)
        self._path_repo = PathTemplateRepository(session)

    async def get_career(self, career_id: int) -> CareerWithPathsResponse | None:
        """Get a career by ID with its paths."""
        career = await self._career_repo.get_by_id(career_id)
        if not career:
            return None
        return self._career_to_response_with_paths(career)

    async def get_all_careers(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[CareerResponse], int]:
        """Get all careers."""
        careers = await self._career_repo.get_all_with_paths(skip=skip, limit=limit)
        total = await self._career_repo.count()

        return [self._career_to_response(c) for c in careers], total

    async def create_career(
        self,
        name: str,
        specialization: str | None = None,
    ) -> CareerResponse:
        """Create a new career."""
        career = await self._career_repo.create({
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
        career = await self._career_repo.get_by_id(career_id)
        if not career:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if specialization is not None:
            update_data["specialization"] = specialization

        if update_data:
            career = await self._career_repo.update(career, update_data)

        return self._career_to_response(career)

    async def delete_career(self, career_id: int) -> bool:
        """Delete a career."""
        career = await self._career_repo.get_by_id(career_id)
        if not career:
            return False

        await self._career_repo.delete(career)
        return True

    def _career_to_response(self, career: Career) -> CareerResponse:
        """Convert Career to CareerResponse."""
        return CareerResponse(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
        )

    def _career_to_response_with_paths(self, career: Career) -> CareerWithPathsResponse:
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

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._path_repo = PathTemplateRepository(session)
        self._step_repo = PathStepRepository(session)
        self._career_repo = CareerRepository(session)

    async def get_path(self, path_template_id: int) -> PathTemplateWithStepsResponse | None:
        """Get a path template by ID with steps."""
        path = await self._path_repo.get_by_id(path_template_id)
        if not path:
            return None
        return self._path_to_response_with_steps(path)

    async def get_all_paths(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplateResponse], int]:
        """Get all path templates."""
        if career_id:
            paths = await self._path_repo.get_by_career(career_id)
            return [self._path_to_response(p) for p in paths], len(paths)

        paths = await self._path_repo.get_all_with_details(skip=skip, limit=limit)
        total = await self._path_repo.count()

        return [self._path_to_response(p) for p in paths], total

    async def create_path(
        self,
        career_id: int,
        name: str,
        description: str,
        duration_hours: int,
        default_start_offset_days: int | None = None,
        default_deadline_offset_days: int | None = None,
    ) -> PathTemplateResponse:
        """Create a new path template."""
        # Verify career exists
        career = await self._career_repo.get_by_id(career_id)
        if not career:
            raise ValueError("Career not found")

        path = await self._path_repo.create({
            "career_id": career_id,
            "name": name,
            "description": description,
            "duration_hours": duration_hours,
            "default_start_offset_days": default_start_offset_days,
            "default_deadline_offset_days": default_deadline_offset_days,
        })
        return self._path_to_response(path)

    async def update_path(
        self,
        path_template_id: int,
        name: str | None = None,
        description: str | None = None,
        duration_hours: int | None = None,
        default_start_offset_days: int | None = None,
        default_deadline_offset_days: int | None = None,
    ) -> PathTemplateResponse | None:
        """Update a path template."""
        path = await self._path_repo.get_by_id(path_template_id)
        if not path:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if duration_hours is not None:
            update_data["duration_hours"] = duration_hours
        if default_start_offset_days is not None:
            update_data["default_start_offset_days"] = default_start_offset_days
        if default_deadline_offset_days is not None:
            update_data["default_deadline_offset_days"] = default_deadline_offset_days

        if update_data:
            path = await self._path_repo.update(path, update_data)

        return self._path_to_response(path)

    async def delete_path(self, path_template_id: int) -> bool:
        """Delete a path template."""
        path = await self._path_repo.get_by_id(path_template_id)
        if not path:
            return False

        await self._path_repo.delete(path)
        return True

    def _path_to_response(self, path: PathTemplate) -> PathTemplateResponse:
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

    def _path_to_response_with_steps(
        self, path: PathTemplate
    ) -> PathTemplateWithStepsResponse:
        """Convert PathTemplate to PathTemplateWithStepsResponse."""
        steps = []
        if path.steps:
            for step in path.steps:
                deps = []
                if step.dependencies:
                    for dep in step.dependencies:
                        deps.append(PathStepDependencyResponse(
                            depends_on_step_id=dep.depends_on_step_id,
                            depends_on_step_name=dep.depends_on_step.name if dep.depends_on_step else "",
                        ))

                steps.append(PathStepResponse(
                    step_id=step.step_id,
                    path_template_id=step.path_template_id,
                    step_order=step.step_order,
                    name=step.name,
                    description=step.description,
                    duration_hours=step.duration_hours,
                    course_link=step.course_link,
                    dependencies=deps,
                ))

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

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._step_repo = PathStepRepository(session)
        self._path_repo = PathTemplateRepository(session)

    async def get_step(self, step_id: int) -> PathStepResponse | None:
        """Get a step by ID."""
        step = await self._step_repo.get_by_id(step_id)
        if not step:
            return None
        return self._step_to_response(step)

    async def get_steps_for_path(self, path_template_id: int) -> list[PathStepResponse]:
        """Get all steps for a path template."""
        steps = await self._step_repo.get_by_path_template(path_template_id)
        return [self._step_to_response(s) for s in steps]

    async def create_step(
        self,
        path_template_id: int,
        step_order: int,
        name: str,
        description: str | None = None,
        duration_hours: int | None = None,
        course_link: str | None = None,
    ) -> PathStepResponse:
        """Create a new step."""
        # Verify path exists
        path = await self._path_repo.get_by_id(path_template_id)
        if not path:
            raise ValueError("Path template not found")

        step = await self._step_repo.create({
            "path_template_id": path_template_id,
            "step_order": step_order,
            "name": name,
            "description": description,
            "duration_hours": duration_hours,
            "course_link": course_link,
        })
        return self._step_to_response(step)

    async def update_step(
        self,
        step_id: int,
        step_order: int | None = None,
        name: str | None = None,
        description: str | None = None,
        duration_hours: int | None = None,
        course_link: str | None = None,
    ) -> PathStepResponse | None:
        """Update a step."""
        step = await self._step_repo.get_by_id(step_id)
        if not step:
            return None

        update_data = {}
        if step_order is not None:
            update_data["step_order"] = step_order
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if duration_hours is not None:
            update_data["duration_hours"] = duration_hours
        if course_link is not None:
            update_data["course_link"] = course_link

        if update_data:
            step = await self._step_repo.update(step, update_data)

        return self._step_to_response(step)

    async def delete_step(self, step_id: int) -> bool:
        """Delete a step."""
        step = await self._step_repo.get_by_id(step_id)
        if not step:
            return False

        await self._step_repo.delete(step)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Add a dependency between steps."""
        await self._step_repo.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Remove a dependency between steps."""
        await self._step_repo.remove_dependency(step_id, depends_on_step_id)
        return True

    def _step_to_response(self, step: PathTemplateStep) -> PathStepResponse:
        """Convert PathTemplateStep to PathStepResponse."""
        deps = []
        if step.dependencies:
            for dep in step.dependencies:
                deps.append(PathStepDependencyResponse(
                    depends_on_step_id=dep.depends_on_step_id,
                    depends_on_step_name=dep.depends_on_step.name if dep.depends_on_step else "",
                ))

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
