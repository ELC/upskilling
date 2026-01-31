"""Role and action domain models."""

from .base import DomainModel


class RoleResponse(DomainModel):
    """Response model for a role."""

    role_id: int
    name: str
    description: str | None
    max_active_paths: int | None


class ActionResponse(DomainModel):
    """Response model for an action/permission."""

    action_id: int
    action_key: str
    description: str
