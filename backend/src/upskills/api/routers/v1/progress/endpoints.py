from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import CurrentUser, require_permissions
from upskills.domain import UserCareerPath, UserPathAssignment, UserStepProgress
from upskills.services import ProgressService, TeamService

from .schemas import (
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

router = APIRouter(prefix="/progress", tags=["Progress"])


# === Dashboard ===


@router.get("/dashboard")
@inject
async def get_dashboard(
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> DashboardStats:
    result = await service.get_dashboard_stats(current_user.user_id)
    return DashboardStats.model_validate(result.model_dump())


# === Career Paths ===


@router.get("/career-paths")
@inject
async def get_my_career_paths(
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserCareerPathDetailResponse]:
    paths = await service.get_user_paths(current_user.user_id)
    return [UserCareerPathDetailResponse.model_validate(p.model_dump()) for p in paths]


@router.get("/career-paths/{career_path_id}")
@inject
async def get_career_path(
    career_path_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathDetailResponse:
    result = await service.get_path(career_path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return UserCareerPathDetailResponse.model_validate(result.model_dump())


@router.post(
    "/career-paths",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("paths.assign"))],
)
@inject
async def assign_career_path(
    data: UserCareerPathCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathResponse:
    try:
        input_data = UserCareerPath(
            user_id=data.user_id,
            career_id=data.career_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        result = await service.assign(input_data)
        return UserCareerPathResponse.model_validate(result.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put(
    "/career-paths/{career_path_id}",
    dependencies=[Depends(require_permissions("paths.assign"))],
)
@inject
async def update_career_path(
    career_path_id: int,
    data: UserCareerPathUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathResponse:
    input_data = UserCareerPath(
        start_date=data.start_date,
        end_date=data.end_date,
    )
    result = await service.update(career_path_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return UserCareerPathResponse.model_validate(result.model_dump())


# === Path Assignments ===


@router.get("/career-paths/{career_path_id}/assignments")
@inject
async def get_path_assignments(
    career_path_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserPathAssignmentResponse]:
    assignments = await service.get_path_assignments(career_path_id)
    return [UserPathAssignmentResponse.model_validate(a.model_dump()) for a in assignments]


@router.post(
    "/assignments",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("paths.assign"))],
)
@inject
async def assign_path(
    data: UserPathAssignmentCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    try:
        input_data = UserPathAssignment(
            user_career_path_id=data.user_career_path_id,
            path_template_id=data.path_template_id,
            start_date=data.start_date,
            deadline=data.deadline,
        )
        result = await service.assign_path(input_data)
        return UserPathAssignmentResponse.model_validate(result.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/assignments/{assignment_id}")
@inject
async def get_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentDetailResponse:
    result = await service.get_path_assignment(assignment_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentDetailResponse.model_validate(result.model_dump())


@router.put("/assignments/{assignment_id}")
@inject
async def update_assignment(
    assignment_id: int,
    data: UserPathAssignmentUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    input_data = UserPathAssignment(
        status=data.status.value if data.status else None,
        mentor_validation_status=data.mentor_validation_status.value if data.mentor_validation_status else None,
    )
    result = await service.update_assignment_status(assignment_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


# === Mentor Validation ===


@router.get(
    "/pending-validations",
    dependencies=[Depends(require_permissions("paths.validate"))],
)
@inject
async def get_pending_validations(
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserPathAssignmentDetailResponse]:
    assignments = await service.get_pending_validations()
    return [UserPathAssignmentDetailResponse.model_validate(a.model_dump()) for a in assignments]


@router.post(
    "/assignments/{assignment_id}/approve",
    dependencies=[Depends(require_permissions("paths.validate"))],
)
@inject
async def approve_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    input_data = UserPathAssignment(mentor_validation_status="Approved")
    result = await service.update_assignment_status(assignment_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


@router.post(
    "/assignments/{assignment_id}/reject",
    dependencies=[Depends(require_permissions("paths.validate"))],
)
@inject
async def reject_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    input_data = UserPathAssignment(mentor_validation_status="Rejected")
    result = await service.update_assignment_status(assignment_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


# === Step Progress ===


@router.get("/assignments/{assignment_id}/steps")
@inject
async def get_step_progress(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserStepProgressResponse]:
    progress_list = await service.get_step_progress(assignment_id)
    return [UserStepProgressResponse.model_validate(p.model_dump()) for p in progress_list]


@router.put("/steps/{progress_id}")
@inject
async def update_step_progress(
    progress_id: int,
    data: UserStepProgressUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserStepProgressResponse:
    input_data = UserStepProgress(
        status=data.status.value if data.status else None,
        progress_percent=data.progress_percent,
        planned_start_date=data.planned_start_date,
        planned_end_date=data.planned_end_date,
        actual_start_date=data.actual_start_date,
        actual_end_date=data.actual_end_date,
    )
    result = await service.update_step_progress(progress_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step progress not found",
        )

    return UserStepProgressResponse.model_validate(result.model_dump())


# === Team Progress (for mentors) ===


@router.get("/team-progress")
@inject
async def get_team_progress(
    current_user: CurrentUser,
    team_service: Annotated[TeamService, Depends(Provide["team_service"])],
    progress_service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[MenteeProgressSummary]:
    teams = await team_service.get_teams_by_manager(current_user.user_id)

    member_ids: set[int] = set()
    for team in teams:
        member_ids.update(member.user_id for member in team.members)

    if not member_ids:
        return []

    summaries = await progress_service.get_mentee_progress_summaries(list(member_ids))
    return [MenteeProgressSummary.model_validate(s.model_dump()) for s in summaries]
