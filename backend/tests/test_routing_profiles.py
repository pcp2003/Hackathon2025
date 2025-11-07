"""
Tests to validate if OSRM servers properly differentiate between profiles (foot, car, bike)
Using OpenStreetMap's pre-processed OSRM servers
"""
import pytest
import sys
from pathlib import Path
import requests
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

# Test coordinates
TEST_ORIGIN = (-8.732629, 37.086282)  # (longitude, latitude)
TEST_DESTINATION = (-8.731954, 37.086547)

# OSRM servers from OpenStreetMap - pre-processed for different profiles
OSRM_SERVERS = {
    "foot": "https://routing.openstreetmap.de/routed-foot/route/v1/foot",
    "bike": "https://routing.openstreetmap.de/routed-bike/route/v1/bike",
    "car": "https://routing.openstreetmap.de/routed-car/route/v1/car"
}


def get_osrm_route(profile: str, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
    """
    Get route from OSRM with specific profile
    
    Args:
        profile: "foot", "car", or "bike"
        origin: (longitude, latitude)
        destination: (longitude, latitude)
        
    Returns:
        dict with route data
    """
    origin_lon, origin_lat = origin
    dest_lon, dest_lat = destination
    
    coordinates = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    
    # Get the appropriate OSRM server for this profile
    osrm_base_url = OSRM_SERVERS.get(profile)
    if not osrm_base_url:
        return None
    
    url = f"{osrm_base_url}/{coordinates}"
    
    params = {
        "overview": "false",
        "steps": "true",
        "geometries": "geojson"
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if data.get("code") != "Ok" or not data.get("routes"):
        return None
    
    route = data["routes"][0]
    leg = route["legs"][0]
    
    return {
        "profile": profile,
        "distance": route.get("distance", 0.0),
        "duration": route.get("duration", 0.0),
        "num_steps": len(leg.get("steps", [])),
        "steps": leg.get("steps", [])
    }


class TestOSRMProfileDifferences:
    """Test if OSRM returns different routes for different profiles"""
    
    @pytest.mark.asyncio
    def test_foot_profile_returns_data(self):
        """Test that foot profile returns valid data"""
        result = get_osrm_route("foot", TEST_ORIGIN, TEST_DESTINATION)
        assert result is not None, "OSRM should return a route for foot profile"
        assert result["distance"] > 0, "Distance should be > 0"
        assert result["duration"] > 0, "Duration should be > 0"
        print(f"\n✓ FOOT Profile: {result['distance']:.1f}m, {result['duration']:.1f}s")
    
    @pytest.mark.asyncio
    def test_car_profile_returns_data(self):
        """Test that car profile returns valid data"""
        result = get_osrm_route("car", TEST_ORIGIN, TEST_DESTINATION)
        assert result is not None, "OSRM should return a route for car profile"
        assert result["distance"] > 0, "Distance should be > 0"
        assert result["duration"] > 0, "Duration should be > 0"
        print(f"\n✓ CAR Profile: {result['distance']:.1f}m, {result['duration']:.1f}s")
    
    @pytest.mark.asyncio
    def test_bike_profile_returns_data(self):
        """Test that bike profile returns valid data"""
        result = get_osrm_route("bike", TEST_ORIGIN, TEST_DESTINATION)
        assert result is not None, "OSRM should return a route for bike profile"
        assert result["distance"] > 0, "Distance should be > 0"
        assert result["duration"] > 0, "Duration should be > 0"
        print(f"\n✓ BIKE Profile: {result['distance']:.1f}m, {result['duration']:.1f}s")
    
    @pytest.mark.asyncio
    def test_profiles_return_different_distances(self):
        """Test if different profiles return DIFFERENT distances"""
        foot_result = get_osrm_route("foot", TEST_ORIGIN, TEST_DESTINATION)
        car_result = get_osrm_route("car", TEST_ORIGIN, TEST_DESTINATION)
        bike_result = get_osrm_route("bike", TEST_ORIGIN, TEST_DESTINATION)
        
        print(f"\n📊 Distance Comparison:")
        print(f"  FOOT: {foot_result['distance']:.1f}m")
        print(f"  CAR:  {car_result['distance']:.1f}m")
        print(f"  BIKE: {bike_result['distance']:.1f}m")
        
        # Check if distances are different
        distances_are_different = (
            foot_result['distance'] != car_result['distance'] or
            car_result['distance'] != bike_result['distance'] or
            foot_result['distance'] != bike_result['distance']
        )
        
        if distances_are_different:
            print(f"\n✓ PROFILES RETURN DIFFERENT DISTANCES")
        else:
            print(f"\n✗ WARNING: ALL PROFILES RETURN SAME DISTANCE - OSRM might be treating them equally!")
        
        assert distances_are_different, "Profiles should return different distances"
    
    @pytest.mark.asyncio
    def test_profiles_return_different_durations(self):
        """Test if different profiles return DIFFERENT durations"""
        foot_result = get_osrm_route("foot", TEST_ORIGIN, TEST_DESTINATION)
        car_result = get_osrm_route("car", TEST_ORIGIN, TEST_DESTINATION)
        bike_result = get_osrm_route("bike", TEST_ORIGIN, TEST_DESTINATION)
        
        print(f"\n⏱️  Duration Comparison:")
        print(f"  FOOT: {foot_result['duration']:.1f}s")
        print(f"  CAR:  {car_result['duration']:.1f}s")
        print(f"  BIKE: {bike_result['duration']:.1f}s")
        
        # Check if durations are different
        durations_are_different = (
            foot_result['duration'] != car_result['duration'] or
            car_result['duration'] != bike_result['duration'] or
            foot_result['duration'] != bike_result['duration']
        )
        
        if durations_are_different:
            print(f"\n✓ PROFILES RETURN DIFFERENT DURATIONS")
        else:
            print(f"\n✗ WARNING: ALL PROFILES RETURN SAME DURATION - OSRM might be treating them equally!")
        
        assert durations_are_different, "Profiles should return different durations"
    
    @pytest.mark.asyncio
    def test_car_should_be_faster_than_foot(self):
        """Test that car routes are faster than foot routes"""
        foot_result = get_osrm_route("foot", TEST_ORIGIN, TEST_DESTINATION)
        car_result = get_osrm_route("car", TEST_ORIGIN, TEST_DESTINATION)
        
        print(f"\n🚗 vs 🚶 Speed Test:")
        print(f"  FOOT duration: {foot_result['duration']:.1f}s")
        print(f"  CAR duration:  {car_result['duration']:.1f}s")
        print(f"  Ratio (Car/Foot): {car_result['duration']/foot_result['duration']:.2f}x")
        
        if car_result['duration'] < foot_result['duration']:
            print(f"✓ Car is faster than foot (as expected)")
        else:
            print(f"✗ Car is NOT faster than foot - something is wrong!")
        
        assert car_result['duration'] < foot_result['duration'], \
            "Car should be faster than walking"
    
    @pytest.mark.asyncio
    def test_compare_all_three_profiles(self):
        """Comprehensive comparison of all three profiles"""
        foot = get_osrm_route("foot", TEST_ORIGIN, TEST_DESTINATION)
        car = get_osrm_route("car", TEST_ORIGIN, TEST_DESTINATION)
        bike = get_osrm_route("bike", TEST_ORIGIN, TEST_DESTINATION)
        
        print(f"\n" + "="*60)
        print(f"COMPREHENSIVE PROFILE COMPARISON")
        print(f"="*60)
        print(f"\nCoordinates: {TEST_ORIGIN} → {TEST_DESTINATION}")
        print(f"\n{'Profile':<10} {'Distance':<15} {'Duration':<15} {'Steps':<10}")
        print(f"{'-'*50}")
        print(f"{'FOOT':<10} {foot['distance']:<15.1f} {foot['duration']:<15.1f} {foot['num_steps']:<10}")
        print(f"{'CAR':<10} {car['distance']:<15.1f} {car['duration']:<15.1f} {car['num_steps']:<10}")
        print(f"{'BIKE':<10} {bike['distance']:<15.1f} {bike['duration']:<15.1f} {bike['num_steps']:<10}")
        print(f"{'-'*50}")
        
        # Analysis
        all_same_distance = (foot['distance'] == car['distance'] == bike['distance'])
        all_same_duration = (foot['duration'] == car['duration'] == bike['duration'])
        
        print(f"\nAnalysis:")
        print(f"  Same distances: {all_same_distance}")
        print(f"  Same durations: {all_same_duration}")
        
        if all_same_distance and all_same_duration:
            print(f"\n⚠️  CONCLUSION: OSRM IS TREATING ALL PROFILES THE SAME!")
            print(f"   The API might not support different profiles or is returning")
            print(f"   identical routes regardless of transportation mode.")
        else:
            print(f"\n✓ CONCLUSION: OSRM returns different routes for different profiles")
        
        print(f"="*60 + "\n")
