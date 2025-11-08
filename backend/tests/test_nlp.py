"""
Tests for NLP service
"""
import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nlp import (
    text_to_places, 
    haversine_distance, 
    generate_destination_summary, 
    generate_user_comment_response, 
    speak_user_comment_response,
    generate_error_response,
    speak_error_response
)


# Unit Tests for haversine_distance
class TestHaversineDistance:
    """Tests for haversine distance calculation to validate 25km threshold"""

    def test_same_location(self):
        """Test distance between same point is zero"""
        distance = haversine_distance(38.7369, -9.1299, 38.7369, -9.1299)
        print(f"\n📍 Same location test: Distance = {distance:.4f}km")
        assert distance == pytest.approx(0, abs=0.01)

    def test_lisbon_destination_within_25km(self):
        """Test destination in Lisbon is within 25km radius"""
        # User location: Lisbon center (38.7369, -9.1299)
        user_lat, user_lon = 38.7369, -9.1299
        
        # Destination: R. Neves Ferreira, Lisbon (38.7307615, -9.1299053)
        dest_lat, dest_lon = 38.7307615, -9.1299053
        
        distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
        print(f"\n🏙️  Lisbon → R. Neves Ferreira: {distance:.2f}km (expected < 25km)")
        
        # Should be very close (less than 1km)
        assert distance < 25.0
        assert distance == pytest.approx(0.68, abs=0.1)

    def test_fonte_luminosa_within_25km(self):
        """Test Fonte Luminosa is within 25km radius"""
        # User location: Lisbon center (38.7369, -9.1299)
        user_lat, user_lon = 38.7369, -9.1299
        
        # Destination: Fonte Monumental, Lisbon (38.7372982, -9.1303159)
        dest_lat, dest_lon = 38.7372982, -9.1303159
        
        distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
        print(f"\n💧 Lisbon → Fonte Luminosa: {distance:.2f}km (expected < 25km)")
        
        # Should be very close (less than 1km)
        assert distance < 25.0
        assert distance == pytest.approx(0.05, abs=0.1)

    def test_colombo_shopping_within_25km(self):
        """Test Centro Comercial Colombo is within 25km radius"""
        # User location: Lisbon center (38.7369, -9.1299)
        user_lat, user_lon = 38.7369, -9.1299
        
        # Destination: Centro Comercial Colombo, Lisbon (38.7547377, -9.1888962)
        dest_lat, dest_lon = 38.7547377, -9.1888962
        
        distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
        print(f"\n🛍️  Lisbon → Centro Colombo: {distance:.2f}km (expected < 25km)")
        
        # Should be within 25km (approximately 5km)
        assert distance < 25.0
        assert distance == pytest.approx(5.3, abs=0.5)

    def test_far_destination_exceeds_25km(self):
        """Test that distant location exceeds 25km radius"""
        # User location: Lisbon (38.7369, -9.1299)
        user_lat, user_lon = 38.7369, -9.1299
        
        # Destination: Porto (41.1579, -8.6291) - about 272km away
        dest_lat, dest_lon = 41.1579, -8.6291
        
        distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
        print(f"\n❌ Lisbon → Porto: {distance:.2f}km (expected > 25km) ⚠️  TOO FAR!")
        
        # Should exceed 25km (actually ~272km)
        assert distance > 25.0
        assert distance > 250.0

    def test_distance_symmetry(self):
        """Test that distance calculation is symmetric"""
        lat1, lon1 = 38.7369, -9.1299
        lat2, lon2 = 38.7307615, -9.1299053
        
        distance_12 = haversine_distance(lat1, lon1, lat2, lon2)
        distance_21 = haversine_distance(lat2, lon2, lat1, lon1)
        
        print(f"\n🔄 Symmetry test: A→B = {distance_12:.4f}km, B→A = {distance_21:.4f}km")
        
        # Both directions should give same result
        assert distance_12 == pytest.approx(distance_21, abs=0.001)

    def test_valid_destination_within_radius(self):
        """Test multiple valid destinations within 25km radius"""
        user_lat, user_lon = 38.7369, -9.1299  # Lisbon center
        
        destinations = [
            (38.7307615, -9.1299053),  # R. Neves Ferreira
            (38.7372982, -9.1303159),  # Fonte Luminosa
            (38.7547377, -9.1888962),  # Colombo shopping
        ]
        
        print(f"\n✅ Testing multiple destinations within 25km radius:")
        for i, (dest_lat, dest_lon) in enumerate(destinations, 1):
            distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
            status = "✓ OK" if distance < 25.0 else "✗ INVALID"
            print(f"   {i}. Distance: {distance:.2f}km {status}")
            assert distance < 25.0, f"Destination at ({dest_lat}, {dest_lon}) is {distance}km away, exceeds 25km limit"


