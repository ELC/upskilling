"""User step progress repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.progress import UserStepProgress
from upskills.repositories.base import BaseRepository


class UserStepProgressRepository(BaseRepository[UserStepProgress]):
    """Repository for UserStepProgress operations."""

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
            await self._session.commit()
            await self._session.refresh(progress)

        return progress
