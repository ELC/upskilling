"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession

from upskills.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from upskills.models.db.user import User
from upskills.models.domain.auth import AuthResponse, TokenResponse
from upskills.models.domain.user import RoleResponse, UserResponse
from upskills.repositories.user import RoleRepository, UserRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)

    async def register(
        self,
        full_name: str,
        email: str,
        password: str,
        bio: str | None = None,
    ) -> AuthResponse:
        """Register a new user."""
        # Check if email already exists
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        # Create user
        user = await self._user_repo.create({
            "full_name": full_name,
            "email": email,
            "password_hash": hash_password(password),
            "bio": bio,
        })

        # Assign default role (mentee)
        mentee_role = await self._role_repo.get_by_name("mentee")
        if mentee_role:
            await self._user_repo.assign_role(user.user_id, mentee_role.role_id)
            # Refresh to get the role
            user = await self._user_repo.get_by_id(user.user_id)

        # Generate tokens
        tokens = self._create_tokens(user.user_id)

        return AuthResponse(
            user=self._user_to_response(user),
            tokens=tokens,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate a user and return tokens."""
        user = await self._user_repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        tokens = self._create_tokens(user.user_id)

        return AuthResponse(
            user=self._user_to_response(user),
            tokens=tokens,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access and refresh tokens."""
        user_id_str = verify_token(refresh_token, "refresh")

        if user_id_str is None:
            raise ValueError("Invalid or expired refresh token")

        user_id = int(user_id_str)
        user = await self._user_repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return self._create_tokens(user.user_id)

    async def request_password_reset(self, email: str) -> str | None:
        """Request a password reset token."""
        user = await self._user_repo.get_by_email(email)

        if not user:
            # Don't reveal whether email exists
            return None

        token = await self._user_repo.create_password_reset_token(user.user_id)
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using a reset token."""
        reset_token = await self._user_repo.get_password_reset_token(token)

        if not reset_token:
            raise ValueError("Invalid or expired reset token")

        # Update password
        user = await self._user_repo.get_by_id(reset_token.user_id)
        if user:
            await self._user_repo.update(user, {
                "password_hash": hash_password(new_password)
            })
            await self._user_repo.mark_token_used(reset_token)
            return True

        return False

    def _create_tokens(self, user_id: int) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

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
