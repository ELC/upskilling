from upskills.domain import UserStepProgress
from upskills.repositories.base import BaseMapper

from .models import UserStepProgress as UserStepProgressModel


class UserStepProgressMapper(BaseMapper[UserStepProgress, UserStepProgressModel]):
    _exclude_fields = frozenset({"user_step_progress_id", "updated_at"})
    _fk_mappings = {"step": "step_id"}
