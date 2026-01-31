"""Career domain models."""

from pydantic import Field

from .base import DomainModel
from .path_template import PathTemplateResponse


class CareerCreate(DomainModel):
    """Request model for creating a career."""

    name: str = Field(..., min_length=1, max_length=255)
    specialization: str | None = None


class CareerUpdate(DomainModel):
    """Request model for updating a career."""

    name: str | None = Field(None, min_length=1, max_length=255)
    specialization: str | None = None


class CareerResponse(DomainModel):
    """Response model for a career."""

    career_id: int
    name: str
    specialization: str | None


class CareerWithPathsResponse(CareerResponse):
    """Response model for a career with its path templates."""

    path_templates: list[PathTemplateResponse] = Field(default_factory=list)