# Tests for destination summary generation
class TestDestinationSummary:
    """Tests for generating destination confirmations with distance details"""
    
    def test_summary_with_short_distance(self):
        """Test summary generation with a short distance (< 1km)"""
        destination_address = "R. Neves Ferreira, Lisbon, Portugal"
        destination_coords = {"latitude": 38.7307615, "longitude": -9.1299053}
        user_coords = {"latitude": 38.7369, "longitude": -9.1299}
        
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        print(f"\n📍 Short distance summary:\n{summary}")
        
        # Check that summary contains expected elements
        assert "R. Neves Ferreira" in summary
        assert "meters" in summary.lower()
        assert "confirm" in summary.lower()
    
    def test_summary_with_medium_distance(self):
        """Test summary generation with a medium distance (5-10km)"""
        destination_address = "Centro Comercial Colombo, Lisbon, Portugal"
        destination_coords = {"latitude": 38.7547377, "longitude": -9.1888962}
        user_coords = {"latitude": 38.7369, "longitude": -9.1299}
        
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        print(f"\n🛍️  Medium distance summary:\n{summary}")
        
        # Check that summary contains expected elements
        assert "Centro Comercial Colombo" in summary
        assert "kilometers" in summary.lower()
        assert "5" in summary  # Should mention ~5km distance
    
    def test_summary_with_far_distance(self):
        """Test summary generation with a far distance (> 25km)"""
        destination_address = "Porto, Portugal"
        destination_coords = {"latitude": 41.1579, "longitude": -8.6291}
        user_coords = {"latitude": 38.7369, "longitude": -9.1299}
        
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        print(f"\n❌ Far distance summary:\n{summary}")
        
        # Check that summary contains expected elements
        assert "Porto" in summary
        assert "kilometers" in summary.lower()
        assert "27" in summary  # Should mention ~273km distance
    
    def test_summary_without_user_coords(self):
        """Test summary generation when user coordinates are missing"""
        destination_address = "R. Neves Ferreira, Lisbon, Portugal"
        destination_coords = {"latitude": 38.7307615, "longitude": -9.1299053}
        user_coords = None  # No user coordinates
        
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        print(f"\n⚠️  No user coords summary:\n{summary}")
        
        # Should just mention the destination
        assert "R. Neves Ferreira" in summary
        assert "Your destination is" in summary
    
    def test_summary_contains_confirmation_message(self):
        """Test that summary always asks for confirmation"""
        destination_address = "Fonte Luminosa, Lisbon, Portugal"
        destination_coords = {"latitude": 38.7372982, "longitude": -9.1303159}
        user_coords = {"latitude": 38.7369, "longitude": -9.1299}
        
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        
        # Should contain a confirmation request
        assert "confirm" in summary.lower() or "proceed" in summary.lower()
        print(f"\n✅ Confirmation message included in summary")


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


