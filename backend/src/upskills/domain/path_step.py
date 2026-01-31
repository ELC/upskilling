"""Path step domain models."""

from pydantic import Field

from .base import DomainModel


class PathStepCreate(DomainModel):
    """Request model for creating a path step."""

    path_template_id: int
    step_order: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class PathStepUpdate(DomainModel):
    """Request model for updating a path step."""

    step_order: int | None = Field(None, ge=1)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class PathStepCreateInput(DomainModel):
    """Input model for creating a path step."""

    path_template_id: int
    step_order: int
    name: str
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None


class PathStepUpdateInput(DomainModel):
    """Input model for updating a path step."""

    step_order: int | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None


class StepDependencyCreate(DomainModel):
    """Request model for creating a step dependency."""

    step_id: int
    depends_on_step_id: int


class PathStepDependencyResponse(DomainModel):
    """Response model for a step dependency."""

    depends_on_step_id: int
    depends_on_step_name: str


class PathStepResponse(DomainModel):
    """Response model for a path step."""

    step_id: int
    path_template_id: int
    step_order: int
    name: str
    description: str | None
    duration_hours: int | None
    course_link: str | None
    dependencies: list[PathStepDependencyResponse] = Field(default_factory=list)
