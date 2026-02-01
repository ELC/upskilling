from dependency_injector.wiring import Provide, inject

from upskills.core import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from upskills.domain import AuthResult, Token
from upskills.repositories import RoleRepository, UserRepository


class AuthService:
    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        role_repository: RoleRepository = Provide["role_repository"],
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository

    async def register(
        self,
        full_name: str,
        email: str,
        password: str,
        bio: str | None = None,
    ) -> AuthResult:
        existing = await self._user_repository.get_by_email(email)
        if existing:
            msg = "Email already registered"
            raise ValueError(msg)

        db_model = await self._user_repository.create({
            "full_name": full_name,
            "email": email,
            "password_hash": hash_password(password),
            "bio": bio,
        })

        mentee_role = await self._role_repository.get_by_name("mentee")
        if mentee_role:
            await self._user_repository.assign_role(db_model.user_id, mentee_role.role_id)

        user = await self._user_repository.get_by_id_with_roles(db_model.user_id)
        tokens = self._create_tokens(db_model.user_id)

        return AuthResult(user=user, tokens=tokens)

    async def login(self, email: str, password: str) -> AuthResult:
        db_model = await self._user_repository.get_by_email(email)

        if not db_model or not verify_password(password, db_model.password_hash):
            msg = "Invalid email or password"
            raise ValueError(msg)

        user = self._user_repository.to_domain(db_model)
        tokens = self._create_tokens(db_model.user_id)

        return AuthResult(user=user, tokens=tokens)

    async def refresh_tokens(self, refresh_token: str) -> Token:
        user_id_str = verify_token(refresh_token, "refresh")

        if user_id_str is None:
            msg = "Invalid or expired refresh token"
            raise ValueError(msg)

        user_id = int(user_id_str)
        db_model = await self._user_repository.get_by_id(user_id, id_column="user_id")

        if not db_model:
            msg = "User not found"
            raise ValueError(msg)

        return self._create_tokens(db_model.user_id)

    async def request_password_reset(self, email: str) -> str | None:
        db_model = await self._user_repository.get_by_email(email)

        if not db_model:
            return None

        return await self._user_repository.create_password_reset_token(db_model.user_id)

    async def reset_password(self, token: str, new_password: str) -> bool:
        reset_token = await self._user_repository.get_password_reset_token(token)

        if not reset_token:
            msg = "Invalid or expired reset token"
            raise ValueError(msg)

        db_model = await self._user_repository.get_by_id(reset_token.user_id, id_column="user_id")
        if db_model:
            await self._user_repository.update(db_model, {"password_hash": hash_password(new_password)})
            await self._user_repository.mark_token_used(reset_token)
            return True

        return False

    @staticmethod
    def _create_tokens(user_id: int) -> Token:
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
