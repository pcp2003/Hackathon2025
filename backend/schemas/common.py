"""
Common schemas used across the API
"""
from pydantic import BaseModel, Field
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel):
    """Standard success response wrapper"""
    success: bool = Field(default=True, description="Whether operation was successful")
    data: Optional[dict] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Optional message")
