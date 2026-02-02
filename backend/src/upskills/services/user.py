from dependency_injector.wiring import Provide, inject

from upskills.core import hash_password, verify_password
from upskills.domain import User
from upskills.repositories import RoleRepository, UserRepository


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
        return await self._user_repository.get_by_id_with_roles(user_id)

    async def get_user_with_permissions(self, user_id: int) -> User | None:
        user = await self._user_repository.get_by_id_with_roles(user_id)
        if not user:
            return None

        permissions = await self._user_repository.get_user_permissions(user_id)
        user.permissions = permissions
        return user

    async def get_all_users(self, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        users = await self._user_repository.get_all_with_roles(skip=skip, limit=limit)
        total = await self._user_repository.count()
        return users, total

    async def update_user(
        self,
        user_id: int,
        full_name: str | None = None,
        email: str | None = None,
        bio: str | None = None,
    ) -> User | None:
        db_model = await self._user_repository.get_by_id(user_id, id_column="user_id")
        if not db_model:
            return None

        if email and email != db_model.email:
            existing = await self._user_repository.get_by_email(email)
            if existing:
                msg = "Email already in use"
                raise ValueError(msg)

        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if email is not None:
            update_data["email"] = email
        if bio is not None:
            update_data["bio"] = bio

        if update_data:
            await self._user_repository.update(db_model, update_data)

        return await self._user_repository.get_by_id_with_roles(user_id)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> bool:
        db_model = await self._user_repository.get_by_id(user_id, id_column="user_id")
        if not db_model:
            return False

        if not verify_password(current_password, db_model.password_hash):
            msg = "Current password is incorrect"
            raise ValueError(msg)

        await self._user_repository.update(db_model, {"password_hash": hash_password(new_password)})
        return True

    async def delete_user(self, user_id: int) -> bool:
        db_model = await self._user_repository.get_by_id(user_id, id_column="user_id")
        if not db_model:
            return False

        if await self._user_repository.has_team_memberships(user_id):
            msg = "Cannot delete user: they are a member of one or more teams. Remove them from all teams first."
            raise ValueError(msg)

        if await self._user_repository.has_career_paths(user_id):
            msg = "Cannot delete user: they have career paths assigned. Remove all career path assignments first."
            raise ValueError(msg)

        await self._user_repository.delete(db_model)
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
