"""
Tests for helper utilities
"""
import pytest
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import haversine_distance, is_off_route

def test_haversine_distance_same_point():
    """Test haversine distance between same point is zero"""
    distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
    assert distance == pytest.approx(0, abs=0.01)

def test_haversine_distance_known_points():
    """Test haversine distance with known coordinates"""
    # Distance between NYC (40.7128, -74.0060) and LA (34.0522, -118.2437)
    # Approximately 3943 km
    distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
    assert distance == pytest.approx(3943, abs=50)

def test_is_off_route_on_route():
    """Test is_off_route returns False when user is on route"""
    current = (40.7128, -74.0060)
    route_start = (40.7128, -74.0060)
    route_end = (34.0522, -118.2437)
    
    result = is_off_route(current, route_start, route_end, threshold=100)
    assert result is False

def test_is_off_route_off_route():
    """Test is_off_route returns True when user is far from route"""
    current = (35.0, -119.0)
    route_start = (40.7128, -74.0060)
    route_end = (34.0522, -118.2437)
    
    result = is_off_route(current, route_start, route_end, threshold=0.1)
    assert result is True
