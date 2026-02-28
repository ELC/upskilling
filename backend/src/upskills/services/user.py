from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import User
from upskills.repositories import RoleRepository, UserRepository


@dataclass
class UserService:
    user_repository: UserRepository = Provide["user_repository"]
    role_repository: RoleRepository = Provide["role_repository"]

    async def get_user(self, user_id: int) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return self.user_repository.to_domain(user)

    async def get_user_with_permissions(self, user_id: int) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        permissions = await self.user_repository.get_user_permissions(user_id)
        user_domain = self.user_repository.to_domain(user)
        user_domain.permissions = permissions
        return user_domain

    async def get_all_users(self, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        users = await self.user_repository.get_all_with_roles(skip=skip, limit=limit)
        total = await self.user_repository.count()
        return [self.user_repository.to_domain(user) for user in users], total

    async def update_user(self, user: User) -> User:
        existing_user = await self.user_repository.get_by_id(user.user_id)
        if not existing_user:
            msg = "User not found"
            raise ValueError(msg)

        if user.email:
            await self.user_repository.validate_email_available(user.email, user)

        updated_user = await self.user_repository.update(existing_user, user)
        return self.user_repository.to_domain(updated_user)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            msg = "User not found"
            raise ValueError(msg)

        existing_user_domain = self.user_repository.to_domain(existing_user)
        if not existing_user_domain.verify_password(current_password):
            msg = "Current password is incorrect"
            raise ValueError(msg)

        await self.user_repository.update(existing_user, User(password=new_password))

    async def delete_user(self, user_id: int) -> None:
        user_to_delete = await self.user_repository.get_by_id(user_id)
        if not user_to_delete:
            msg = "User not found"
            raise ValueError(msg)

        if await self.user_repository.has_team_memberships(user_id):
            msg = "Cannot delete user: they are a member of one or more teams. Remove them from all teams first."
            raise ValueError(msg)

        if await self.user_repository.has_career_paths(user_id):
            msg = "Cannot delete user: they have career paths assigned. Remove all career path assignments first."
            raise ValueError(msg)

        await self.user_repository.delete(user_to_delete)

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        await self.user_repository.assign_role(user, role)
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        await self.user_repository.remove_role(user, role)
        return True
