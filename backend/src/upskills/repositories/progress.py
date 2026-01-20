"""Progress tracking repositories."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from upskills.models.db.career import PathTemplate
from upskills.models.db.progress import (
    LogEntry,
    UserCareerPath,
    UserPathAssignment,
    UserStepProgress,
)
from upskills.repositories.base import BaseRepository


class UserCareerPathRepository(BaseRepository[UserCareerPath]):
    """Repository for UserCareerPath operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserCareerPath)

    async def get_by_id(
        self, user_career_path_id: int, id_column: str = "user_career_path_id"
    ) -> UserCareerPath | None:
        """Get user career path by ID with related data."""
        stmt = (
            select(UserCareerPath)
            .options(
                selectinload(UserCareerPath.career),
                selectinload(UserCareerPath.path_assignments).selectinload(
                    UserPathAssignment.path_template
                ),
            )
            .where(UserCareerPath.user_career_path_id == user_career_path_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[UserCareerPath]:
        """Get all career paths for a user."""
        stmt = (
            select(UserCareerPath)
            .options(
                selectinload(UserCareerPath.career),
                selectinload(UserCareerPath.path_assignments),
            )
            .where(UserCareerPath.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_for_user(self, user_id: int) -> UserCareerPath | None:
        """Get the current active career path for a user (most recent)."""
        stmt = (
            select(UserCareerPath)
            .options(
                selectinload(UserCareerPath.career),
                selectinload(UserCareerPath.path_assignments).selectinload(
                    UserPathAssignment.path_template
                ),
            )
            .where(UserCareerPath.user_id == user_id)
            .order_by(UserCareerPath.start_date.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class UserPathAssignmentRepository(BaseRepository[UserPathAssignment]):
    """Repository for UserPathAssignment operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserPathAssignment)

    async def get_by_id(
        self, assignment_id: int, id_column: str = "user_path_assignment_id"
    ) -> UserPathAssignment | None:
        """Get path assignment by ID with related data."""
        stmt = (
            select(UserPathAssignment)
            .options(
                selectinload(UserPathAssignment.path_template).selectinload(PathTemplate.steps),
                selectinload(UserPathAssignment.step_progress),
            )
            .where(UserPathAssignment.user_path_assignment_id == assignment_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_career_path(self, user_career_path_id: int) -> list[UserPathAssignment]:
        """Get all path assignments for a career path."""
        stmt = (
            select(UserPathAssignment)
            .options(
                selectinload(UserPathAssignment.path_template),
                selectinload(UserPathAssignment.step_progress),
            )
            .where(UserPathAssignment.user_career_path_id == user_career_path_id)
            .order_by(UserPathAssignment.start_date)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_validation(
        self, mentor_user_id: int | None = None
    ) -> list[UserPathAssignment]:
        """Get all assignments pending mentor validation."""
        stmt = (
            select(UserPathAssignment)
            .options(
                selectinload(UserPathAssignment.path_template),
                selectinload(UserPathAssignment.user_career_path).selectinload(UserCareerPath.user),
            )
            .where(
                UserPathAssignment.status == "Completed",
                UserPathAssignment.mentor_validation_status == "Pending",
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_completed_for_career_path(self, user_career_path_id: int) -> tuple[int, int]:
        """Count completed and total assignments for a career path."""
        total_stmt = (
            select(func.count())
            .select_from(UserPathAssignment)
            .where(UserPathAssignment.user_career_path_id == user_career_path_id)
        )
        completed_stmt = (
            select(func.count())
            .select_from(UserPathAssignment)
            .where(
                UserPathAssignment.user_career_path_id == user_career_path_id,
                UserPathAssignment.mentor_validation_status == "Approved",
            )
        )

        total_result = await self._session.execute(total_stmt)
        completed_result = await self._session.execute(completed_stmt)

        return completed_result.scalar() or 0, total_result.scalar() or 0


class UserStepProgressRepository(BaseRepository[UserStepProgress]):
    """Repository for UserStepProgress operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserStepProgress)

    async def get_by_id(
        self, progress_id: int, id_column: str = "user_step_progress_id"
    ) -> UserStepProgress | None:
        """Get step progress by ID."""
        stmt = (
            select(UserStepProgress)
            .options(selectinload(UserStepProgress.step))
            .where(UserStepProgress.user_step_progress_id == progress_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_assignment(self, user_path_assignment_id: int) -> list[UserStepProgress]:
        """Get all step progress for an assignment."""
        stmt = (
            select(UserStepProgress)
            .options(selectinload(UserStepProgress.step))
            .where(UserStepProgress.user_path_assignment_id == user_path_assignment_id)
            .order_by(UserStepProgress.step_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_or_create(self, user_path_assignment_id: int, step_id: int) -> UserStepProgress:
        """Get existing step progress or create a new one."""
        stmt = select(UserStepProgress).where(
            UserStepProgress.user_path_assignment_id == user_path_assignment_id,
            UserStepProgress.step_id == step_id,
        )
        result = await self._session.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            progress = UserStepProgress(
                user_path_assignment_id=user_path_assignment_id,
                step_id=step_id,
            )
            self._session.add(progress)
            await self._session.flush()
            await self._session.refresh(progress)

        return progress


class LogEntryRepository(BaseRepository[LogEntry]):
    """Repository for LogEntry operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LogEntry)

    async def get_by_id(
        self, log_entry_id: int, id_column: str = "log_entry_id"
    ) -> LogEntry | None:
        """Get log entry by ID."""
        stmt = (
            select(LogEntry)
            .options(
                selectinload(LogEntry.user),
                selectinload(LogEntry.related_path_assignment),
            )
            .where(LogEntry.log_entry_id == log_entry_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_career_path(
        self, user_career_path_id: int, entry_type: str | None = None
    ) -> list[LogEntry]:
        """Get all log entries for a career path."""
        stmt = (
            select(LogEntry)
            .options(
                selectinload(LogEntry.user),
                selectinload(LogEntry.related_path_assignment).selectinload(
                    UserPathAssignment.path_template
                ),
            )
            .where(LogEntry.user_career_path_id == user_career_path_id)
        )

        if entry_type:
            stmt = stmt.where(LogEntry.entry_type == entry_type)

        stmt = stmt.order_by(LogEntry.entry_date.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[LogEntry]:
        """Get all log entries about a user."""
        stmt = (
            select(LogEntry)
            .options(selectinload(LogEntry.related_path_assignment))
            .where(LogEntry.user_id == user_id)
            .order_by(LogEntry.entry_date.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
