from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.schemas import MessageResponse, PaginatedResponse
from upskills.core import CurrentUser, require_permissions
from upskills.domain import Career as CareerDomain
from upskills.repositories import User
from upskills.services import CareerService

from .schemas import CareerCreate, CareerResponse, CareerUpdate, CareerWithPathsResponse

router = APIRouter(prefix="/careers", tags=["Careers"])


@router.get("")
@inject
async def list_careers(
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[CareerResponse]:
    skip = (page - 1) * page_size

    careers, total = await service.get_all_careers(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    # Map domain objects to API schemas
    items = [CareerResponse.model_validate(c.model_dump()) for c in careers]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_career(
    data: CareerCreate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.create"))],
) -> CareerResponse:
    input_data = CareerDomain(
        name=data.name,
        specialization=data.specialization,
    )
    result = await service.create_career(input_data)
    return CareerResponse.model_validate(result.model_dump())


@router.get("/{career_id}")
@inject
async def get_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    current_user: CurrentUser,
) -> CareerWithPathsResponse:
    result = await service.get_career(career_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return CareerWithPathsResponse.model_validate(result.model_dump())


@router.put("/{career_id}")
@inject
async def update_career(
    career_id: int,
    data: CareerUpdate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.update"))],
) -> CareerResponse:
    input_data = CareerDomain(
        name=data.name,
        specialization=data.specialization,
    )
    result = await service.update_career(career_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return CareerResponse.model_validate(result.model_dump())


@router.delete("/{career_id}")
@inject
async def delete_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.update"))],
) -> MessageResponse:
    success = await service.delete_career(career_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return MessageResponse(message="Career deleted successfully.")
