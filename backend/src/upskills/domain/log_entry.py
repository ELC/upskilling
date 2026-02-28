from datetime import date
from enum import StrEnum

from .base import DomainModel
from .progress import UserCareerPath, UserPathAssignment
from .user import User


class LogEntryType(StrEnum):
    MEETING = "Meeting/Conversation"
    PATH_APPROVED = "Path Approved"
    PATH_REJECTED = "Path Rejected"
    FINAL_PROJECT = "Final Project"
    GENERAL = "General"


class LogEntry(DomainModel):
    log_entry_id: int = 0
    user: User | None = None
    user_career_path: UserCareerPath | None = None
    entry_type: str | None = None
    entry_date: date | None = None
    notes: str | None = None
    related_path_assignment: UserPathAssignment | None = None
    user_name: str | None = None
    path_name: str | None = None
