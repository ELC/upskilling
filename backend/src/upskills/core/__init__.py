"""Core module - configuration, security, dependencies."""

from .config import Settings, get_settings
from .dependencies import (
    CurrentUser,
    OptionalUser,
    get_current_user,
    get_current_user_optional,
    require_permissions,
    security,
)
from .security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_token,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Dependencies
    "CurrentUser",
    "OptionalUser",
    "get_current_user",
    "get_current_user_optional",
    "require_permissions",
    "security",
    # Security
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
    "verify_token",
]
