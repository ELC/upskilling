from datetime import date
from enum import StrEnum

from .base import DomainModel


class LogEntryType(StrEnum):
    MEETING = "Meeting/Conversation"
    PATH_APPROVED = "Path Approved"
    PATH_REJECTED = "Path Rejected"
    FINAL_PROJECT = "Final Project"
    GENERAL = "General"


class LogEntry(DomainModel):
    log_entry_id: int | None = None
    user_id: int | None = None
    user_career_path_id: int | None = None
    entry_type: str | None = None
    entry_date: date | None = None
    notes: str | None = None
    related_user_path_assignment_id: int | None = None
    user_name: str | None = None
    path_name: str | None = None
