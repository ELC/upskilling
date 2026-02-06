from dependency_injector.wiring import Provide, inject

from upskills.domain import (
    DashboardStats,
    MenteeProgressSummary,
    UserCareerPath,
    UserPathAssignment,
    UserStepProgress,
)
from upskills.repositories import (
    PathTemplateRepository,
    UserCareerPathRepository,
    UserPathAssignmentRepository,
    UserRepository,
    UserStepProgressRepository,
)

CAREER_PATH_CREATE_FIELDS = {"user_id", "career_id", "start_date", "end_date"}
CAREER_PATH_UPDATE_FIELDS = {"start_date", "end_date"}
ASSIGNMENT_UPDATE_FIELDS = {"status", "mentor_validation_status"}
STEP_PROGRESS_UPDATE_FIELDS = {
    "status",
    "progress_percent",
    "planned_start_date",
    "planned_end_date",
    "actual_start_date",
    "actual_end_date",
}


class ProgressService:
    @inject
    def __init__(  # pylint: disable=too-many-arguments R0913
        self,
        *,
        career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"],
        assignment_repository: UserPathAssignmentRepository = Provide["user_path_assignment_repository"],
        step_progress_repository: UserStepProgressRepository = Provide["user_step_progress_repository"],
        user_repository: UserRepository = Provide["user_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._career_path_repository = career_path_repository
        self._assignment_repository = assignment_repository
        self._step_progress_repository = step_progress_repository
        self._user_repository = user_repository
        self._path_template_repository = path_template_repository

    async def get_user_career_paths(self, user_id: int) -> list[UserCareerPath]:
        return await self._career_path_repository.get_by_user(user_id)

    async def get_career_path(self, user_career_path_id: int) -> UserCareerPath | None:
        path_db = await self._career_path_repository.get_by_id(user_career_path_id)
        if not path_db:
            return None
        return self._career_path_repository.to_domain(path_db, include_assignments=True)

    async def assign_career_path(self, career_path: UserCareerPath) -> UserCareerPath:
        if career_path.user_id is None:
            msg = "User ID is required"
            raise ValueError(msg)

        user = await self._user_repository.get_by_id(career_path.user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        created = await self._career_path_repository.create(career_path.model_dump(include=CAREER_PATH_CREATE_FIELDS))
        return self._career_path_repository.to_domain(created)

    async def update_career_path(self, user_career_path_id: int, career_path: UserCareerPath) -> UserCareerPath | None:
        path_db = await self._career_path_repository.get_by_id(user_career_path_id)
        if not path_db:
            return None

        update_data = career_path.model_dump(include=CAREER_PATH_UPDATE_FIELDS, exclude_none=True)

        if update_data:
            updated_db = await self._career_path_repository.update(path_db, update_data)
            return self._career_path_repository.to_domain(updated_db)
        return self._career_path_repository.to_domain(path_db)

    async def get_path_assignments(self, user_career_path_id: int) -> list[UserPathAssignment]:
        assignments_db = await self._assignment_repository.get_by_career_path(user_career_path_id)
        return [self._assignment_repository.to_domain(a) for a in assignments_db]

    async def get_path_assignment(self, assignment_id: int) -> UserPathAssignment | None:
        assignment_db = await self._assignment_repository.get_by_id(assignment_id)
        if not assignment_db:
            return None
        return self._assignment_repository.to_domain(assignment_db, include_details=True)

    async def assign_path(self, assignment: UserPathAssignment) -> UserPathAssignment:
        if assignment.user_career_path_id is None:
            msg = "Career path ID is required"
            raise ValueError(msg)

        career_path = await self._career_path_repository.get_by_id(assignment.user_career_path_id)
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        if assignment.path_template_id is None:
            msg = "Path template ID is required"
            raise ValueError(msg)

        template = await self._path_template_repository.get_by_id(
            assignment.path_template_id, id_column="path_template_id"
        )
        if not template:
            msg = "Path template not found"
            raise ValueError(msg)

        assignment_data = assignment.model_dump(
            include={"user_career_path_id", "path_template_id", "start_date", "deadline"}
        )
        assignment_data["status"] = "Pending"
        assignment_data["progress_percent"] = 0
        assignment_data["mentor_validation_status"] = "Pending"

        db_model = await self._assignment_repository.create(assignment_data)

        template_domain = self._path_template_repository.to_domain(template)
        if template_domain.steps:
            for step in template_domain.steps:
                step_data = {
                    "user_path_assignment_id": db_model.user_path_assignment_id,
                    "step_id": step.step_id,
                    "status": "Pending",
                    "progress_percent": 0,
                }
                await self._step_progress_repository.create(step_data)

        return self._assignment_repository.to_domain(db_model)

    async def update_assignment_status(
        self, assignment_id: int, assignment: UserPathAssignment
    ) -> UserPathAssignment | None:
        assignment_db = await self._assignment_repository.get_by_id(assignment_id)
        if not assignment_db:
            return None

        update_data = assignment.model_dump(include=ASSIGNMENT_UPDATE_FIELDS, exclude_none=True)

        if update_data:
            updated_db = await self._assignment_repository.update(assignment_db, update_data)
            await self._recalculate_career_progress(updated_db.user_career_path_id)
            return self._assignment_repository.to_domain(updated_db)
        return self._assignment_repository.to_domain(assignment_db)

    async def get_pending_validations(self) -> list[UserPathAssignment]:
        assignments_db = await self._assignment_repository.get_pending_validation()
        return [self._assignment_repository.to_domain(a, include_details=True) for a in assignments_db]

    async def get_step_progress(self, assignment_id: int) -> list[UserStepProgress]:
        return await self._step_progress_repository.get_by_assignment(assignment_id)

    async def update_step_progress(self, progress_id: int, progress: UserStepProgress) -> UserStepProgress | None:
        progress_db = await self._step_progress_repository.get_by_id(progress_id)
        if not progress_db:
            return None

        update_data = progress.model_dump(include=STEP_PROGRESS_UPDATE_FIELDS, exclude_none=True)

        if update_data:
            updated_db = await self._step_progress_repository.update(progress_db, update_data)
            await self._recalculate_assignment_progress(updated_db.user_path_assignment_id)
            return self._step_progress_repository.to_domain(updated_db)
        return self._step_progress_repository.to_domain(progress_db)

    async def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        career_path = await self._career_path_repository.get_active_for_user(user_id)

        if not career_path:
            return DashboardStats(
                current_career=None,
                current_path=None,
                current_path_progress=0,
                paths_remaining=0,
                overall_progress=0,
                skills_obtained=0,
            )

        current_path_name = None
        current_path_progress = 0
        paths_remaining = 0
        skills_obtained = 0

        if career_path.path_assignments:
            for assignment in career_path.path_assignments:
                if assignment.status == "In Progress":
                    current_path_name = assignment.path_template.name if assignment.path_template else None
                    current_path_progress = assignment.progress_percent
                elif assignment.status == "Pending":
                    paths_remaining += 1
                elif assignment.mentor_validation_status == "Approved":
                    skills_obtained += 1

        return DashboardStats(
            current_career=career_path.career.name if career_path.career else None,
            current_path=current_path_name,
            current_path_progress=current_path_progress,
            paths_remaining=paths_remaining,
            overall_progress=career_path.overall_progress_percent,
            skills_obtained=skills_obtained,
        )

    async def get_mentee_progress_summaries(self, team_user_ids: list[int]) -> list[MenteeProgressSummary]:
        summaries = []

        for user_id in team_user_ids:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                continue

            career_path = await self._career_path_repository.get_active_for_user(user_id)
            if not career_path:
                continue

            completed, total = await self._assignment_repository.count_completed_for_career_path(
                career_path.user_career_path_id
            )

            pending = 0
            if career_path.path_assignments:
                for a in career_path.path_assignments:
                    if a.status == "Completed" and a.mentor_validation_status == "Pending":
                        pending += 1

            summaries.append(
                MenteeProgressSummary(
                    user_id=user.user_id,
                    full_name=user.full_name,
                    email=user.email,
                    career_name=career_path.career.name if career_path.career else "Unknown",
                    start_date=career_path.start_date,
                    end_date=career_path.end_date,
                    overall_progress_percent=career_path.overall_progress_percent,
                    paths_completed=completed,
                    paths_total=total,
                    pending_validation=pending,
                )
            )

        return summaries

    async def _recalculate_assignment_progress(self, assignment_id: int) -> None:
        db_model = await self._assignment_repository.get_by_id(assignment_id, id_column="user_path_assignment_id")
        if not db_model or not db_model.step_progress:
            return

        total_steps = len(db_model.step_progress)
        if total_steps == 0:
            return

        total_progress = sum(sp.progress_percent for sp in db_model.step_progress)
        new_progress = total_progress // total_steps

        all_completed = all(sp.status == "Completed" for sp in db_model.step_progress)
        has_progress = any(sp.status != "Pending" for sp in db_model.step_progress)
        new_status = "Completed" if all_completed else ("In Progress" if has_progress else "Pending")

        update_data = UserPathAssignment(progress_percent=new_progress, status=new_status)
        await self._assignment_repository.update(db_model, update_data)
        await self._recalculate_career_progress(db_model.user_career_path_id)

    async def _recalculate_career_progress(self, career_path_id: int) -> None:
        db_model = await self._career_path_repository.get_by_id(career_path_id, id_column="user_career_path_id")
        if not db_model or not db_model.path_assignments:
            return

        total_assignments = len(db_model.path_assignments)
        if total_assignments == 0:
            return

        total_progress = sum(a.progress_percent for a in db_model.path_assignments)
        new_progress = total_progress // total_assignments

        await self._career_path_repository.update(
            db_model,
            {"overall_progress_percent": new_progress},
        )
