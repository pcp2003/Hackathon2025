"""
Tests for health check endpoint
"""
import asyncio

from api.health import health_check


def test_health_check():
    """Directly call the health_check function and verify its fields."""
    result = asyncio.run(health_check())
    # health_check returns a HealthResponse Pydantic model
    assert result.status == "healthy"
    assert hasattr(result, "version")


def test_health_check_response_format():
    result = asyncio.run(health_check())
    assert isinstance(result.status, str)
    assert isinstance(result.version, str)
