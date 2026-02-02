"""User path assignment repository and models."""

from .models import UserPathAssignment
from .repository import UserPathAssignmentRepository

__all__ = [
    "UserPathAssignment",
    "UserPathAssignmentRepository",
]
