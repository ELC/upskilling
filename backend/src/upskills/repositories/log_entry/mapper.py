from upskills.domain import LogEntry
from upskills.domain import PathTemplate as PathTemplateDomain
from upskills.domain import User as UserDomain
from upskills.domain import UserCareerPath
from upskills.domain import UserPathAssignment as UserPathAssignmentDomain
from upskills.repositories.base import BaseMapper

from .models import LogEntry as LogEntryModel


class LogEntryMapper(BaseMapper[LogEntry, LogEntryModel]):
    _exclude_fields = frozenset({"log_entry_id", "user_name", "path_name"})
    _fk_mappings = {
        "user": "user_id",
        "user_career_path": "user_career_path_id",
        "related_path_assignment": ("related_user_path_assignment_id", "user_path_assignment_id"),
    }

    @classmethod
    def to_domain(cls, entry: LogEntryModel, *, include_details: bool = False) -> LogEntry:
        """Convert a database LogEntry entity to a domain object."""
        user_name = None
        path_name = None
        user = UserDomain(user_id=entry.user_id)
        related_assignment = None

        if include_details:
            user = UserDomain.model_validate(entry.user) if entry.user else UserDomain(user_id=entry.user_id)
            user_name = entry.user.full_name if entry.user else None

            if entry.related_path_assignment:
                template = (
                    PathTemplateDomain.model_validate(entry.related_path_assignment.path_template)
                    if entry.related_path_assignment.path_template
                    else None
                )
                path_name = (
                    entry.related_path_assignment.path_template.name
                    if entry.related_path_assignment.path_template
                    else None
                )

                related_assignment = UserPathAssignmentDomain(
                    user_path_assignment_id=entry.related_path_assignment.user_path_assignment_id,
                    path_template=template,
                    start_date=entry.related_path_assignment.start_date,
                    deadline=entry.related_path_assignment.deadline,
                    status=entry.related_path_assignment.status,
                    progress_percent=entry.related_path_assignment.progress_percent,
                    mentor_validation_status=entry.related_path_assignment.mentor_validation_status,
                )

        return LogEntry(
            log_entry_id=entry.log_entry_id,
            user=user,
            user_career_path=UserCareerPath.model_construct(user_career_path_id=entry.user_career_path_id),
            entry_type=entry.entry_type,
            entry_date=entry.entry_date,
            notes=entry.notes,
            related_path_assignment=related_assignment,
            user_name=user_name,
            path_name=path_name,
        )
