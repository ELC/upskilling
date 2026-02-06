from dependency_injector.wiring import Provide, inject

from upskills.core import hash_password, verify_password
from upskills.domain import RoleInfo, User
from upskills.repositories import RoleRepository, UserRepository
from upskills.repositories import User as UserModel

UPDATE_FIELDS = {"full_name", "email", "bio"}


class UserService:
    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        role_repository: RoleRepository = Provide["role_repository"],
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository

    async def get_user(self, user_id: int) -> User | None:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None
        return self._user_model_to_domain(user)

    async def get_user_with_permissions(self, user_id: int) -> User | None:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None

        permissions = await self._user_repository.get_user_permissions(user_id)
        domain_user = self._user_model_to_domain(user)
        domain_user.permissions = permissions
        return domain_user

    async def get_all_users(self, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        users = await self._user_repository.get_all_with_roles(skip=skip, limit=limit)
        total = await self._user_repository.count()
        return [self._user_model_to_domain(u) for u in users], total

    async def update_user(self, user_id: int, user: User) -> User | None:
        user_db = await self._user_repository.get_by_id(user_id)
        if not user_db:
            return None

        if user.email and user.email != user_db.email:
            existing = await self._user_repository.get_by_email(user.email)
            if existing:
                msg = "Email already in use"
                raise ValueError(msg)

        update_data = user.model_dump(include=UPDATE_FIELDS, exclude_none=True)

        if update_data:
            user_db = await self._user_repository.update(user_db, update_data)

        return self._user_model_to_domain(user_db)

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.password_hash):
            msg = "Current password is incorrect"
            raise ValueError(msg)

        await self._user_repository.update(user, {"password_hash": hash_password(new_password)})
        return True

    async def delete_user(self, user_id: int) -> bool:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return False

        if await self._user_repository.has_team_memberships(user_id):
            msg = "Cannot delete user: they are a member of one or more teams. Remove them from all teams first."
            raise ValueError(msg)

        if await self._user_repository.has_career_paths(user_id):
            msg = "Cannot delete user: they have career paths assigned. Remove all career path assignments first."
            raise ValueError(msg)

        await self._user_repository.delete(user)
        return True

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        role = await self._role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self._user_repository.assign_role(user_id, role.role_id)
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        role = await self._role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self._user_repository.remove_role(user_id, role.role_id)
        return True

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
