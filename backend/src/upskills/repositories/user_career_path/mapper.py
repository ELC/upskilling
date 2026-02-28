from upskills.domain import UserCareerPath
from upskills.repositories.base import BaseMapper

from .models import UserCareerPath as UserCareerPathModel


class UserCareerPathMapper(BaseMapper[UserCareerPath, UserCareerPathModel]):
    _exclude_fields = frozenset({"user_career_path_id", "career_name", "career_specialization", "path_assignments"})
    _fk_mappings = {"user": "user_id", "career": "career_id"}
