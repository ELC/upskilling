from sqlalchemy import select

from upskills.domain import Role as RoleDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user.models import Role

from .mapper import RoleMapper


class RoleRepository(BaseRepository[Role, RoleDomain, RoleMapper]):
    _id_column = "role_id"

    async def get_by_name(self, name: str) -> Role | None:
        async with self._db_provider.session() as session:
            stmt = select(Role).where(Role.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
