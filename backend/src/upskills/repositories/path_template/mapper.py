from upskills.domain import PathTemplate
from upskills.repositories.base import BaseMapper

from .models import PathTemplate as PathTemplateModel


class PathTemplateMapper(BaseMapper[PathTemplate, PathTemplateModel]):
    _exclude_fields = frozenset({"path_template_id", "steps"})
    _fk_mappings = {"career": "career_id"}
