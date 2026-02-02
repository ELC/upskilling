"""Path template domain models."""

from pydantic import Field

from .base import DomainModel
from .path_step import PathStepResponse


class PathTemplateCreate(DomainModel):
    """Request model for creating a path template."""

    career_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    duration_hours: int = Field(..., gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateUpdate(DomainModel):
    """Request model for updating a path template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateCreateInput(DomainModel):
    """Input model for creating a path template."""

    career_id: int
    name: str
    description: str
    duration_hours: int
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateUpdateInput(DomainModel):
    """Input model for updating a path template."""

    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateResponse(DomainModel):
    """Response model for a path template."""

    path_template_id: int
    career_id: int
    name: str
    description: str
    duration_hours: int
    default_start_offset_days: int | None
    default_deadline_offset_days: int | None


class PathTemplateWithStepsResponse(PathTemplateResponse):
    """Response model for a path template with its steps."""

    steps: list[PathStepResponse] = Field(default_factory=list)
