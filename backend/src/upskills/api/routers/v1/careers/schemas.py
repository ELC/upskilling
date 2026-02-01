from pydantic import Field

from upskills.api.routers.v1.path_templates.schemas import PathTemplateResponse
from upskills.api.schemas import BaseSchema


class CareerCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    specialization: str | None = None


class CareerUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    specialization: str | None = None


class CareerResponse(BaseSchema):
    career_id: int
    name: str
    specialization: str | None


class CareerWithPathsResponse(CareerResponse):
    path_templates: list[PathTemplateResponse] = Field(default_factory=list)
