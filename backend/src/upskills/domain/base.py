"""Base Pydantic models and utilities."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DomainModel(BaseModel):
    """Base model for all domain models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class PaginatedResponse[T](BaseModel):
    """Generic paginated response model."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
    detail: str | None = None
