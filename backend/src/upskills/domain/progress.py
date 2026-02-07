from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field

from .base import DomainModel

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date, datetime

    from .career import Career
    from .path_step import PathStep
    from .path_template import PathTemplate
    from .user import User


class ProgressStatus(StrEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ValidationStatus(StrEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class DashboardStats(DomainModel):
    current_career: str | None = None
    current_path: str | None = None
    current_path_progress: int = 0
    paths_remaining: int = 0
    overall_progress: int = 0
    skills_obtained: int = 0


class MenteeProgressSummary(DomainModel):
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


class UserPathAssignment(DomainModel):
    user_path_assignment_id: int
    user_career_path: UserCareerPath | None = None
    path_template: PathTemplate | None = None
    start_date: date | None = None
    deadline: date | None = None
    status: str | None = None
    progress_percent: int = 0
    mentor_validation_status: str | None = None
    step_progress: Sequence[UserStepProgress] = Field(default_factory=list)


class UserCareerPath(DomainModel):
    user_career_path_id: int
    user: User | None = None
    career: Career | None = None
    start_date: date | None = None
    end_date: date | None = None
    overall_progress_percent: int = 0
    career_name: str | None = None
    career_specialization: str | None = None
    path_assignments: Sequence[UserPathAssignment] = Field(default_factory=list)


class UserStepProgress(DomainModel):
    user_step_progress_id: int
    user_path_assignment: UserPathAssignment | None = None
    step: PathStep | None = None
    status: str | None = None
    progress_percent: int = 0
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    updated_at: datetime | None = None
