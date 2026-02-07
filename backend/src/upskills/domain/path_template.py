from collections.abc import Sequence

from pydantic import Field

from .base import DomainModel
from .career import Career
from .path_step import PathStep


class PathTemplate(DomainModel):
    path_template_id: int
    career: Career | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None
    steps: Sequence[PathStep] = Field(default_factory=list)
