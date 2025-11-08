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
        assert isinstance(result["destination_address"], str)
        assert len(result["destination_address"]) > 0
        # Check that the address contains the key part we're looking for
        assert "Neves Ferreira" in result["destination_address"]
        # Should include city/country for OSRM geocoding
        assert any(city in result["destination_address"].lower() for city in ["lisbon", "portugal", "lisboa"])

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
        assert isinstance(result["destination_address"], str)
        # Should recognize Fonte Luminosa
        assert "fonte" in result["destination_address"].lower() or "luminosa" in result["destination_address"].lower()
        # Should include city/country for OSRM geocoding
        assert any(city in result["destination_address"].lower() for city in ["lisbon", "portugal", "lisboa"])

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_real_api_response_format(self):
        """Test that real API returns proper OSRM-compatible address format"""
        transcription_data = {
            "text": "Quero ir para o Centro Comercial Colombo",
            "confidence": 0.92
        }

        result = text_to_places(transcription_data)

        # Verify response is a dictionary with destination_address
        assert isinstance(result, dict)
        assert "destination_address" in result
        assert isinstance(result["destination_address"], str)
        assert len(result["destination_address"]) > 0
        # Address should be suitable for OSRM geocoding (include location details)
        assert any(part in result["destination_address"].lower() for part in ["colombo", "lisbon", "portugal", "lisboa"])
