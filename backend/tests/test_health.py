"""
Tests for health check endpoint
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint returns success"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()

def test_health_check_response_format():
    """Test health check response has correct format"""
    response = client.get("/api/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
