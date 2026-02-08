from pydantic import Field, field_validator

from upskills.api.schemas import BaseSchema, UserResponse


class TeamCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    manager_user_id: int


class TeamUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    manager_user_id: int | None = None


class TeamMemberAdd(BaseSchema):
    user_id: int


class TeamMemberBulkAdd(BaseSchema):
    user_ids: list[int]


class TeamMemberResponse(BaseSchema):
    user_id: int
    full_name: str | None = None
    email: str | None = None


class TeamResponse(BaseSchema):
    team_id: int
    name: str
    manager_user_id: int = Field(default=0)
    manager: UserResponse | None = None

    @field_validator("manager_user_id", mode="before")
    @classmethod
    def extract_manager_user_id(cls, v: int | dict | None, info) -> int:
        if isinstance(v, dict):
            return v.get("user_id", 0)
        if v is None and info.data.get("manager"):
            manager = info.data["manager"]
            if isinstance(manager, dict):
                return manager.get("user_id", 0)
            if hasattr(manager, "user_id"):
                return manager.user_id
        return v or 0


class TeamListResponse(BaseSchema):
    team_id: int
    name: str
    member_count: int = Field(default=0)
    manager_name: str = Field(default="")
    manager: UserResponse | None = None

    @field_validator("member_count", mode="before")
    @classmethod
    def extract_member_count(cls, v, info) -> int:
        if v is not None:
            return v
        members = info.data.get("members", [])
        return len(members) if members else 0

    @field_validator("manager_name", mode="before")
    @classmethod
    def extract_manager_name(cls, v: str | None, info) -> str:
        if v:
            return v
        manager = info.data.get("manager")
        if manager:
            if isinstance(manager, dict):
                return manager.get("full_name", "")
            if hasattr(manager, "full_name"):
                return manager.full_name or ""
        return ""


class TeamWithMembersResponse(BaseSchema):
    team_id: int
    name: str
    manager_user_id: int = Field(default=0)
    manager: UserResponse | None = None
    members: list[UserResponse] = Field(default_factory=list)

    @field_validator("manager_user_id", mode="before")
    @classmethod
    def extract_manager_user_id(cls, v: int | dict | None, info) -> int:
        if isinstance(v, dict):
            return v.get("user_id", 0)
        if v is None and info.data.get("manager"):
            manager = info.data["manager"]
            if isinstance(manager, dict):
                return manager.get("user_id", 0)
            if hasattr(manager, "user_id"):
                return manager.user_id
        return v or 0

    @field_validator("members", mode="before")
    @classmethod
    def convert_members(cls, v):
        if not v:
            return []
        # Members are now User objects, not TeamMembership
        return v


__all__ = [
    "TeamCreate",
    "TeamListResponse",
    "TeamMemberAdd",
    "TeamMemberBulkAdd",
    "TeamMemberResponse",
    "TeamResponse",
    "TeamUpdate",
    "TeamWithMembersResponse",
]
