from upskills.domain import PathStep
from upskills.repositories.base import BaseMapper
from upskills.repositories.path_template.models import PathTemplateStep


class PathStepMapper(BaseMapper[PathStep, PathTemplateStep]):
    _exclude_fields = frozenset({"step_id", "dependencies"})
    _fk_mappings = {"path_template": "path_template_id"}
