from pydantic import Field, field_validator

from upskills.api.schemas import BaseSchema, UserResponse


class ManagerRef(BaseSchema):
    user_id: int


class TeamCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    manager: ManagerRef


class TeamUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    manager: ManagerRef | None = None


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
    manager: UserResponse | None = None


class TeamListResponse(BaseSchema):
    team_id: int
    name: str
    member_count: int = Field(default=0)
    manager: UserResponse | None = None

    @field_validator("member_count", mode="before")
    @classmethod
    def extract_member_count(cls, v, info) -> int:
        if v is not None:
            return v
        members = info.data.get("members", [])
        return len(members) if members else 0


class TeamWithMembersResponse(BaseSchema):
    team_id: int
    name: str
    manager: UserResponse | None = None
    members: list[UserResponse] = Field(default_factory=list)

    @field_validator("members", mode="before")
    @classmethod
    def convert_members(cls, v):
        if not v:
            return []
        # Members are now User objects, not TeamMembership
        return v



