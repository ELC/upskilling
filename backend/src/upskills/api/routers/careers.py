"""Careers router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.career import (
    CareerCreate,
    CareerResponse,
    CareerUpdate,
    CareerWithPathsResponse,
)
from upskills.services.career import CareerService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CareerResponse])
async def list_careers(
    session: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CareerResponse]:
    """List all careers."""
    service = CareerService(session)
    skip = (page - 1) * page_size

    careers, total = await service.get_all_careers(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=careers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=CareerResponse, status_code=status.HTTP_201_CREATED)
async def create_career(
    data: CareerCreate,
    session: DbSession,
    _: CurrentUser = Depends(require_permissions("career.create")),
) -> CareerResponse:
    """Create a new career (requires career.create permission)."""
    service = CareerService(session)
    result = await service.create_career(
        name=data.name,
        specialization=data.specialization,
    )
    await session.commit()
    return result


@router.get("/{career_id}", response_model=CareerWithPathsResponse)
async def get_career(
    career_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> CareerWithPathsResponse:
    """Get a specific career with its paths."""
    service = CareerService(session)
    result = await service.get_career(career_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return result


@router.put("/{career_id}", response_model=CareerResponse)
async def update_career(
    career_id: int,
    data: CareerUpdate,
    session: DbSession,
    _: CurrentUser = Depends(require_permissions("career.update")),
) -> CareerResponse:
    """Update a career (requires career.update permission)."""
    service = CareerService(session)
    result = await service.update_career(
        career_id,
        name=data.name,
        specialization=data.specialization,
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return result


@router.delete("/{career_id}", response_model=MessageResponse)
async def delete_career(
    career_id: int,
    session: DbSession,
    _: CurrentUser = Depends(require_permissions("career.update")),
) -> MessageResponse:
    """Delete a career (requires career.update permission)."""
    service = CareerService(session)
    success = await service.delete_career(career_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return MessageResponse(message="Career deleted successfully.")
