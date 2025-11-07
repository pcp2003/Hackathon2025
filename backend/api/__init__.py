"""
API endpoints package
"""
from .health import router as health_router
from .navigation import router as navigation_router

__all__ = ["health_router", "navigation_router"]
