"""Progress tracking router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from upskills.core.dependencies import CurrentUser, DbSession, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse
from upskills.models.domain.progress import (
    DashboardStats,
    MenteeProgressSummary,
    UserCareerPathCreate,
    UserCareerPathDetailResponse,
    UserCareerPathResponse,
    UserCareerPathUpdate,
    UserPathAssignmentCreate,
    UserPathAssignmentDetailResponse,
    UserPathAssignmentResponse,
    UserPathAssignmentUpdate,
    UserStepProgressResponse,
    UserStepProgressUpdate,
)
from upskills.services.progress import ProgressService
from upskills.services.team import TeamService

router = APIRouter()


# === Dashboard ===


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_user: CurrentUser,
    session: DbSession,
) -> DashboardStats:
    """Get dashboard statistics for the current user."""
    service = ProgressService(session)
    return await service.get_dashboard_stats(current_user.user_id)


# === Career Paths ===


@router.get("/career-paths", response_model=list[UserCareerPathDetailResponse])
async def get_my_career_paths(
    current_user: CurrentUser,
    session: DbSession,
) -> list[UserCareerPathDetailResponse]:
    """Get career paths for the current user."""
    service = ProgressService(session)
    return await service.get_user_career_paths(current_user.user_id)


@router.get("/career-paths/{career_path_id}", response_model=UserCareerPathDetailResponse)
async def get_career_path(
    career_path_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> UserCareerPathDetailResponse:
    """Get a specific career path."""
    service = ProgressService(session)
    result = await service.get_career_path(career_path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return result


@router.post(
    "/career-paths",
    response_model=UserCareerPathResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_career_path(
    data: UserCareerPathCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserCareerPathResponse:
    """Assign a career path to a user (requires paths.assign permission)."""
    service = ProgressService(session)

    try:
        result = await service.assign_career_path(
            user_id=data.user_id,
            career_id=data.career_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/career-paths/{career_path_id}", response_model=UserCareerPathResponse)
async def update_career_path(
    career_path_id: int,
    data: UserCareerPathUpdate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserCareerPathResponse:
    """Update a career path (requires paths.assign permission)."""
    service = ProgressService(session)
    result = await service.update_career_path(
        career_path_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return result


# === Path Assignments ===


@router.get(
    "/career-paths/{career_path_id}/assignments",
    response_model=list[UserPathAssignmentResponse],
)
async def get_path_assignments(
    career_path_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> list[UserPathAssignmentResponse]:
    """Get path assignments for a career path."""
    service = ProgressService(session)
    return await service.get_path_assignments(career_path_id)


@router.post(
    "/assignments",
    response_model=UserPathAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_path(
    data: UserPathAssignmentCreate,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserPathAssignmentResponse:
    """Assign a path to a user's career (requires paths.assign permission)."""
    service = ProgressService(session)

    try:
        result = await service.assign_path(
            user_career_path_id=data.user_career_path_id,
            path_template_id=data.path_template_id,
            start_date=data.start_date,
            deadline=data.deadline,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/assignments/{assignment_id}", response_model=UserPathAssignmentDetailResponse)
async def get_assignment(
    assignment_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> UserPathAssignmentDetailResponse:
    """Get a specific path assignment with details."""
    service = ProgressService(session)
    result = await service.get_path_assignment(assignment_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


@router.put("/assignments/{assignment_id}", response_model=UserPathAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: UserPathAssignmentUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> UserPathAssignmentResponse:
    """Update a path assignment status."""
    service = ProgressService(session)
    result = await service.update_assignment_status(
        assignment_id,
        status=data.status.value if data.status else None,
        mentor_validation_status=data.mentor_validation_status.value if data.mentor_validation_status else None,
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


# === Mentor Validation ===


@router.get("/pending-validations", response_model=list[UserPathAssignmentDetailResponse])
async def get_pending_validations(
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> list[UserPathAssignmentDetailResponse]:
    """Get all assignments pending mentor validation."""
    service = ProgressService(session)
    return await service.get_pending_validations()


@router.post("/assignments/{assignment_id}/approve", response_model=UserPathAssignmentResponse)
async def approve_assignment(
    assignment_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> UserPathAssignmentResponse:
    """Approve a completed path assignment."""
    service = ProgressService(session)
    result = await service.update_assignment_status(
        assignment_id,
        mentor_validation_status="Approved",
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


@router.post("/assignments/{assignment_id}/reject", response_model=UserPathAssignmentResponse)
async def reject_assignment(
    assignment_id: int,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> UserPathAssignmentResponse:
    """Reject a completed path assignment."""
    service = ProgressService(session)
    result = await service.update_assignment_status(
        assignment_id,
        mentor_validation_status="Rejected",
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


# === Step Progress ===


@router.get(
    "/assignments/{assignment_id}/steps",
    response_model=list[UserStepProgressResponse],
)
async def get_step_progress(
    assignment_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> list[UserStepProgressResponse]:
    """Get step progress for an assignment."""
    service = ProgressService(session)
    return await service.get_step_progress(assignment_id)


@router.put("/steps/{progress_id}", response_model=UserStepProgressResponse)
async def update_step_progress(
    progress_id: int,
    data: UserStepProgressUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> UserStepProgressResponse:
    """Update step progress."""
    service = ProgressService(session)
    result = await service.update_step_progress(
        progress_id,
        status=data.status.value if data.status else None,
        progress_percent=data.progress_percent,
        planned_start_date=data.planned_start_date,
        planned_end_date=data.planned_end_date,
        actual_start_date=data.actual_start_date,
        actual_end_date=data.actual_end_date,
    )
    await session.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step progress not found",
        )

    return result


# === Team Progress (for mentors) ===


@router.get("/team-progress", response_model=list[MenteeProgressSummary])
async def get_team_progress(
    current_user: CurrentUser,
    session: DbSession,
) -> list[MenteeProgressSummary]:
    """Get progress summaries for mentees in teams managed by current user."""
    team_service = TeamService(session)
    progress_service = ProgressService(session)

    # Get teams managed by current user
    teams = await team_service.get_teams_by_manager(current_user.user_id)

    # Collect all unique member IDs
    member_ids = set()
    for team in teams:
        for member in team.members:
            member_ids.add(member.user_id)

    if not member_ids:
        return []

    return await progress_service.get_mentee_progress_summaries(list(member_ids))
