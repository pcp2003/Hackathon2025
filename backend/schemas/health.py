"""
Health check schemas
"""
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status", example="healthy")
    version: str = Field(..., description="API version", example="0.1.0")
