from collections.abc import Sequence
from datetime import datetime

from pydantic import Field, model_validator

from upskills.core import hash_password, verify_password

from .base import DomainModel


class RoleInfo(DomainModel):
    role_id: int
    name: str
    description: str | None = None
    max_active_paths: int = 0


class User(DomainModel):
    user_id: int = 0
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    password_hash: str | None = None
    bio: str | None = None
    created_at: datetime | None = None
    roles: Sequence[RoleInfo] = Field(default_factory=list)
    permissions: Sequence[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _derive_password_hash(self) -> "User":
        if not self.password:
            return self
        self.password_hash = hash_password(self.password)
        self.password = None
        return self

    def verify_password(self, plain_password: str) -> bool:
        if not self.password_hash:
            return False
        return verify_password(plain_password, self.password_hash)
