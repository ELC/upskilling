"""Logbook service."""

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from upskills.models.db.progress import LogEntry
from upskills.models.domain.progress import (
    LogEntryCreateInput,
    LogEntryDetailResponse,
    LogEntryResponse,
)
from upskills.repositories.progress import LogEntryRepository, UserCareerPathRepository


class LogbookService:
    """Service for logbook operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._log_repo = LogEntryRepository(session)
        self._career_path_repo = UserCareerPathRepository(session)

    async def get_entries_for_career_path(
        self,
        user_career_path_id: int,
        entry_type: str | None = None,
    ) -> list[LogEntryDetailResponse]:
        """Get log entries for a career path."""
        entries = await self._log_repo.get_by_career_path(user_career_path_id, entry_type)
        return [self._entry_to_detail_response(e) for e in entries]

    async def get_entry(self, log_entry_id: int) -> LogEntryDetailResponse | None:
        """Get a specific log entry."""
        entry = await self._log_repo.get_by_id(log_entry_id)
        if not entry:
            return None
        return self._entry_to_detail_response(entry)

    async def create_entry(
        self,
        data: LogEntryCreateInput,
    ) -> LogEntryResponse:
        """Create a new log entry."""
        # Verify career path exists
        career_path = await self._career_path_repo.get_by_id(data.user_career_path_id)
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        entry = await self._log_repo.create(data.model_dump())

        return self._entry_to_response(entry)

    async def update_entry(
        self,
        log_entry_id: int,
        entry_type: str | None = None,
        entry_date: date | None = None,
        notes: str | None = None,
    ) -> LogEntryResponse | None:
        """Update a log entry."""
        entry = await self._log_repo.get_by_id(log_entry_id)
        if not entry:
            return None

        update_data: dict[str, Any] = {}
        if entry_type is not None:
            update_data["entry_type"] = entry_type
        if entry_date is not None:
            update_data["entry_date"] = entry_date
        if notes is not None:
            update_data["notes"] = notes

        if update_data:
            entry = await self._log_repo.update(entry, update_data)

        return self._entry_to_response(entry)

    async def delete_entry(self, log_entry_id: int) -> bool:
        """Delete a log entry."""
        entry = await self._log_repo.get_by_id(log_entry_id)
        if not entry:
            return False

        await self._log_repo.delete(entry)
        return True

    @staticmethod
    def _entry_to_response(entry: LogEntry) -> LogEntryResponse:
        """Convert LogEntry to response."""
        return LogEntryResponse(
            log_entry_id=entry.log_entry_id,
            user_id=entry.user_id,
            user_career_path_id=entry.user_career_path_id,
            entry_type=entry.entry_type,
            entry_date=entry.entry_date,
            notes=entry.notes,
            related_user_path_assignment_id=entry.related_user_path_assignment_id,
        )

    @staticmethod
    def _entry_to_detail_response(entry: LogEntry) -> LogEntryDetailResponse:
        """Convert LogEntry to detailed response."""
        path_name = None
        if entry.related_path_assignment and entry.related_path_assignment.path_template:
            path_name = entry.related_path_assignment.path_template.name

        return LogEntryDetailResponse(
            log_entry_id=entry.log_entry_id,
            user_id=entry.user_id,
            user_career_path_id=entry.user_career_path_id,
            entry_type=entry.entry_type,
            entry_date=entry.entry_date,
            notes=entry.notes,
            related_user_path_assignment_id=entry.related_user_path_assignment_id,
            user_name=entry.user.full_name if entry.user else "Unknown",
            path_name=path_name,
        )
