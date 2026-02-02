"""Role repository."""

from sqlalchemy import select

from upskills.models import Role

from .base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role operations."""

    async def get_by_id(self, role_id: int, id_column: str = "role_id") -> Role | None:
        return await super().get_by_id(role_id, "role_id")

    async def get_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        async with self._db_provider.session() as session:
            stmt = select(Role).where(Role.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
