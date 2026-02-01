from dependency_injector.wiring import Provide, inject

from upskills.domain import LogEntry
from upskills.repositories import LogEntryRepository, UserCareerPathRepository


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
        return await self._log_repository.get_by_id_with_details(log_entry_id)

    async def create_entry(self, data: LogEntry) -> LogEntry:
        career_path = await self._career_path_repository.get_by_id(
            data.user_career_path_id, id_column="user_career_path_id"
        )
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        db_model = await self._log_repository.create(data)
        return self._log_repository.to_domain(db_model)

    async def update_entry(self, log_entry_id: int, data: LogEntry) -> LogEntry | None:
        db_model = await self._log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not db_model:
            return None
        updated = await self._log_repository.update(db_model, data)
        return self._log_repository.to_domain(updated)

    async def delete_entry(self, log_entry_id: int) -> bool:
        db_model = await self._log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not db_model:
            return False
        await self._log_repository.delete(db_model)
        return True
