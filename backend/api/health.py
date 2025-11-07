"""
Health check endpoints
"""
from fastapi import APIRouter
from schemas.health import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    return HealthResponse(status="healthy", version="0.1.0")
