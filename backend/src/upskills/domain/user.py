from datetime import datetime

from pydantic import Field

from .base import DomainModel
from .role import RoleResponse


class User(DomainModel):
    user_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    password_hash: str | None = None
    bio: str | None = None
    created_at: datetime | None = None
    roles: list[RoleResponse] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
