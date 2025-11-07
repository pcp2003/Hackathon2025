"""
Health check endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    return HealthResponse(status="healthy", version="0.1.0")
