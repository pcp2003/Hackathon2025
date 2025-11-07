"""
Helper utilities for NaviAcess backend
"""
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers using Haversine formula
    
    Args:
        lat1, lon1: First coordinate (latitude, longitude)
        lat2, lon2: Second coordinate (latitude, longitude)
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def is_off_route(current: tuple, route_start: tuple, route_end: tuple, threshold: float = 0.1) -> bool:
    """
    Check if user is off route using distance threshold
    
    Args:
        current: Current coordinates (lat, lon)
        route_start: Route start coordinates (lat, lon)
        route_end: Route end coordinates (lat, lon)
        threshold: Distance threshold in kilometers
        
    Returns:
        True if user is off-route, False otherwise
    """
    # Calculate cross-track distance
    # For now, use simple distance check
    dist = haversine_distance(current[0], current[1], route_end[0], route_end[1])
    return dist > threshold
