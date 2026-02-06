from dependency_injector.wiring import Provide, inject

from upskills.domain import LogEntry
from upskills.repositories import LogEntryRepository, UserCareerPathRepository

CREATE_FIELDS = {
    "user_id",
    "user_career_path_id",
    "entry_type",
    "entry_date",
    "notes",
    "related_user_path_assignment_id",
}
UPDATE_FIELDS = {"entry_type", "entry_date", "notes"}


class LogbookService:
    @inject
    def __init__(
        self,
        log_repository: LogEntryRepository = Provide["log_entry_repository"],
        career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"],
    ) -> None:
        self._log_repository = log_repository
        self._career_path_repository = career_path_repository

    async def get_entries_for_career_path(
        self,
        user_career_path_id: int,
        entry_type: str | None = None,
    ) -> list[LogEntry]:
        return await self._log_repository.get_by_career_path(user_career_path_id, entry_type)

    async def get_entry(self, log_entry_id: int) -> LogEntry | None:
        entry_db = await self._log_repository.get_by_id(log_entry_id)
        if not entry_db:
            return None
        return self._log_repository.to_domain(entry_db, include_details=True)

    async def create_entry(self, entry: LogEntry) -> LogEntry:
        if entry.user_career_path_id is None:
            msg = "Career path ID is required"
            raise ValueError(msg)

        career_path = await self._career_path_repository.get_by_id(entry.user_career_path_id)
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        db_model = await self._log_repository.create(entry.model_dump(include=CREATE_FIELDS))
        return self._log_repository.to_domain(db_model)

    async def update_entry(self, log_entry_id: int, entry: LogEntry) -> LogEntry | None:
        entry_db = await self._log_repository.get_by_id(log_entry_id)
        if not entry_db:
            return None

        update_data = entry.model_dump(include=UPDATE_FIELDS, exclude_none=True)

        if update_data:
            updated_db = await self._log_repository.update(entry_db, update_data)
            return self._log_repository.to_domain(updated_db)
        return self._log_repository.to_domain(entry_db)

    async def delete_entry(self, log_entry_id: int) -> bool:
        entry_db = await self._log_repository.get_by_id(log_entry_id)
        if not entry_db:
            return False
        await self._log_repository.delete(entry_db)
        return True
