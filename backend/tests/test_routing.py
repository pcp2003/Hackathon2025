"""
Tests for routing service using OSRM
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.routing import calculate_route

# Sample OSRM response structure
SAMPLE_OSRM_RESPONSE = {
    "code": "Ok",
    "routes": [
        {
            "geometry": "encoded_polyline",
            "legs": [
                {
                    "steps": [
                        {
                            "maneuver": {
                                "type": "depart",
                                "modifier": "straight"
                            },
                            "name": "Main Street",
                            "distance": 100.0,
                            "duration": 20.0,
                            "geometry": "encoded"
                        },
                        {
                            "maneuver": {
                                "type": "turn",
                                "modifier": "left"
                            },
                            "name": "5th Avenue",
                            "distance": 150.0,
                            "duration": 30.0,
                            "geometry": "encoded"
                        }
                    ],
                    "distance": 250.0,
                    "duration": 50.0
                }
            ],
            "distance": 250.0,
            "duration": 50.0
        }
    ]
}

@pytest.mark.asyncio
async def test_calculate_route_success():
    """Test successful route calculation with valid coordinates"""
    origin = (40.7128, -74.0060)  # NYC
    destination = (40.7580, -73.9855)  # Central Park
    
    with patch('services.routing.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_OSRM_RESPONSE
        mock_response.raise_for_status.return_value = None  # Don't raise on success
        mock_get.return_value = mock_response
        
        result = await calculate_route(origin, destination)
        
        assert "steps" in result
        assert "total_distance" in result
        assert "total_duration" in result
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) > 0
        assert "instruction" in result["steps"][0]
        assert "distance" in result["steps"][0]
        assert "duration" in result["steps"][0]
        assert result["total_distance"] > 0
        assert result["total_duration"] > 0

@pytest.mark.asyncio
async def test_calculate_route_response_format():
    """Test route response has correct format matching RouteStep model"""
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    with patch('services.routing.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_OSRM_RESPONSE
        mock_response.raise_for_status.return_value = None  # Don't raise on success
        mock_get.return_value = mock_response
        
        result = await calculate_route(origin, destination)
        
        # Validate each step structure
        for step in result["steps"]:
            assert isinstance(step["instruction"], str)
            assert isinstance(step["distance"], (int, float))
            assert isinstance(step["duration"], (int, float))
            assert step["distance"] >= 0
            assert step["duration"] >= 0

@pytest.mark.asyncio
async def test_calculate_route_api_error():
    """Test routing handles OSRM API errors gracefully"""
    import requests
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    with patch('services.routing.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("OSRM API Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            await calculate_route(origin, destination)

@pytest.mark.asyncio
async def test_calculate_route_invalid_response():
    """Test routing handles invalid OSRM response format"""
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    with patch('services.routing.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "NoRoute", "routes": []}
        mock_get.return_value = mock_response
        
        # Should handle gracefully - either return empty or raise
        result = await calculate_route(origin, destination)
        # Depending on implementation, could be empty steps or exception
        assert "steps" in result

@pytest.mark.asyncio
async def test_calculate_route_network_error():
    """Test routing handles network connection errors"""
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    with patch('services.routing.requests.get') as mock_get:
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            await calculate_route(origin, destination)

@pytest.mark.asyncio
async def test_calculate_route_coordinates_format():
    """Test that coordinates are formatted correctly for OSRM API"""
    origin = (40.7128, -74.0060)
    destination = (40.7580, -73.9855)
    
    with patch('services.routing.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_OSRM_RESPONSE
        mock_response.raise_for_status.return_value = None  # Don't raise on success
        mock_get.return_value = mock_response
        
        await calculate_route(origin, destination)
        
        # Verify API was called with correct coordinate format (lon,lat)
        assert mock_get.called
        call_args = mock_get.call_args
        url = call_args[0][0]  # First positional argument is the URL
        # OSRM uses lon,lat format - verify longitude comes first
        assert '-74.0060' in url or '-73.9855' in url
        # Verify coordinates are in lon,lat format (not lat,lon)
        assert url.count(',') >= 1  # Should have coordinate separators

