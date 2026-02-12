from dataclasses import dataclass

from dependency_injector.wiring import Provide

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


@dataclass
class ProgressService:
    career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"]
    assignment_repository: UserPathAssignmentRepository = Provide["user_path_assignment_repository"]
    step_progress_repository: UserStepProgressRepository = Provide["user_step_progress_repository"]
    user_repository: UserRepository = Provide["user_repository"]
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]

    # === User Career Paths ===

    async def get_user_paths(self, user_id: int) -> list[UserCareerPath]:
        return await self.career_path_repository.get_by_user(user_id)

    async def get_path(self, user_career_path_id: int) -> UserCareerPath | None:
        return await self.career_path_repository.get_by_id_with_details(user_career_path_id)

    async def assign(self, data: UserCareerPath) -> UserCareerPath:
        user = await self.user_repository.get_by_id(data.user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        db_model = await self.career_path_repository.create(data)
        return self.career_path_repository.to_domain(db_model)

    async def update(self, user_career_path_id: int, data: UserCareerPath) -> UserCareerPath | None:
        db_model = await self.career_path_repository.get_by_id(user_career_path_id, id_column="user_career_path_id")
        if not db_model:
            return None
        updated = await self.career_path_repository.update(db_model, data)
        return self.career_path_repository.to_domain(updated)

    # === Path Assignments ===

    async def get_path_assignments(self, user_career_path_id: int) -> list[UserPathAssignment]:
        return await self.assignment_repository.get_by_career_path(user_career_path_id)

    async def get_path_assignment(self, assignment_id: int) -> UserPathAssignment | None:
        return await self.assignment_repository.get_by_id_with_details(assignment_id)

    async def assign_path(self, data: UserPathAssignment) -> UserPathAssignment:
        career_path = await self.career_path_repository.get_by_id(
            data.user_career_path_id, id_column="user_career_path_id"
        )
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        template = await self.path_template_repository.get_by_id(data.path_template_id, id_column="path_template_id")
        if not template:
            msg = "Path template not found"
            raise ValueError(msg)

        db_model = await self.assignment_repository.create(data)

        if template.steps:
            for step in template.steps:
                step_data = UserStepProgress(
                    user_path_assignment_id=db_model.user_path_assignment_id,
                    step_id=step.step_id,
                    status="Pending",
                    progress_percent=0,
                )
                await self.step_progress_repository.create(step_data)

        return self.assignment_repository.to_domain(db_model)

    async def update_assignment_status(self, assignment_id: int, data: UserPathAssignment) -> UserPathAssignment | None:
        db_model = await self.assignment_repository.get_by_id(assignment_id, id_column="user_path_assignment_id")
        if not db_model:
            return None

        updated = await self.assignment_repository.update(db_model, data)
        await self._recalculate_progress(updated.user_career_path_id)

        return self.assignment_repository.to_domain(updated)

    async def get_pending_validations(self) -> list[UserPathAssignment]:
        assignments = await self.assignment_repository.get_pending_validation()
        return [self.assignment_repository.to_domain(a, include_details=True) for a in assignments]

    # === Step Progress ===

    async def get_step_progress(self, assignment_id: int) -> list[UserStepProgress]:
        return await self.step_progress_repository.get_by_assignment(assignment_id)

    async def update_step_progress(self, progress_id: int, data: UserStepProgress) -> UserStepProgress | None:
        db_model = await self.step_progress_repository.get_by_id(progress_id, id_column="user_step_progress_id")
        if not db_model:
            return None

        updated = await self.step_progress_repository.update(db_model, data)
        await self._recalculate_assignment_progress(updated.user_path_assignment_id)

        return self.step_progress_repository.to_domain(updated)

    # === Dashboard ===

    async def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        career_path = await self.career_path_repository.get_active_for_user(user_id)

        if not career_path:
            return DashboardStats()

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
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                continue

            career_path = await self.career_path_repository.get_active_for_user(user_id)
            if not career_path:
                continue

            completed, total = await self.assignment_repository.count_completed_for_career_path(
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

    # === Private Helpers ===

    async def _recalculate_assignment_progress(self, assignment_id: int) -> None:
        db_model = await self.assignment_repository.get_by_id(assignment_id, id_column="user_path_assignment_id")
        if not db_model or not db_model.step_progress:
            return

        total_steps = len(db_model.step_progress)
        if total_steps == 0:
            return

        total_progress = sum(sp.progress_percent for sp in db_model.step_progress)
        new_progress = total_progress // total_steps

        all_completed = all(sp.status == "Completed" for sp in db_model.step_progress)
        new_status = (
            "Completed"
            if all_completed
            else ("In Progress" if any(sp.status != "Pending" for sp in db_model.step_progress) else "Pending")
        )

        update_data = UserPathAssignment(progress_percent=new_progress, status=new_status)
        await self.assignment_repository.update(db_model, update_data)
        await self._recalculate_progress(db_model.user_career_path_id)

    async def _recalculate_progress(self, career_path_id: int) -> None:
        db_model = await self.career_path_repository.get_by_id(career_path_id, id_column="user_career_path_id")
        if not db_model or not db_model.path_assignments:
            return

        total_assignments = len(db_model.path_assignments)
        if total_assignments == 0:
            return

        total_progress = sum(a.progress_percent for a in db_model.path_assignments)
        new_progress = total_progress // total_assignments

        update_data = UserCareerPath(overall_progress_percent=new_progress)
        await self.career_path_repository.update(db_model, update_data)
