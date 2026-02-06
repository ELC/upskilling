from dependency_injector.wiring import Provide, inject

from upskills.domain import Team, TeamListItem, TeamMember
from upskills.repositories import TeamRepository, UserRepository

CREATE_FIELDS = {"name", "manager_user_id"}
UPDATE_FIELDS = {"name", "manager_user_id"}


class TeamService:
    @inject
    def __init__(
        self,
        team_repository: TeamRepository = Provide["team_repository"],
        user_repository: UserRepository = Provide["user_repository"],
    ) -> None:
        self._team_repository = team_repository
        self._user_repository = user_repository

    async def get_team(self, team_id: int) -> Team | None:
        team_db = await self._team_repository.get_by_id(team_id)
        if not team_db:
            return None
        return self._team_repository.to_domain(team_db)

    async def get_all_teams(self, *, skip: int = 0, limit: int = 100) -> tuple[list[TeamListItem], int]:
        teams = await self._team_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._team_repository.count()

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
        teams = await self._team_repository.get_teams_by_manager(manager_user_id)
        return [self._team_repository.to_domain(t) for t in teams]

    async def get_teams_for_user(self, user_id: int) -> list[Team]:
        teams = await self._team_repository.get_teams_for_user(user_id)
        return [self._team_repository.to_domain(t) for t in teams]

    async def create_team(self, team: Team) -> Team:
        if team.manager_user_id is None:
            msg = "Manager user ID is required"
            raise ValueError(msg)

        manager = await self._user_repository.get_by_id(team.manager_user_id)
        if not manager:
            msg = "Manager user not found"
            raise ValueError(msg)

        db_model = await self._team_repository.create(team.model_dump(include=CREATE_FIELDS))
        result_db = await self._team_repository.get_by_id(db_model.team_id)
        if not result_db:
            msg = "Failed to reload team after creation"
            raise RuntimeError(msg)
        return self._team_repository.to_domain(result_db)

    async def update_team(self, team_id: int, team: Team) -> Team | None:
        team_db = await self._team_repository.get_by_id(team_id)
        if not team_db:
            return None

        if team.manager_user_id:
            manager = await self._user_repository.get_by_id(team.manager_user_id)
            if not manager:
                msg = "Manager user not found"
                raise ValueError(msg)

        update_data = team.model_dump(include=UPDATE_FIELDS, exclude_none=True)

        if update_data:
            await self._team_repository.update(team_db, update_data)
        result_db = await self._team_repository.get_by_id(team_id)
        if not result_db:
            return None
        return self._team_repository.to_domain(result_db)

    async def delete_team(self, team_id: int) -> bool:
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            return False
        await self._team_repository.delete(team)
        return True

    async def add_member(self, team_id: int, user_id: int) -> bool:
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            msg = "Team not found"
            raise ValueError(msg)

        user = await self._user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        if await self._team_repository.is_member(team_id, user_id):
            msg = "User is already a member of this team"
            raise ValueError(msg)

        await self._team_repository.add_member(team_id, user_id)
        return True

    async def remove_member(self, team_id: int, user_id: int) -> bool:
        if not await self._team_repository.is_member(team_id, user_id):
            return False
        await self._team_repository.remove_member(team_id, user_id)
        return True

    async def get_team_members(self, team_id: int) -> list[TeamMember]:
        members = await self._team_repository.get_team_members(team_id)
        return [
            TeamMember(
                user_id=m.user_id,
                full_name=m.full_name,
                email=m.email,
            )
            for m in members
        ]
