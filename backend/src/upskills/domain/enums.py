"""Enums for domain models."""

from enum import StrEnum


class ProgressStatus(StrEnum):
    """Status values for progress tracking."""

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ValidationStatus(StrEnum):
    """Mentor validation status values."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class LogEntryType(StrEnum):
    """Log entry type values."""

    MEETING = "Meeting/Conversation"
    PATH_APPROVED = "Path Approved"
    PATH_REJECTED = "Path Rejected"
    FINAL_PROJECT = "Final Project"
    GENERAL = "General"
