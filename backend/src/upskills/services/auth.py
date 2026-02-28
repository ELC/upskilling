from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.core import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from upskills.domain import AuthResult, Token, User
from upskills.repositories import RoleRepository, UserRepository


@dataclass
class AuthService:
    user_repository: UserRepository = Provide["user_repository"]
    role_repository: RoleRepository = Provide["role_repository"]

    async def register(self, user: User) -> AuthResult:
        existing = await self.user_repository.get_by_email(user.email)
        if existing:
            msg = "Email already registered"
            raise ValueError(msg)

        created_user = await self.user_repository.create(user)

        mentee_role = await self.role_repository.get_by_name("mentee")
        if mentee_role:
            await self.user_repository.assign_role(created_user, mentee_role)

        registered_user = await self.user_repository.get_by_id(created_user.user_id)
        if not registered_user:
            msg = "Failed to retrieve user after registration"
            raise RuntimeError(msg)
        tokens = self._create_tokens(created_user.user_id)

        return AuthResult(
            user=self.user_repository.to_domain(registered_user),
            tokens=tokens,
        )

    async def login(self, email: str, password: str) -> AuthResult:
        user = await self.user_repository.get_by_email(email)

        if not user:
            msg = "Invalid email or password"
            raise ValueError(msg)

        user_domain = self.user_repository.to_domain(user)
        if not user_domain.verify_password(password):
            msg = "Invalid email or password"
            raise ValueError(msg)
        tokens = self._create_tokens(user_domain.user_id)

        return AuthResult(
            user=self.user_repository.to_domain(user),
            tokens=tokens,
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        user_id_str = verify_token(refresh_token, "refresh")

        if user_id_str is None:
            msg = "Invalid or expired refresh token"
            raise ValueError(msg)

        user_id = int(user_id_str)
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            msg = "User not found"
            raise ValueError(msg)

        return self._create_tokens(user.user_id)

    async def request_password_reset(self, email: str) -> str | None:
        user = await self.user_repository.get_by_email(email)

        if not user:
            return None

        return await self.user_repository.create_password_reset_token(user.user_id)

    async def reset_password(self, token: str, new_password: str) -> bool:
        reset_token = await self.user_repository.get_password_reset_token(token)

        if not reset_token:
            msg = "Invalid or expired reset token"
            raise ValueError(msg)

        user = await self.user_repository.get_by_id(reset_token.user_id)
        if user:
            await self.user_repository.update(user, User(password=new_password))
            await self.user_repository.mark_token_used(reset_token)
            return True

        return False

    @staticmethod
    def _create_tokens(user_id: int) -> Token:
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
