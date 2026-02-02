"""Dashboard domain models."""

from datetime import date

from .base import DomainModel


class MenteeProgressSummary(DomainModel):
    """Summary of a mentee's progress (for team management view)."""

    user_id: int
    full_name: str
    email: str
    career_name: str
    start_date: date
    end_date: date
    overall_progress_percent: int
    paths_completed: int
    paths_total: int
    pending_validation: int


class DashboardStats(DomainModel):
    """Dashboard statistics for a user."""

    current_career: str | None
    current_path: str | None
    current_path_progress: int
    paths_remaining: int
    overall_progress: int
    skills_obtained: int
