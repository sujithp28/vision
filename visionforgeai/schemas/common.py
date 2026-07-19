"""Common Pydantic schemas used across the application."""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "forbid",
        "json_encoders": {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)},
    }


class ErrorResponse(BaseSchema):
    """Standard error response model."""

    error: str = Field(
        ..., description="Error code or type", examples=["InternalServerError"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["An unexpected error occurred"],
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details (usually hidden in production)",
        examples=["Connection timeout to external service"],
    )
    path: str = Field(
        ...,
        description="The URL path where the error occurred",
        examples=["/api/v1/llm/generate"],
    )
    status_code: int = Field(
        ..., description="HTTP status code", examples=[500], ge=100, le=599
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the error occurred"
    )


class SuccessResponse(BaseSchema):
    """Standard success response model."""

    success: bool = Field(True, description="Indicates if the request was successful")
    message: str = Field(
        ..., description="Status message", examples=["Operation completed successfully"]
    )
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
