"""Users router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.user import (
    PasswordChange,
    UserResponse,
    UserUpdate,
    UserWithPermissions,
)
from upskills.services.user import UserService

router = APIRouter()


@router.get("")
async def list_users(
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.view"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[UserResponse]:
    """List all users (requires team.view permission)."""
    service = UserService(session)
    skip = (page - 1) * page_size

    users, total = await service.get_all_users(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/me")
async def get_my_profile(
    current_user: CurrentUser,
    session: DbSession,
) -> UserWithPermissions:
    """Get current user's profile with permissions."""
    service = UserService(session)
    result = await service.get_user_with_permissions(current_user.user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return result


@router.put("/me")
async def update_my_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> UserResponse:
    """Update current user's profile."""
    service = UserService(session)

    try:
        result = await service.update_user(
            current_user.user_id,
            full_name=data.full_name,
            email=data.email,
            bio=data.bio,
        )
        await session.commit()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/me/change-password")
async def change_my_password(
    data: PasswordChange,
    current_user: CurrentUser,
    session: DbSession,
) -> MessageResponse:
    """Change current user's password."""
    service = UserService(session)

    try:
        success = await service.change_password(
            current_user.user_id,
            data.current_password,
            data.new_password,
        )
        await session.commit()

        if success:
            return MessageResponse(message="Password changed successfully.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> UserResponse:
    """Get a specific user (requires team.view permission)."""
    service = UserService(session)
    result = await service.get_user(user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return result


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Delete a user (requires team.manage permission)."""
    service = UserService(session)
    success = await service.delete_user(user_id)
    await session.commit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return MessageResponse(message="User deleted successfully.")


@router.post("/{user_id}/roles/{role_name}")
async def assign_role_to_user(
    user_id: int,
    role_name: str,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Assign a role to a user (requires team.manage permission)."""
    service = UserService(session)

    try:
        await service.assign_role(user_id, role_name)
        await session.commit()
        return MessageResponse(message=f"Role '{role_name}' assigned to user.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{user_id}/roles/{role_name}")
async def remove_role_from_user(
    user_id: int,
    role_name: str,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Remove a role from a user (requires team.manage permission)."""
    service = UserService(session)

    try:
        await service.remove_role(user_id, role_name)
        await session.commit()
        return MessageResponse(message=f"Role '{role_name}' removed from user.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
