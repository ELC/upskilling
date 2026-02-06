from dependency_injector.wiring import Provide, inject

from upskills.core import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from upskills.domain import AuthResult, RoleInfo, Token, User
from upskills.repositories import RoleRepository, UserRepository
from upskills.repositories import User as UserModel


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

        user = await self._user_repository.get_by_id(db_model.user_id)
        if not user:
            msg = "Failed to retrieve user after registration"
            raise RuntimeError(msg)
        tokens = self._create_tokens(db_model.user_id)

        return AuthResult(
            user=self._user_model_to_domain(user),
            tokens=tokens,
        )

    async def login(self, email: str, password: str) -> AuthResult:
        user = await self._user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            msg = "Invalid email or password"
            raise ValueError(msg)

        tokens = self._create_tokens(user.user_id)

        return AuthResult(
            user=self._user_model_to_domain(user),
            tokens=tokens,
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        user_id_str = verify_token(refresh_token, "refresh")

        if user_id_str is None:
            msg = "Invalid or expired refresh token"
            raise ValueError(msg)

        user_id = int(user_id_str)
        user = await self._user_repository.get_by_id(user_id, id_column="user_id")

        if not user:
            msg = "User not found"
            raise ValueError(msg)

        return self._create_tokens(user.user_id)

    async def request_password_reset(self, email: str) -> str | None:
        user = await self._user_repository.get_by_email(email)

        if not user:
            return None

        return await self._user_repository.create_password_reset_token(user.user_id)

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

    @staticmethod
    def _user_model_to_domain(user: UserModel) -> User:
        roles: list[RoleInfo] = []
        if user.roles:
            roles = [
                RoleInfo(
                    role_id=user_role.role.role_id,
                    name=user_role.role.name,
                    description=user_role.role.description,
                    max_active_paths=user_role.role.max_active_paths,
                )
                for user_role in user.roles
                if user_role.role
            ]
        return User(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            bio=user.bio,
            created_at=user.created_at,
            roles=roles,
        )
