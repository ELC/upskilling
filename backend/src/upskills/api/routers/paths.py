"""Paths router for path templates and steps."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, require_permissions
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
@inject
async def list_paths(
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    current_user: CurrentUser,
    career_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[PathTemplateResponse]:
    """List all path templates, optionally filtered by career."""
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
@inject
async def create_path(
    data: PathTemplateCreate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    _: Annotated[User, Depends(require_permissions("path_template.create"))],
) -> PathTemplateResponse:
    """Create a new path template (requires path_template.create permission)."""
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
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{path_id}")
@inject
async def get_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    current_user: CurrentUser,
) -> PathTemplateWithStepsResponse:
    """Get a specific path template with its steps."""
    result = await service.get_path(path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return result


@router.put("/{path_id}")
@inject
async def update_path(
    path_id: int,
    data: PathTemplateUpdate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    _: Annotated[User, Depends(require_permissions("path_template.update"))],
) -> PathTemplateResponse:
    """Update a path template (requires path_template.update permission)."""
    input_data = PathTemplateUpdateInput(
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        default_start_offset_days=data.default_start_offset_days,
        default_deadline_offset_days=data.default_deadline_offset_days,
    )
    result = await service.update_path(path_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return result


@router.delete("/{path_id}")
@inject
async def delete_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    _: Annotated[User, Depends(require_permissions("path_template.update"))],
) -> MessageResponse:
    """Delete a path template (requires path_template.update permission)."""
    success = await service.delete_path(path_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return MessageResponse(message="Path template deleted successfully.")


# === Steps ===


@router.get("/{path_id}/steps")
@inject
async def list_steps(
    path_id: int,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    current_user: CurrentUser,
) -> list[PathStepResponse]:
    """Get all steps for a path template."""
    return await step_service.get_steps_for_path(path_id)


@router.post("/{path_id}/steps", status_code=status.HTTP_201_CREATED)
@inject
async def create_step(
    path_id: int,
    data: PathStepCreate,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Create a new step (requires path_content.add permission)."""
    try:
        input_data = PathStepCreateInput(
            path_template_id=path_id,
            step_order=data.step_order,
            name=data.name,
            description=data.description,
            duration_hours=data.duration_hours,
            course_link=data.course_link,
        )
        result = await step_service.create_step(input_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/steps/{step_id}")
@inject
async def get_step(
    step_id: int,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    current_user: CurrentUser,
) -> PathStepResponse:
    """Get a specific step."""
    result = await step_service.get_step(step_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.put("/steps/{step_id}")
@inject
async def update_step(
    step_id: int,
    data: PathStepUpdate,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Update a step (requires path_content.add permission)."""
    input_data = PathStepUpdateInput(
        step_order=data.step_order,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        course_link=data.course_link,
    )
    result = await step_service.update_step(step_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.delete("/steps/{step_id}")
@inject
async def delete_step(
    step_id: int,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Delete a step (requires path_content.add permission)."""
    success = await step_service.delete_step(step_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return MessageResponse(message="Step deleted successfully.")


# === Step Dependencies ===


@router.post("/steps/{step_id}/dependencies")
@inject
async def add_step_dependency(
    step_id: int,
    data: StepDependencyCreate,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Add a dependency to a step (requires path_content.add permission)."""
    await step_service.add_dependency(step_id, data.depends_on_step_id)
    return MessageResponse(message="Dependency added successfully.")


@router.delete("/steps/{step_id}/dependencies/{depends_on_step_id}")
@inject
async def remove_step_dependency(
    step_id: int,
    depends_on_step_id: int,
    step_service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Remove a dependency from a step (requires path_content.add permission)."""
    await step_service.remove_dependency(step_id, depends_on_step_id)
    return MessageResponse(message="Dependency removed successfully.")
