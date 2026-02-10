"""User repository."""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.progress import UserCareerPath
from upskills.models.db.team import TeamMember
from upskills.models.db.user import Action, PasswordResetToken, Role, User, UserRole
from upskills.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    async def get_by_id(self, user_id: int, id_column: str = "user_id") -> User | None:
        """Get user by ID with roles loaded."""
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email with roles loaded."""
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.email == email)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_roles(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with their roles."""
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: int) -> list[str]:
        """Get all permission action keys for a user."""
        stmt = (
            select(Action.action_key)
            .join(Action.roles)
            .join(Role)
            .join(Role.users)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def assign_role(self, user_id: int, role_id: int) -> None:
        """Assign a role to a user."""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self._session.add(user_role)
        await self._session.flush()
        await self._session.commit()

    async def remove_role(self, user_id: int, role_id: int) -> None:
        """Remove a role from a user."""
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        result = await self._session.execute(stmt)
        user_role = result.scalar_one_or_none()
        if user_role:
            await self._session.delete(user_role)
            await self._session.flush()
            await self._session.commit()

    async def create_password_reset_token(self, user_id: int, expires_hours: int = 24) -> str:
        """Create a password reset token for a user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(hours=expires_hours)

        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self._session.add(reset_token)
        await self._session.flush()
        await self._session.commit()
        return token

    async def get_password_reset_token(self, token: str) -> PasswordResetToken | None:
        """Get a valid password reset token."""
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_token_used(self, token: PasswordResetToken) -> None:
        """Mark a password reset token as used."""
        token.used = True
        await self._session.flush()
        await self._session.commit()

    async def has_team_memberships(self, user_id: int) -> bool:
        """Check if a user is a member of any team."""
        stmt = select(TeamMember).where(TeamMember.user_id == user_id).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def has_career_paths(self, user_id: int) -> bool:
        """Check if a user has any assigned career paths."""
        stmt = select(UserCareerPath).where(UserCareerPath.user_id == user_id).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


class RoleRepository(BaseRepository[Role]):
    """Repository for Role operations."""

    async def get_by_id(self, role_id: int, id_column: str = "role_id") -> Role | None:
        return await super().get_by_id(role_id, "role_id")

    async def get_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        stmt = select(Role).where(Role.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
