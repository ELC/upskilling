from upskills.domain import Team
from upskills.repositories.base import BaseMapper

from .models import Team as TeamModel


class TeamMapper(BaseMapper[Team, TeamModel]):
    _exclude_fields = frozenset({"team_id", "members"})
    _fk_mappings = {"manager": ("manager_user_id", "user_id")}
