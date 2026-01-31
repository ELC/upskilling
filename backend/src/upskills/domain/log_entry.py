"""Log entry domain models."""

from datetime import date

from pydantic import Field

from .base import DomainModel
from .enums import LogEntryType


class LogEntryCreate(DomainModel):
    """Request model for creating a log entry."""

    user_id: int
    user_career_path_id: int
    entry_type: LogEntryType
    entry_date: date
    notes: str = Field(..., min_length=1)
    related_user_path_assignment_id: int | None = None


class LogEntryUpdate(DomainModel):
    """Request model for updating a log entry."""

    entry_type: LogEntryType | None = None
    entry_date: date | None = None
    notes: str | None = Field(None, min_length=1)


class LogEntryCreateInput(DomainModel):
    """Input model for creating a log entry."""

    user_id: int
    user_career_path_id: int
    entry_type: str
    entry_date: date
    notes: str
    related_user_path_assignment_id: int | None = None


class LogEntryResponse(DomainModel):
    """Response model for a log entry."""

    log_entry_id: int
    user_id: int
    user_career_path_id: int
    entry_type: str
    entry_date: date
    notes: str
    related_user_path_assignment_id: int | None


class LogEntryDetailResponse(LogEntryResponse):
    """Detailed log entry response with related info."""

    user_name: str
    path_name: str | None = None
