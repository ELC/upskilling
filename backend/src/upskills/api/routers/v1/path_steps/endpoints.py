from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse
from upskills.domain import PathStep
from upskills.services import PathStepService

from .schemas import (
    PathStepCreate,
    PathStepResponse,
    PathStepUpdate,
    StepDependencyCreate,
)

router = APIRouter(prefix="/steps", tags=["Path Steps"])


@router.get("/templates/{path_id}/steps", dependencies=[Depends(get_optional_user)])
@inject
async def list_steps(
    path_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> list[PathStepResponse]:
    steps = await service.get_for_path(path_id)
    return [PathStepResponse.model_validate(s.model_dump()) for s in steps]


@router.post(
    "/templates/{path_id}/steps",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("path_content.add"))],
)
@inject
async def create_step(
    path_id: int,
    data: PathStepCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    step_data = data.model_dump()
    step_data["path_template"]["path_template_id"] = path_id
    step = PathStep.model_validate(step_data)
    result = await service.create(step)
    return PathStepResponse.model_validate(result.model_dump())


@router.get("/{step_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    try:
        result = await service.get(step_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return PathStepResponse.model_validate(result.model_dump())


@router.put("/{step_id}", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def update_step(
    step_id: int,
    data: PathStepUpdate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    step_data = data.model_dump(exclude_unset=True)
    step = PathStep.model_validate(step_data)
    step.step_id = step_id
    try:
        result = await service.update(step)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return PathStepResponse.model_validate(result.model_dump())


@router.delete("/{step_id}", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def delete_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    try:
        await service.delete(step_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return MessageResponse(message="Step deleted successfully.")


@router.post("/{step_id}/dependencies", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def add_step_dependency(
    step_id: int,
    data: StepDependencyCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    try:
        await service.add_dependency(step_id, data.depends_on_step_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return MessageResponse(message="Dependency added successfully.")


@router.delete(
    "/{step_id}/dependencies/{depends_on_step_id}", dependencies=[Depends(require_permissions("path_content.add"))]
)
@inject
async def remove_step_dependency(
    step_id: int,
    depends_on_step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    try:
        await service.remove_dependency(step_id, depends_on_step_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return MessageResponse(message="Dependency removed successfully.")
