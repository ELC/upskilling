from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import LogEntry
from upskills.repositories import LogEntryRepository, UserCareerPathRepository


@dataclass
class LogbookService:
    log_repository: LogEntryRepository = Provide["log_entry_repository"]
    career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"]

    async def get_for_career_path(
        self,
        user_career_path_id: int,
        entry_type: str | None = None,
    ) -> list[LogEntry]:
        return await self.log_repository.get_by_career_path(user_career_path_id, entry_type)

    async def get(self, log_entry_id: int) -> LogEntry | None:
        return await self.log_repository.get_by_id_with_details(log_entry_id)

    async def create(self, data: LogEntry) -> LogEntry:
        career_path = await self.career_path_repository.get_by_id(
            data.user_career_path_id, id_column="user_career_path_id"
        )
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        db_model = await self.log_repository.create(data)
        return self.log_repository.to_domain(db_model)

    async def update(self, log_entry_id: int, data: LogEntry) -> LogEntry | None:
        db_model = await self.log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not db_model:
            return None
        updated = await self.log_repository.update(db_model, data)
        return self.log_repository.to_domain(updated)

    async def delete(self, log_entry_id: int) -> bool:
        db_model = await self.log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not db_model:
            return False
        await self.log_repository.delete(db_model)
        return True
