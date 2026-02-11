"""User domain models."""

from datetime import datetime

from pydantic import EmailStr, Field

from .base import DomainModel
from .role import RoleResponse


class UserCreate(DomainModel):
    """Request model for creating a user."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    bio: str | None = None


class UserUpdate(DomainModel):
    """Request model for updating a user."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    bio: str | None = None


class PasswordChange(DomainModel):
    """Request model for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordReset(DomainModel):
    """Request model for password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetRequest(DomainModel):
    """Request model for requesting password reset."""

    email: EmailStr


class UserResponse(DomainModel):
    """Response model for a user."""

    user_id: int
    full_name: str
    email: str
    bio: str | None
    created_at: datetime
    roles: list[RoleResponse] = Field(default_factory=list)


class UserWithPermissions(UserResponse):
    """User response with full permission details."""

    permissions: list[str] = Field(default_factory=list)


class UserInDB(DomainModel):
    """Internal model for user with password hash."""

    user_id: int
    full_name: str
    email: str
    password_hash: str
    bio: str | None
    created_at: datetime
