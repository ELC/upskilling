from pydantic import Field

from .base import DomainModel
from .user import User


class TeamMember(DomainModel):
    user_id: int
    full_name: str
    email: str


class TeamListItem(DomainModel):
    team_id: int
    name: str
    member_count: int
    manager_name: str


class Team(DomainModel):
    team_id: int | None = None
    name: str | None = None
    manager_user_id: int | None = None
    manager: User | None = None
    members: list[TeamMember] = Field(default_factory=list)
