"""Base Pydantic models and utilities."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Base model for all domain models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""

    created_at: datetime


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
