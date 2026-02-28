from .base import DomainModel


class Role(DomainModel):
    role_id: int = 0
    name: str | None = None
    description: str | None = None
    max_active_paths: int | None = None


class Action(DomainModel):
    action_id: int = 0
    action_key: str | None = None
    description: str | None = None
