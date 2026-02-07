from collections.abc import Sequence

from pydantic import Field

from .base import DomainModel
from .user import User


class Team(DomainModel):
    team_id: int
    name: str | None = None
    manager: User
    members: Sequence[User] = Field(default_factory=list)
