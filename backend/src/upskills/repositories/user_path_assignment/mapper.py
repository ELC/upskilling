from upskills.domain import UserPathAssignment
from upskills.repositories.base import BaseMapper

from .models import UserPathAssignment as UserPathAssignmentModel


class UserPathAssignmentMapper(BaseMapper[UserPathAssignment, UserPathAssignmentModel]):
    _exclude_fields = frozenset({"user_path_assignment_id", "step_progress"})
    _fk_mappings = {"path_template": "path_template_id"}
