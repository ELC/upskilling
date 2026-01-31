"""User step progress domain models."""

from datetime import date, datetime

from pydantic import Field

from .base import DomainModel
from .enums import ProgressStatus
from .path_step import PathStepResponse


class UserStepProgressUpdate(DomainModel):
    """Request model for updating step progress."""

    status: ProgressStatus | None = None
    progress_percent: int | None = Field(None, ge=0, le=100)
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None


class StepProgressUpdateInput(DomainModel):
    """Input model for updating step progress."""

    status: str | None = None
    progress_percent: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None


class UserStepProgressResponse(DomainModel):
    """Response model for step progress."""

    user_step_progress_id: int
    user_path_assignment_id: int
    step_id: int
    status: str
    progress_percent: int
    planned_start_date: date | None
    planned_end_date: date | None
    actual_start_date: date | None
    actual_end_date: date | None
    updated_at: datetime
    step: PathStepResponse | None = None
