"""User service."""

from sqlalchemy.ext.asyncio import AsyncSession

from upskills.core.security import hash_password, verify_password
from upskills.models.db.user import User
from upskills.models.domain.user import RoleResponse, UserResponse, UserWithPermissions
from upskills.repositories.user import RoleRepository, UserRepository


class UserService:
    """Service for user operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)

    async def get_user(self, user_id: int) -> UserResponse | None:
        """Get a user by ID."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return None
        return self._user_to_response(user)

    async def get_user_with_permissions(self, user_id: int) -> UserWithPermissions | None:
        """Get a user with their permissions."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return None

        permissions = await self._user_repo.get_user_permissions(user_id)

        response = self._user_to_response(user)
        return UserWithPermissions(
            **response.model_dump(),
            permissions=permissions,
        )

    async def get_all_users(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[UserResponse], int]:
        """Get all users with pagination."""
        users = await self._user_repo.get_all_with_roles(skip=skip, limit=limit)
        total = await self._user_repo.count()
        return [self._user_to_response(u) for u in users], total

    async def update_user(
        self,
        user_id: int,
        full_name: str | None = None,
        email: str | None = None,
        bio: str | None = None,
    ) -> UserResponse | None:
        """Update a user's profile."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness if changing
        if email and email != user.email:
            existing = await self._user_repo.get_by_email(email)
            if existing:
                raise ValueError("Email already in use")

        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if email is not None:
            update_data["email"] = email
        if bio is not None:
            update_data["bio"] = bio

        if update_data:
            user = await self._user_repo.update(user, update_data)

        return self._user_to_response(user)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change a user's password."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        await self._user_repo.update(user, {
            "password_hash": hash_password(new_password)
        })
        return True

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return False

        await self._user_repo.delete(user)
        return True

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        """Assign a role to a user."""
        role = await self._role_repo.get_by_name(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found")

        await self._user_repo.assign_role(user_id, role.role_id)
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        """Remove a role from a user."""
        role = await self._role_repo.get_by_name(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found")

        await self._user_repo.remove_role(user_id, role.role_id)
        return True

    def _user_to_response(self, user: User) -> UserResponse:
        """Convert a User model to UserResponse."""
        roles = []
        if user.roles:
            for user_role in user.roles:
                if user_role.role:
                    roles.append(RoleResponse(
                        role_id=user_role.role.role_id,
                        name=user_role.role.name,
                        description=user_role.role.description,
                        max_active_paths=user_role.role.max_active_paths,
                    ))

        return UserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            bio=user.bio,
            created_at=user.created_at,
            roles=roles,
        )
