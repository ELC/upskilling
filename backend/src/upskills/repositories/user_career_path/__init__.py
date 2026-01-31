"""User career path repository and models."""

from .models import UserCareerPath
from .repository import UserCareerPathRepository

__all__ = [
    "UserCareerPath",
    "UserCareerPathRepository",
]
