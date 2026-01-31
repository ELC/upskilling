"""API routers."""

from .auth import router as auth_router
from .careers import router as careers_router
from .logbook import router as logbook_router
from .path_steps import router as path_steps_router
from .path_templates import router as path_templates_router
from .progress import router as progress_router
from .teams import router as teams_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "careers_router",
    "logbook_router",
    "path_steps_router",
    "path_templates_router",
    "progress_router",
    "teams_router",
    "users_router",
]
