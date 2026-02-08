from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import DomainModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .path_template import PathTemplate

if False:
    pass


class Career(DomainModel):
    career_id: int | None = None
    name: str | None = None
    specialization: str | None = None
    path_templates: Sequence[PathTemplate] = Field(default_factory=list)
