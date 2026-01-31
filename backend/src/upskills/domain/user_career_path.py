"""User career path domain models."""

from datetime import date

from pydantic import Field

from .base import DomainModel
from .user_path_assignment import UserPathAssignmentResponse


class UserCareerPathCreate(DomainModel):
    """Request model for assigning a career path to a user."""

    user_id: int
    career_id: int
    start_date: date
    end_date: date


class UserCareerPathUpdate(DomainModel):
    """Request model for updating a user's career path."""

    start_date: date | None = None
    end_date: date | None = None


class UserCareerPathResponse(DomainModel):
    """Response model for a user's career path."""

    user_career_path_id: int
    user_id: int
    career_id: int
    start_date: date
    end_date: date
    overall_progress_percent: int


class UserCareerPathDetailResponse(UserCareerPathResponse):
    """Detailed response model for a user's career path."""

    career_name: str
    career_specialization: str | None
    path_assignments: list[UserPathAssignmentResponse] = Field(default_factory=list)
