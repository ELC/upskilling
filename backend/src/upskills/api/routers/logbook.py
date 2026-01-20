"""Logbook router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse
from upskills.models.domain.progress import (
    LogEntryCreate,
    LogEntryDetailResponse,
    LogEntryResponse,
    LogEntryUpdate,
)
from upskills.services.logbook import LogbookService

router = APIRouter()


@router.get("/career-path/{career_path_id}", response_model=list[LogEntryDetailResponse])
async def get_logbook_entries(
    career_path_id: int,
    current_user: CurrentUser,
    session: DbSession,
    entry_type: str | None = None,
) -> list[LogEntryDetailResponse]:
    """Get logbook entries for a career path."""
    service = LogbookService(session)
    return await service.get_entries_for_career_path(career_path_id, entry_type)


@router.post("", response_model=LogEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_logbook_entry(
    data: LogEntryCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> LogEntryResponse:
    """Create a new logbook entry (requires logbook.create permission)."""
    service = LogbookService(session)

    try:
        result = await service.create_entry(
            user_id=data.user_id,
            user_career_path_id=data.user_career_path_id,
            entry_type=data.entry_type.value,
            entry_date=data.entry_date,
            notes=data.notes,
            related_user_path_assignment_id=data.related_user_path_assignment_id,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{log_entry_id}", response_model=LogEntryDetailResponse)
async def get_logbook_entry(
    log_entry_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> LogEntryDetailResponse:
    """Get a specific logbook entry."""
    service = LogbookService(session)
    result = await service.get_entry(log_entry_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return result


@router.put("/{log_entry_id}", response_model=LogEntryResponse)
async def update_logbook_entry(
    log_entry_id: int,
    data: LogEntryUpdate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> LogEntryResponse:
    """Update a logbook entry (requires logbook.create permission)."""
    service = LogbookService(session)
    result = await service.update_entry(
        log_entry_id,
        entry_type=data.entry_type.value if data.entry_type else None,
        entry_date=data.entry_date,
        notes=data.notes,
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return result


@router.delete("/{log_entry_id}", response_model=MessageResponse)
async def delete_logbook_entry(
    log_entry_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> MessageResponse:
    """Delete a logbook entry (requires logbook.create permission)."""
    service = LogbookService(session)
    success = await service.delete_entry(log_entry_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return MessageResponse(message="Log entry deleted successfully.")
