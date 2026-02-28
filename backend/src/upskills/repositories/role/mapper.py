from upskills.domain import Role
from upskills.repositories.base import BaseMapper
from upskills.repositories.user.models import Role as RoleModel


class RoleMapper(BaseMapper[Role, RoleModel]):
    _exclude_fields = frozenset({"role_id"})
