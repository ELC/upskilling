"""User path assignment domain models."""

from datetime import date

from pydantic import Field

from .base import DomainModel
from .enums import ProgressStatus, ValidationStatus
from .path_template import PathTemplateResponse
from .user_step_progress import UserStepProgressResponse


class UserPathAssignmentCreate(DomainModel):
    """Request model for assigning a path to a user's career."""

    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date


class UserPathAssignmentUpdate(DomainModel):
    """Request model for updating a path assignment."""

    start_date: date | None = None
    deadline: date | None = None
    status: ProgressStatus | None = None
    mentor_validation_status: ValidationStatus | None = None


class UserPathAssignmentResponse(DomainModel):
    """Response model for a path assignment."""

    user_path_assignment_id: int
    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date
    status: str
    progress_percent: int
    mentor_validation_status: str


class UserPathAssignmentDetailResponse(UserPathAssignmentResponse):
    """Detailed response model for a path assignment with related data."""

    path_template: PathTemplateResponse | None = None
    step_progress: list[UserStepProgressResponse] = Field(default_factory=list)
