from upskills.domain import User
from upskills.repositories.base import BaseMapper

from .models import User as UserModel


class UserMapper(BaseMapper[User, UserModel]):
    _exclude_fields = frozenset({"user_id", "password", "roles", "permissions", "created_at"})
