from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import Team, TeamListItem, TeamMember
from upskills.repositories import TeamRepository, UserRepository


@dataclass
class TeamService:
    team_repository: TeamRepository = Provide["team_repository"]
    user_repository: UserRepository = Provide["user_repository"]

    async def get_team(self, team_id: int) -> Team | None:
        return await self.team_repository.get_by_id_with_members(team_id)

    async def get_all_teams(self, *, skip: int = 0, limit: int = 100) -> tuple[list[TeamListItem], int]:
        teams = await self.team_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self.team_repository.count()

        return [
            TeamListItem(
                team_id=t.team_id,
                name=t.name,
                member_count=len(t.members) if t.members else 0,
                manager_name=t.manager.full_name if t.manager else "Unknown",
            )
            for t in teams
        ], total

    async def get_teams_by_manager(self, manager_user_id: int) -> list[Team]:
        teams = await self.team_repository.get_teams_by_manager(manager_user_id)
        return [self.team_repository.to_domain(t) for t in teams]

    async def get_teams_for_user(self, user_id: int) -> list[Team]:
        teams = await self.team_repository.get_teams_for_user(user_id)
        return [
            Team(
                team_id=t.team_id,
                name=t.name,
                manager_user_id=t.manager_user_id,
            )
            for t in teams
        ]

    async def create_team(self, data: Team) -> Team:
        manager = await self.user_repository.get_by_id(data.manager_user_id)
        if not manager:
            msg = "Manager user not found"
            raise ValueError(msg)

        db_model = await self.team_repository.create(data)
        result = await self.team_repository.get_by_id_with_members(db_model.team_id)
        if not result:
            msg = "Failed to reload team after creation"
            raise RuntimeError(msg)
        return result

    async def update_team(self, team_id: int, data: Team) -> Team | None:
        db_model = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not db_model:
            return None

        if data.manager_user_id:
            manager = await self.user_repository.get_by_id(data.manager_user_id)
            if not manager:
                msg = "Manager user not found"
                raise ValueError(msg)

        await self.team_repository.update(db_model, data)
        return await self.team_repository.get_by_id_with_members(team_id)

    async def delete_team(self, team_id: int) -> bool:
        db_model = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not db_model:
            return False
        await self.team_repository.delete(db_model)
        return True

    async def add_member(self, team_id: int, user_id: int) -> bool:
        team = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not team:
            msg = "Team not found"
            raise ValueError(msg)

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        if await self.team_repository.is_member(team_id, user_id):
            msg = "User is already a member of this team"
            raise ValueError(msg)

        await self.team_repository.add_member(team_id, user_id)
        return True

    async def remove_member(self, team_id: int, user_id: int) -> bool:
        if not await self.team_repository.is_member(team_id, user_id):
            return False
        await self.team_repository.remove_member(team_id, user_id)
        return True

    async def get_team_members(self, team_id: int) -> list[TeamMember]:
        members = await self.team_repository.get_team_members(team_id)
        return [
            TeamMember(
                user_id=m.user_id,
                full_name=m.full_name,
                email=m.email,
            )
            for m in members
        ]
