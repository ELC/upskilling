from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import LogEntry as LogEntryDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user_path_assignment.models import UserPathAssignment

from .mapper import LogEntryMapper
from .models import LogEntry


class LogEntryRepository(BaseRepository[LogEntry, LogEntryDomain, LogEntryMapper]):
    _id_column = "log_entry_id"

    async def get_by_id(self, id_value: int) -> LogEntry | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment).selectinload(UserPathAssignment.path_template),
                )
                .where(LogEntry.log_entry_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career_path(self, user_career_path_id: int, entry_type: str | None = None) -> list[LogEntryDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment).selectinload(UserPathAssignment.path_template),
                )
                .where(LogEntry.user_career_path_id == user_career_path_id)
            )

            if entry_type:
                stmt = stmt.where(LogEntry.entry_type == entry_type)

            stmt = stmt.order_by(LogEntry.entry_date.desc())
            result = await session.execute(stmt)
            return [self._mapper.to_domain(e, include_details=True) for e in result.scalars().all()]

    async def get_by_user(self, user_id: int) -> list[LogEntryDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(selectinload(LogEntry.related_path_assignment))
                .where(LogEntry.user_id == user_id)
                .order_by(LogEntry.entry_date.desc())
            )
            result = await session.execute(stmt)
            return [self._mapper.to_domain(e) for e in result.scalars().all()]
