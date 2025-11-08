# """
# Tests for navigation endpoints
# """
# import pytest
# from fastapi.testclient import TestClient
# import sys
# from pathlib import Path
# from unittest.mock import patch, MagicMock

# sys.path.insert(0, str(Path(__file__).parent.parent))

# from main import app

# client = TestClient(app)


# @pytest.fixture
# def mock_elevenlabs():
#     """Mock ElevenLabs para testes de TTS."""
#     with patch('services.text_to_speech.ElevenLabs') as mock_client_class:
#         mock_client = MagicMock()
#         mock_client_class.return_value = mock_client
#         mock_client.text_to_speech.convert.return_value = iter([b'audio_chunk_1', b'audio_chunk_2'])
#         yield mock_client_class


# def test_transcribe_endpoint_exists():
#     """Test that transcribe endpoint is available"""
#     # Note: This will fail without actual audio, but verifies endpoint exists
#     # In real scenario, would pass valid audio file
#     # pass


# def test_analyze_destination_with_text():
#     """Test destination analysis endpoint"""
#     # This endpoint requires form data
#     response = client.post(
#         "/api/analyze",
#         data={"text": "I want to go to Times Square"}
#     )
#     # Even with placeholder, should return 200
#     assert response.status_code == 200
#     data = response.json()
#     assert "destination" in data
#     assert "latitude" in data
#     assert "longitude" in data


# def test_route_endpoint_with_coordinates():
#     """Test route calculation endpoint"""
#     response = client.post(
#         "/api/route",
#         data={
#             "origin_lat": 40.7128,
#             "origin_lon": -74.0060,
#             "dest_lat": 34.0522,
#             "dest_lon": -118.2437,
#         }
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "steps" in data
#     assert "total_distance" in data
#     assert "total_duration" in data
#     assert len(data["steps"]) > 0


# def test_update_location_endpoint():
#     """Test location update endpoint"""
#     response = client.post(
#         "/api/update-location",
#         data={
#             "latitude": 40.7128,
#             "longitude": -74.0060,
#             "destination_lat": 34.0522,
#             "destination_lon": -118.2437,
#         }
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "on_route" in data
#     assert "needs_recalculation" in data
#     assert "message" in data

