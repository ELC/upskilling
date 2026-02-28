from datetime import date

from pydantic import Field

from upskills.api.schemas import BaseSchema
from upskills.domain import LogEntryType


class UserRef(BaseSchema):
    user_id: int


class CareerRef(BaseSchema):
    career_id: int


class UserCareerPathRef(BaseSchema):
    user_career_path_id: int
    user: UserRef | None = None
    career: CareerRef | None = None


class UserPathAssignmentRef(BaseSchema):
    user_path_assignment_id: int


class LogEntryCreate(BaseSchema):
    user: UserRef
    user_career_path: UserCareerPathRef
    entry_type: LogEntryType
    entry_date: date
    notes: str = Field(..., min_length=1)
    related_path_assignment: UserPathAssignmentRef | None = None


class LogEntryUpdate(BaseSchema):
    entry_type: LogEntryType | None = None
    entry_date: date | None = None
    notes: str | None = Field(None, min_length=1)


class LogEntryResponse(BaseSchema):
    log_entry_id: int
    user_id: int
    user_career_path_id: int
    entry_type: str
    entry_date: date
    notes: str | None = None
    related_user_path_assignment_id: int | None = None


class LogEntryDetailResponse(LogEntryResponse):
    user_name: str
    path_name: str | None = None