# Tests for user comment processing
class TestUserCommentProcessing:
    """Tests for generating responses to user comments and feedback"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_generate_response_destination_too_far(self):
        """Test response when user says destination is too far"""
        response = generate_user_comment_response(
            "The destination seems too far",
            context={
                "current_destination": "Porto",
                "current_distance": 273
            }
        )
        print(f"\n💬 Response to 'destination too far':\n{response}")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "i" in response.lower() or "understand" in response.lower() or "porto" in response.lower()
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_generate_response_change_destination(self):
        """Test response when user wants to change destination"""
        response = generate_user_comment_response(
            "Can I change my destination?"
        )
        print(f"\n💬 Response to 'change destination':\n{response}")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "destination" in response.lower() or "yes" in response.lower() or "change" in response.lower()
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_generate_response_with_route_context(self):
        """Test response with route navigation context"""
        response = generate_user_comment_response(
            "What's next?",
            context={
                "current_destination": "Centro Comercial Colombo, Lisbon",
                "current_distance": 5.5,
                "current_route_step": "Turn left onto R. Neves Ferreira"
            }
        )
        print(f"\n💬 Response to 'What's next?' with context:\n{response}")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_generate_response_feedback(self):
        """Test response to user feedback"""
        response = generate_user_comment_response(
            "This is very helpful, thank you"
        )
        print(f"\n💬 Response to positive feedback:\n{response}")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_speak_user_comment_response(self):
        """Test generating and speaking user comment response"""
        result = speak_user_comment_response(
            "Is this the right way?",
            context={
                "current_destination": "R. Neves Ferreira, Lisbon",
                "current_distance": 0.7
            }
        )
        print(f"\n🎵 Generated response text:\n{result['response_text']}")
        print(f"🎵 Audio file: {result['audio_path']}")
        
        assert isinstance(result, dict)
        assert "response_text" in result
        assert "audio_path" in result
        assert result["response_text"]
        assert result["audio_path"]
        assert ".wav" in result["audio_path"]
        print(f"✅ Audio file created successfully")


# Tests for error response handling
class TestErrorResponses:
    """Tests for generating user-friendly error messages and audio"""
    
    def test_generate_error_distance_exceeded(self):
        """Test error message when distance exceeds limit"""
        message = generate_error_response("distance_exceeded")
        print(f"\n🚫 Distance exceeded error:\n{message}")
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert "too far" in message.lower() or "exceeds" in message.lower()
        assert "50" in message  # Should mention 50km limit
        assert "kilometers" in message.lower() or "km" in message.lower()
    
    def test_generate_error_distance_exceeded_with_details(self):
        """Test error message with specific distance details"""
        error_details = "Route is 273 kilometers away, maximum is 50 kilometers"
        message = generate_error_response("distance_exceeded", error_details)
        print(f"\n🚫 Distance exceeded with details:\n{message}")
        
        assert isinstance(message, str)
        assert "273" in message  # Should include the specific distance
        assert "50" in message   # Should include the limit
    
    def test_generate_error_invalid_destination(self):
        """Test error message for invalid destination"""
        message = generate_error_response("invalid_destination")
        print(f"\n🚫 Invalid destination error:\n{message}")
        
        assert isinstance(message, str)
        assert "destination" in message.lower()
        assert "not find" in message.lower() or "could not" in message.lower()
    
    def test_generate_error_no_route_found(self):
        """Test error message when no route exists"""
        message = generate_error_response("no_route_found")
        print(f"\n🚫 No route found error:\n{message}")
        
        assert isinstance(message, str)
        assert "route" in message.lower()
        assert "not find" in message.lower() or "could not" in message.lower()
    
    def test_generate_error_routing_service_error(self):
        """Test error message for routing service failure"""
        message = generate_error_response("routing_service_error")
        print(f"\n🚫 Routing service error:\n{message}")
        
        assert isinstance(message, str)
        assert "unavailable" in message.lower() or "failed" in message.lower() or "temporarily" in message.lower()
    
    def test_generate_error_geocoding_error(self):
        """Test error message for geocoding failure"""
        message = generate_error_response("geocoding_error")
        print(f"\n🚫 Geocoding error:\n{message}")
        
        assert isinstance(message, str)
        assert "coordinates" in message.lower() or "destination" in message.lower()
    
    def test_generate_error_unknown(self):
        """Test error message for unknown error"""
        message = generate_error_response("unknown")
        print(f"\n🚫 Unknown error:\n{message}")
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert "something went wrong" in message.lower() or "sorry" in message.lower()
    
    def test_generate_error_with_invalid_type(self):
        """Test error message with invalid error type"""
        message = generate_error_response("invalid_error_type")
        print(f"\n🚫 Invalid error type (should default to unknown):\n{message}")
        
        # Should fall back to unknown error message
        assert isinstance(message, str)
        assert len(message) > 0
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_speak_error_distance_exceeded(self):
        """Test generating and speaking distance exceeded error"""
        result = speak_error_response(
            "distance_exceeded",
            "Route is 273 km away, maximum is 50 km"
        )
        print(f"\n🎵 Generated error message:\n{result['error_message']}")
        print(f"🎵 Error type: {result['error_type']}")
        print(f"🎵 Audio file: {result['audio_path']}")
        
        assert isinstance(result, dict)
        assert "error_message" in result
        assert "audio_path" in result
        assert "error_type" in result
        assert result["error_type"] == "distance_exceeded"
        assert result["error_message"]
        assert result["audio_path"]
        assert ".wav" in result["audio_path"]
        print(f"✅ Error audio file created successfully")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_speak_error_routing_service_error(self):
        """Test generating and speaking routing service error"""
        result = speak_error_response(
            "routing_service_error",
            "OSRM API timeout"
        )
        print(f"\n🎵 Routing service error audio generated")
        print(f"🎵 Message: {result['error_message'][:50]}...")
        
        assert isinstance(result, dict)
        assert "error_message" in result
        assert "audio_path" in result
        assert "error_type" in result
        assert result["error_type"] == "routing_service_error"
        print(f"✅ Routing error audio file created successfully")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_speak_error_invalid_destination(self):
        """Test generating and speaking invalid destination error"""
        result = speak_error_response(
            "invalid_destination",
            "Could not find 'Xyztown'"
        )
        print(f"\n🎵 Invalid destination error audio generated")
        print(f"🎵 Message: {result['error_message'][:50]}...")
        
        assert isinstance(result, dict)
        assert "error_message" in result
        assert "audio_path" in result
        assert "error_type" in result
        print(f"✅ Invalid destination error audio file created successfully")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_speak_error_no_details(self):
        """Test generating error audio without additional details"""
        result = speak_error_response("unknown")
        print(f"\n🎵 Unknown error audio generated (no details)")
        print(f"🎵 Message: {result['error_message'][:50]}...")
        
        assert isinstance(result, dict)
        assert result["error_message"]
        assert result["audio_path"]
        print(f"✅ Unknown error audio file created successfully")

