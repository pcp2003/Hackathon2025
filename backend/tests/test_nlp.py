"""
Tests for NLP service
"""
import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nlp import text_to_places


# Integration Tests (use real OpenAI API)
# Only run these if OPENAI_API_KEY is set and you want to test with real API
class TestTextToPlacesIntegration:
    """Integration tests using real OpenAI API"""

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_real_api_simple_address(self):
        """Test with real OpenAI API - simple address"""
        transcription_data = {
            "text": "Leva-me para a R. Neves Ferreira",
            "confidence": 0.95
        }

        result = text_to_places(transcription_data)

        assert "destination_address" in result
        assert "latitude" in result
        assert "longitude" in result
        assert isinstance(result["destination_address"], str)
        assert isinstance(result["latitude"], (int, float))
        assert isinstance(result["longitude"], (int, float))
        assert len(result["destination_address"]) > 0
        # Check that the address contains the key part we're looking for
        assert "R. Neves Ferreira" in result["destination_address"]
        # Allow ~0.01 degree tolerance for coordinates (roughly 1km)
        assert result["latitude"] == pytest.approx(38.73077805628982, abs=0.01)
        assert result["longitude"] == pytest.approx(-9.129930928279666, abs=0.01)

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_real_place(self):
        """Test with real OpenAI API - place name"""
        transcription_data = {
            "text": "Leva-me à Fonte Luminosa",
            "confidence": 0.87
        }

        result = text_to_places(transcription_data)

        assert "destination_address" in result
        assert "latitude" in result
        assert "longitude" in result
        assert isinstance(result["destination_address"], str)
        assert isinstance(result["latitude"], (int, float))
        assert isinstance(result["longitude"], (int, float))
        # Should recognize Fonte Luminosa
        assert "fonte" in result["destination_address"].lower() or "luminosa" in result["destination_address"].lower()
        assert result["latitude"] == pytest.approx(38.73727961098159, abs=0.05)
        assert result["longitude"] == pytest.approx(-9.130489043391634, abs=0.05)

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_real_api_response_format(self):
        """Test that real API returns proper JSON format with coordinates"""
        transcription_data = {
            "text": "Quero ir para o Centro Comercial Colombo",
            "confidence": 0.92
        }

        result = text_to_places(transcription_data)

        # Verify response is a dictionary with all required fields
        assert isinstance(result, dict)
        assert "destination_address" in result
        assert "latitude" in result
        assert "longitude" in result
        assert isinstance(result["destination_address"], str)
        assert isinstance(result["latitude"], (int, float))
        assert isinstance(result["longitude"], (int, float))
        
        # Verify coordinates are in reasonable ranges for Earth
        assert -90 <= result["latitude"] <= 90
        assert -180 <= result["longitude"] <= 180
