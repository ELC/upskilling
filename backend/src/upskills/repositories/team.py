"""Team repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.team import Team, TeamMember
from upskills.models.db.user import User
from upskills.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """Repository for Team operations."""

    async def get_by_id(self, team_id: int, id_column: str = "team_id") -> Team | None:
        """Get team by ID with members loaded."""
        stmt = (
            select(Team)
            .options(
                selectinload(Team.manager),
                selectinload(Team.members).selectinload(TeamMember.user),
            )
            .where(Team.team_id == team_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_details(self, *, skip: int = 0, limit: int = 100) -> list[Team]:
        """Get all teams with manager and member details."""
        stmt = (
            select(Team)
            .options(
                selectinload(Team.manager),
                selectinload(Team.members).selectinload(TeamMember.user),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_teams_by_manager(self, manager_user_id: int) -> list[Team]:
        """Get all teams managed by a specific user."""
        stmt = (
            select(Team)
            .options(
                selectinload(Team.manager),
                selectinload(Team.members).selectinload(TeamMember.user),
            )
            .where(Team.manager_user_id == manager_user_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_teams_for_user(self, user_id: int) -> list[Team]:
        """Get all teams a user is a member of."""
        stmt = (
            select(Team)
            .join(TeamMember)
            .options(selectinload(Team.manager))
            .where(TeamMember.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_member(self, team_id: int, user_id: int) -> None:
        """Add a member to a team."""
        member = TeamMember(team_id=team_id, user_id=user_id)
        self._session.add(member)
        await self._session.flush()
        await self._session.commit()

    async def remove_member(self, team_id: int, user_id: int) -> None:
        """Remove a member from a team."""
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
        result = await self._session.execute(stmt)
        member = result.scalar_one_or_none()
        if member:
            await self._session.delete(member)
            await self._session.flush()
            await self._session.commit()

    async def is_member(self, team_id: int, user_id: int) -> bool:
        """Check if a user is a member of a team."""
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_team_members(self, team_id: int) -> list[User]:
        """Get all members of a team."""
        stmt = select(User).join(TeamMember).where(TeamMember.team_id == team_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
