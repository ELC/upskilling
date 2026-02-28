from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import DomainModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .path_template import PathTemplate


class PathStep(DomainModel):
    step_id: int = 0
    path_template: PathTemplate | None = None
    step_order: int | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None
    dependencies: Sequence[PathStepDependency] = Field(default_factory=list)


class PathStepDependency(DomainModel):
    step: PathStep | None = None
