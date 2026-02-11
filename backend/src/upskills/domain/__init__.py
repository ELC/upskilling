"""Domain models package."""

from .auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPayload,
    TokenResponse,
)
from .base import DomainModel, MessageResponse, PaginatedResponse
from .career import CareerCreate, CareerResponse, CareerUpdate, CareerWithPathsResponse
from .dashboard import DashboardStats, MenteeProgressSummary
from .enums import LogEntryType, ProgressStatus, ValidationStatus
from .log_entry import (
    LogEntryCreate,
    LogEntryCreateInput,
    LogEntryDetailResponse,
    LogEntryResponse,
    LogEntryUpdate,
)
from .path_step import (
    PathStepCreate,
    PathStepCreateInput,
    PathStepDependencyResponse,
    PathStepResponse,
    PathStepUpdate,
    PathStepUpdateInput,
    StepDependencyCreate,
)
from .path_template import (
    PathTemplateCreate,
    PathTemplateCreateInput,
    PathTemplateResponse,
    PathTemplateUpdate,
    PathTemplateUpdateInput,
    PathTemplateWithStepsResponse,
)
from .role import ActionResponse, RoleResponse
from .team import (
    TeamCreate,
    TeamListResponse,
    TeamMemberAdd,
    TeamMemberBulkAdd,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
    TeamWithMembersResponse,
)
from .user import (
    PasswordChange,
    PasswordReset,
    PasswordResetRequest,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
    UserWithPermissions,
)
from .user_career_path import (
    UserCareerPathCreate,
    UserCareerPathDetailResponse,
    UserCareerPathResponse,
    UserCareerPathUpdate,
)
from .user_path_assignment import (
    UserPathAssignmentCreate,
    UserPathAssignmentDetailResponse,
    UserPathAssignmentResponse,
    UserPathAssignmentUpdate,
)
from .user_step_progress import (
    StepProgressUpdateInput,
    UserStepProgressResponse,
    UserStepProgressUpdate,
)

__all__ = [
    "ActionResponse",
    "AuthResponse",
    "CareerCreate",
    "CareerResponse",
    "CareerUpdate",
    "CareerWithPathsResponse",
    "DashboardStats",
    "DomainModel",
    "LogEntryCreate",
    "LogEntryCreateInput",
    "LogEntryDetailResponse",
    "LogEntryResponse",
    "LogEntryType",
    "LogEntryUpdate",
    "LoginRequest",
    "MenteeProgressSummary",
    "MessageResponse",
    "PaginatedResponse",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetRequest",
    "PathStepCreate",
    "PathStepCreateInput",
    "PathStepDependencyResponse",
    "PathStepResponse",
    "PathStepUpdate",
    "PathStepUpdateInput",
    "PathTemplateCreate",
    "PathTemplateCreateInput",
    "PathTemplateResponse",
    "PathTemplateUpdate",
    "PathTemplateUpdateInput",
    "PathTemplateWithStepsResponse",
    "ProgressStatus",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RoleResponse",
    "StepDependencyCreate",
    "StepProgressUpdateInput",
    "TeamCreate",
    "TeamListResponse",
    "TeamMemberAdd",
    "TeamMemberBulkAdd",
    "TeamMemberResponse",
    "TeamResponse",
    "TeamUpdate",
    "TeamWithMembersResponse",
    "TokenPayload",
    "TokenResponse",
    "UserCareerPathCreate",
    "UserCareerPathDetailResponse",
    "UserCareerPathResponse",
    "UserCareerPathUpdate",
    "UserCreate",
    "UserInDB",
    "UserPathAssignmentCreate",
    "UserPathAssignmentDetailResponse",
    "UserPathAssignmentResponse",
    "UserPathAssignmentUpdate",
    "UserResponse",
    "UserStepProgressResponse",
    "UserStepProgressUpdate",
    "UserUpdate",
    "UserWithPermissions",
    "ValidationStatus",
]
