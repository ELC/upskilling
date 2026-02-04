from pydantic import Field

from upskills.api.schemas import BaseSchema

from upskills.api.routers.v1.path_steps.schemas import PathStepResponse


class PathTemplateCreate(BaseSchema):
    career_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    duration_hours: int = Field(..., gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateResponse(BaseSchema):
    path_template_id: int
    career_id: int
    name: str
    description: str
    duration_hours: int
    default_start_offset_days: int | None
    default_deadline_offset_days: int | None


class PathTemplateWithStepsResponse(PathTemplateResponse):
    steps: list[PathStepResponse] = Field(default_factory=list)
