"""Teams router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.team import (
    TeamCreate,
    TeamListResponse,
    TeamMemberAdd,
    TeamMemberBulkAdd,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
    TeamWithMembersResponse,
)
from upskills.services.team import TeamService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TeamListResponse])
async def list_teams(
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.view"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[TeamListResponse]:
    """List all teams (requires team.view permission)."""
    service = TeamService(session)
    skip = (page - 1) * page_size

    teams, total = await service.get_all_teams(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=teams,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/my-teams", response_model=list[TeamWithMembersResponse])
async def get_my_managed_teams(
    current_user: CurrentUser,
    session: DbSession,
) -> list[TeamWithMembersResponse]:
    """Get teams managed by the current user."""
    service = TeamService(session)
    return await service.get_teams_by_manager(current_user.user_id)


@router.get("/member-of", response_model=list[TeamResponse])
async def get_teams_im_member_of(
    current_user: CurrentUser,
    session: DbSession,
) -> list[TeamResponse]:
    """Get teams the current user is a member of."""
    service = TeamService(session)
    return await service.get_teams_for_user(current_user.user_id)


@router.post("", response_model=TeamWithMembersResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> TeamWithMembersResponse:
    """Create a new team (requires team.manage permission)."""
    service = TeamService(session)

    try:
        result = await service.create_team(
            name=data.name,
            manager_user_id=data.manager_user_id,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{team_id}", response_model=TeamWithMembersResponse)
async def get_team(
    team_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> TeamWithMembersResponse:
    """Get a specific team (requires team.view permission)."""
    service = TeamService(session)
    result = await service.get_team(team_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return result


@router.put("/{team_id}", response_model=TeamWithMembersResponse)
async def update_team(
    team_id: int,
    data: TeamUpdate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> TeamWithMembersResponse:
    """Update a team (requires team.manage permission)."""
    service = TeamService(session)

    try:
        result = await service.update_team(
            team_id,
            name=data.name,
            manager_user_id=data.manager_user_id,
        )
        await session.commit()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{team_id}", response_model=MessageResponse)
async def delete_team(
    team_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Delete a team (requires team.manage permission)."""
    service = TeamService(session)
    success = await service.delete_team(team_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return MessageResponse(message="Team deleted successfully.")


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
async def get_team_members(
    team_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> list[TeamMemberResponse]:
    """Get members of a team (requires team.view permission)."""
    service = TeamService(session)
    return await service.get_team_members(team_id)


@router.post("/{team_id}/members", response_model=MessageResponse)
async def add_team_member(
    team_id: int,
    data: TeamMemberAdd,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Add a member to a team (requires team.manage permission)."""
    service = TeamService(session)

    try:
        await service.add_member(team_id, data.user_id)
        await session.commit()
        return MessageResponse(message="Member added to team.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{team_id}/members/bulk", response_model=MessageResponse)
async def add_team_members_bulk(
    team_id: int,
    data: TeamMemberBulkAdd,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Add multiple members to a team (requires team.manage permission)."""
    service = TeamService(session)
    errors = []

    for user_id in data.user_ids:
        try:
            await service.add_member(team_id, user_id)
        except ValueError as e:
            errors.append(f"User {user_id}: {str(e)}")

    await session.commit()

    if errors:
        return MessageResponse(
            message=f"Added {len(data.user_ids) - len(errors)} members.",
            detail="; ".join(errors),
        )

    return MessageResponse(message=f"Added {len(data.user_ids)} members to team.")


@router.delete("/{team_id}/members/{user_id}", response_model=MessageResponse)
async def remove_team_member(
    team_id: int,
    user_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Remove a member from a team (requires team.manage permission)."""
    service = TeamService(session)
    success = await service.remove_member(team_id, user_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in team",
        )

    return MessageResponse(message="Member removed from team.")
