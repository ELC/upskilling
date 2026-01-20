"""Paths router for path templates and steps."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.career import (
    PathStepCreate,
    PathStepCreateInput,
    PathStepResponse,
    PathStepUpdate,
    PathStepUpdateInput,
    PathTemplateCreate,
    PathTemplateCreateInput,
    PathTemplateResponse,
    PathTemplateUpdate,
    PathTemplateUpdateInput,
    PathTemplateWithStepsResponse,
    StepDependencyCreate,
)
from upskills.services.career import PathStepService, PathTemplateService

router = APIRouter()


# === Path Templates ===


@router.get("")
async def list_paths(
    session: DbSession,
    current_user: CurrentUser,
    career_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[PathTemplateResponse]:
    """List all path templates, optionally filtered by career."""
    service = PathTemplateService(session)
    skip = (page - 1) * page_size

    paths, total = await service.get_all_paths(skip=skip, limit=page_size, career_id=career_id)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=paths,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_path(
    data: PathTemplateCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_template.create"))],
) -> PathTemplateResponse:
    """Create a new path template (requires path_template.create permission)."""
    service = PathTemplateService(session)

    try:
        input_data = PathTemplateCreateInput(
            career_id=data.career_id,
            name=data.name,
            description=data.description,
            duration_hours=data.duration_hours,
            default_start_offset_days=data.default_start_offset_days,
            default_deadline_offset_days=data.default_deadline_offset_days,
        )
        result = await service.create_path(input_data)
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{path_id}")
async def get_path(
    path_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> PathTemplateWithStepsResponse:
    """Get a specific path template with its steps."""
    service = PathTemplateService(session)
    result = await service.get_path(path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return result


@router.put("/{path_id}")
async def update_path(
    path_id: int,
    data: PathTemplateUpdate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_template.update"))],
) -> PathTemplateResponse:
    """Update a path template (requires path_template.update permission)."""
    service = PathTemplateService(session)
    input_data = PathTemplateUpdateInput(
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        default_start_offset_days=data.default_start_offset_days,
        default_deadline_offset_days=data.default_deadline_offset_days,
    )
    result = await service.update_path(path_id, input_data)
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return result


@router.delete("/{path_id}")
async def delete_path(
    path_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_template.update"))],
) -> MessageResponse:
    """Delete a path template (requires path_template.update permission)."""
    service = PathTemplateService(session)
    success = await service.delete_path(path_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return MessageResponse(message="Path template deleted successfully.")


# === Steps ===


@router.get("/{path_id}/steps")
async def list_steps(
    path_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> list[PathStepResponse]:
    """Get all steps for a path template."""
    service = PathStepService(session)
    return await service.get_steps_for_path(path_id)


@router.post("/{path_id}/steps", status_code=status.HTTP_201_CREATED)
async def create_step(
    path_id: int,
    data: PathStepCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Create a new step (requires path_content.add permission)."""
    service = PathStepService(session)

    try:
        input_data = PathStepCreateInput(
            path_template_id=path_id,
            step_order=data.step_order,
            name=data.name,
            description=data.description,
            duration_hours=data.duration_hours,
            course_link=data.course_link,
        )
        result = await service.create_step(input_data)
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/steps/{step_id}")
async def get_step(
    step_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> PathStepResponse:
    """Get a specific step."""
    service = PathStepService(session)
    result = await service.get_step(step_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.put("/steps/{step_id}")
async def update_step(
    step_id: int,
    data: PathStepUpdate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Update a step (requires path_content.add permission)."""
    service = PathStepService(session)
    input_data = PathStepUpdateInput(
        step_order=data.step_order,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        course_link=data.course_link,
    )
    result = await service.update_step(step_id, input_data)
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.delete("/steps/{step_id}")
async def delete_step(
    step_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Delete a step (requires path_content.add permission)."""
    service = PathStepService(session)
    success = await service.delete_step(step_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return MessageResponse(message="Step deleted successfully.")


# === Step Dependencies ===


@router.post("/steps/{step_id}/dependencies")
async def add_step_dependency(
    step_id: int,
    data: StepDependencyCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Add a dependency to a step (requires path_content.add permission)."""
    service = PathStepService(session)
    await service.add_dependency(step_id, data.depends_on_step_id)
    await session.commit()
    return MessageResponse(message="Dependency added successfully.")


@router.delete("/steps/{step_id}/dependencies/{depends_on_step_id}")
async def remove_step_dependency(
    step_id: int,
    depends_on_step_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Remove a dependency from a step (requires path_content.add permission)."""
    service = PathStepService(session)
    await service.remove_dependency(step_id, depends_on_step_id)
    await session.commit()
    return MessageResponse(message="Dependency removed successfully.")
