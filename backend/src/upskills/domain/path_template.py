from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import DomainModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .career import Career
    from .path_step import PathStep

if False:
    pass


class PathTemplate(DomainModel):
    path_template_id: int
    career: Career | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None
    steps: Sequence[PathStep] = Field(default_factory=list)
