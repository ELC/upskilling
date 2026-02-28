from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse, PaginatedResponse
from upskills.domain import PathTemplate
from upskills.services import PathTemplateService

from .schemas import PathTemplateCreate, PathTemplateResponse, PathTemplateUpdate, PathTemplateWithStepsResponse

router = APIRouter(prefix="/paths", tags=["Path Templates"])


@router.get("", dependencies=[Depends(get_optional_user)])
@inject
async def list_paths(
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    career_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[PathTemplateResponse]:
    skip = (page - 1) * page_size

    paths, total = await service.get_all(skip=skip, limit=page_size, career_id=career_id)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    items = [PathTemplateResponse.model_validate(p.model_dump()) for p in paths]

    return PaginatedResponse[PathTemplateResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("path_template.create"))]
)
@inject
async def create_path(
    data: PathTemplateCreate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateResponse:
    path = PathTemplate.model_validate(data.model_dump())
    result = await service.create(path)
    return PathTemplateResponse.model_validate(result.model_dump())


@router.get("/{path_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateWithStepsResponse:
    try:
        result = await service.get(path_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return PathTemplateWithStepsResponse.model_validate(result.model_dump())


@router.put("/{path_id}", dependencies=[Depends(require_permissions("path_template.update"))])
@inject
async def update_path(
    path_id: int,
    data: PathTemplateUpdate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateResponse:
    template_data = data.model_dump(exclude_unset=True)
    template = PathTemplate.model_validate(template_data)
    template.path_template_id = path_id
    try:
        result = await service.update(template)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return PathTemplateResponse.model_validate(result.model_dump())


@router.delete("/{path_id}", dependencies=[Depends(require_permissions("path_template.update"))])
@inject
async def delete_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> MessageResponse:
    try:
        await service.delete(path_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return MessageResponse(message="Path template deleted successfully.")
