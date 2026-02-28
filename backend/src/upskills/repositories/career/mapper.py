from upskills.domain import Career
from upskills.repositories.base import BaseMapper

from .models import Career as CareerModel


class CareerMapper(BaseMapper[Career, CareerModel]):
    _exclude_fields = frozenset({"career_id", "path_templates"})
