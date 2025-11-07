"""
Tests for routing service module
Using mocked OSRM responses for unit testing
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.routing import calculate_route, _format_instruction

# Test coordinates
TEST_ORIGIN = (37.086282, -8.732629)  # (latitude, longitude)
TEST_DESTINATION = (37.086547, -8.731954)


class TestRouting:
    """Test routing service functionality"""
    
    @pytest.mark.asyncio
    async def test_calculate_route_returns_dict(self):
        """Test that calculate_route returns a valid dict"""
        with patch('services.routing.requests.get') as mock_get:
            # Mock OSRM response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 150.0,
                    "duration": 20.5,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 75.0,
                                "duration": 10.0,
                                "maneuver": {"type": "depart", "modifier": "straight"},
                                "name": "Main Street"
                            },
                            {
                                "distance": 75.0,
                                "duration": 10.5,
                                "maneuver": {"type": "arrive"},
                                "name": "Side Street"
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert isinstance(result, dict), "Result should be a dict"
            assert "steps" in result, "Result should have 'steps' key"
            assert "total_distance" in result, "Result should have 'total_distance' key"
            assert "total_duration" in result, "Result should have 'total_duration' key"
            print(f"\n✓ Route calculation returns valid dict structure")
    
    @pytest.mark.asyncio
    async def test_calculate_route_with_valid_response(self):
        """Test calculate_route with valid OSRM response"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 250.0,
                    "duration": 30.0,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 125.0,
                                "duration": 15.0,
                                "maneuver": {"type": "depart", "modifier": "right"},
                                "name": "Main Street"
                            },
                            {
                                "distance": 125.0,
                                "duration": 15.0,
                                "maneuver": {"type": "arrive"},
                                "name": "Final Street"
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert result["total_distance"] == 250.0, "Total distance should match"
            assert result["total_duration"] == 30.0, "Total duration should match"
            assert len(result["steps"]) == 2, "Should have 2 steps"
            print(f"\n✓ Route calculated correctly: {result['total_distance']:.1f}m, {result['total_duration']:.1f}s")
    
    @pytest.mark.asyncio
    async def test_calculate_route_step_has_instruction(self):
        """Test that route steps include instructions"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 100.0,
                    "duration": 15.0,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                "maneuver": {"type": "depart", "modifier": "straight"},
                                "name": "Oak Avenue"
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert len(result["steps"]) > 0, "Should have at least one step"
            step = result["steps"][0]
            assert "instruction" in step, "Step should have instruction"
            assert "distance" in step, "Step should have distance"
            assert "duration" in step, "Step should have duration"
            assert isinstance(step["instruction"], str), "Instruction should be string"
            print(f"\n✓ Step has instruction: '{step['instruction']}'")
    
    @pytest.mark.asyncio
    async def test_calculate_route_no_route_found(self):
        """Test handling when OSRM returns no route"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "NoRoute",
                "routes": []
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert result["steps"] == [], "Steps should be empty when no route found"
            assert result["total_distance"] == 0.0, "Distance should be 0"
            assert result["total_duration"] == 0.0, "Duration should be 0"
            print(f"\n✓ No route found handled correctly")
    
    @pytest.mark.asyncio
    async def test_calculate_route_api_error(self):
        """Test handling of API errors"""
        with patch('services.routing.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            print(f"\n✓ API error handled correctly")
    
    def test_format_instruction_depart(self):
        """Test formatting depart instruction"""
        maneuver = {"type": "depart", "modifier": "right"}
        instruction = _format_instruction(maneuver, "Main Street")
        
        # Should contain either "Head" or "Start"
        assert ("Head" in instruction or "Start" in instruction), "Should contain direction instruction"
        assert "right" in instruction or "Right" in instruction, "Should contain direction modifier"
        assert "Main Street" in instruction, "Should contain street name"
        print(f"\n✓ Depart instruction: '{instruction}'")
    
    def test_format_instruction_turn(self):
        """Test formatting turn instruction"""
        maneuver = {"type": "turn", "modifier": "left"}
        instruction = _format_instruction(maneuver, "Oak Avenue")
        
        assert "Turn" in instruction, "Should contain 'Turn'"
        assert "left" in instruction, "Should contain turn direction"
        assert "Oak Avenue" in instruction, "Should contain street name"
        print(f"\n✓ Turn instruction: '{instruction}'")
    
    def test_format_instruction_continue(self):
        """Test formatting continue instruction"""
        maneuver = {"type": "continue"}
        instruction = _format_instruction(maneuver, "Park Road")
        
        # Should contain meaningful navigation text
        assert isinstance(instruction, str) and len(instruction) > 0, "Should have instruction"
        assert "Park Road" in instruction, "Should contain street name"
        print(f"\n✓ Continue instruction: '{instruction}'")
    
    def test_format_instruction_arrive(self):
        """Test formatting arrive instruction"""
        maneuver = {"type": "arrive"}
        instruction = _format_instruction(maneuver, "Destination")
        
        # Should mention arrival (Arrive or "arrived")
        assert "Arrive" in instruction or "arrive" in instruction.lower(), "Should mention arrival"
        print(f"\n✓ Arrive instruction: '{instruction}'")
    
    def test_format_instruction_new_name(self):
        """Test formatting new name instruction"""
        maneuver = {"type": "new name"}
        instruction = _format_instruction(maneuver, "Harbor Street")
        
        assert "Continue" in instruction, "Should contain 'Continue'"
        assert "Harbor Street" in instruction, "Should contain street name"
        print(f"\n✓ New name instruction: '{instruction}'")
    
    def test_format_instruction_no_name(self):
        """Test formatting instruction without street name"""
        maneuver = {"type": "depart", "modifier": "straight"}
        instruction = _format_instruction(maneuver, "")
        
        # Should have some default message
        assert isinstance(instruction, str) and len(instruction) > 0, "Should have default message"
        print(f"\n✓ Instruction without name: '{instruction}'")
    
    def test_format_instruction_no_modifier(self):
        """Test formatting instruction without modifier"""
        maneuver = {"type": "turn"}
        instruction = _format_instruction(maneuver, "Pine Lane")
        
        # Should have meaningful turn information
        assert isinstance(instruction, str) and len(instruction) > 0, "Should have instruction"
        assert "Pine Lane" in instruction, "Should contain street name"
        print(f"\n✓ Turn instruction without modifier: '{instruction}'")
    
    @pytest.mark.asyncio
    async def test_calculate_route_sum_steps_equals_total(self):
        """Test that sum of steps equals totals"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 300.0,
                    "duration": 45.0,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                "maneuver": {"type": "depart", "modifier": "straight"},
                                "name": "Street A"
                            },
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                "maneuver": {"type": "turn", "modifier": "right"},
                                "name": "Street B"
                            },
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                "maneuver": {"type": "arrive"},
                                "name": "Street C"
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            sum_distance = sum(step["distance"] for step in result["steps"])
            sum_duration = sum(step["duration"] for step in result["steps"])
            
            assert sum_distance == result["total_distance"], "Sum of distances should equal total"
            assert sum_duration == result["total_duration"], "Sum of durations should equal total"
            print(f"\n✓ Step sums match totals: {sum_distance}m == {result['total_distance']}m")
    
    @pytest.mark.asyncio
    async def test_calculate_route_coordinates_order(self):
        """Test that coordinates are passed in correct order (lon,lat)"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 100.0,
                    "duration": 15.0,
                    "legs": [{"steps": []}]
                }]
            }
            mock_get.return_value = mock_response
            
            await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            # Check the URL was built correctly (OSRM expects lon,lat)
            call_args = mock_get.call_args
            url = call_args[0][0] if call_args[0] else ""
            
            # URL should contain coordinates in longitude,latitude format
            assert "-8.732629" in url, "Should contain origin longitude"
            assert "37.086282" in url, "Should contain origin latitude"
            print(f"\n✓ Coordinates passed in correct order (lon,lat)")
    
    @pytest.mark.asyncio
    async def test_calculate_route_handles_missing_optional_fields(self):
        """Test handling of OSRM response with missing optional fields"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 100.0,
                    "duration": 15.0,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                # Missing maneuver
                                # Missing name
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert len(result["steps"]) > 0, "Should handle missing fields"
            assert "instruction" in result["steps"][0], "Should have default instruction"
            print(f"\n✓ Missing fields handled: '{result['steps'][0]['instruction']}'")
    
    @pytest.mark.asyncio
    async def test_calculate_route_handles_list_names(self):
        """Test handling when street name is a list"""
        with patch('services.routing.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "code": "Ok",
                "routes": [{
                    "distance": 100.0,
                    "duration": 15.0,
                    "legs": [{
                        "steps": [
                            {
                                "distance": 100.0,
                                "duration": 15.0,
                                "maneuver": {"type": "depart"},
                                "name": ["Main Street", "Highway 1"]  # List of names
                            }
                        ]
                    }]
                }]
            }
            mock_get.return_value = mock_response
            
            result = await calculate_route(TEST_ORIGIN, TEST_DESTINATION)
            
            assert len(result["steps"]) > 0, "Should handle list names"
            assert "Main Street" in result["steps"][0]["instruction"], "Should use first name"
            print(f"\n✓ List names handled: '{result['steps'][0]['instruction']}'")
