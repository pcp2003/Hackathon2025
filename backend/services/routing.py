"""
Routing service using OSRM (Open Source Routing Machine)
Optimized for pedestrian navigation - suitable for visually impaired users
Uses pre-processed profile-specific OSRM servers from OpenStreetMap
"""
import logging
import os
import requests
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# OSRM API endpoints - pre-processed for different profiles
# These are free servers maintained by OpenStreetMap Foundation
OSRM_SERVERS = {
    "foot": "https://routing.openstreetmap.de/routed-foot/route/v1/foot",
    "bike": "https://routing.openstreetmap.de/routed-bike/route/v1/bike",
    "car": "https://routing.openstreetmap.de/routed-car/route/v1/car"
}

# Routing profile for pedestrian navigation
ROUTING_PROFILE = "foot"

def _format_instruction(maneuver: Dict, name: str) -> str:
    """
    Format OSRM maneuver into human-readable instruction for pedestrians
    
    Args:
        maneuver: OSRM maneuver object
        name: Street/road name
        
    Returns:
        Formatted instruction string optimized for pedestrian navigation
    """
    maneuver_type = maneuver.get("type", "")
    modifier = maneuver.get("modifier", "")
    
    # Pedestrian-friendly instructions
    instructions = {
        "depart": f"Start walking {modifier or 'straight'} on {name}" if name else "Start your journey",
        "turn": f"Turn {modifier} onto {name}" if modifier else f"Head to {name}",
        "new name": f"Continue on {name}",
        "continue": f"Keep walking straight on {name}" if name else "Continue straight",
        "arrive": f"You have arrived at your destination",
    }
    
    if maneuver_type in instructions:
        return instructions[maneuver_type]
    
    # Fallback for other maneuver types
    if modifier:
        return f"Go {modifier} towards {name}" if name else f"Go {modifier}"
    return f"Walk along {name}" if name else "Continue forward"

async def calculate_route(origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
    """
    Calculate optimal pedestrian route between two coordinates using OSRM
    
    Optimized for visually impaired users with pedestrian-friendly directions.
    
    Args:
        origin: tuple of (latitude, longitude)
        destination: tuple of (latitude, longitude)
        
    Returns:
        dict with route steps and duration/distance:
        {
            "steps": [
                {
                    "instruction": str (pedestrian-friendly),
                    "distance": float (meters),
                    "duration": float (seconds)
                }
            ],
            "total_distance": float (meters),
            "total_duration": float (seconds)
        }
        
    Raises:
        Exception: If routing calculation fails
    """
    try:
        origin_lat, origin_lon = origin
        dest_lat, dest_lon = destination
        
        # OSRM uses longitude,latitude format
        coordinates = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        
        # Get the appropriate OSRM server for the profile
        osrm_base_url = OSRM_SERVERS.get(ROUTING_PROFILE, OSRM_SERVERS["foot"])
        url = f"{osrm_base_url}/{coordinates}"
        
        params = {
            "overview": "full",
            "steps": "true",
            "geometries": "geojson"
        }
        
        logger.info(f"Requesting route from OSRM: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if route was found
        if data.get("code") != "Ok" or not data.get("routes"):
            logger.warning(f"OSRM returned no route: {data.get('code')}")
            return {
                "steps": [],
                "total_distance": 0.0,
                "total_duration": 0.0
            }
        
        route = data["routes"][0]
        leg = route["legs"][0]
        
        # Extract steps from OSRM response
        steps = []
        for step in leg.get("steps", []):
            maneuver = step.get("maneuver", {})
            name = step.get("name", "unnamed road")
            if isinstance(name, list):
                name = name[0] if name else "unnamed road"
            
            instruction = _format_instruction(maneuver, name)
            
            steps.append({
                "instruction": instruction,
                "distance": step.get("distance", 0.0),
                "duration": step.get("duration", 0.0)
            })
        
        # Extract the route geometry (coordinates) for map visualization
        route_geometry = route.get("geometry", {})
        route_coords = []
        if isinstance(route_geometry, dict) and route_geometry.get("coordinates"):
            # GeoJSON format: [[lon, lat], [lon, lat], ...]
            # Convert to [[lat, lon], [lat, lon], ...] for Leaflet
            route_coords = [[lat, lon] for lon, lat in route_geometry.get("coordinates", [])]
            logger.info(f"Extracted {len(route_coords)} coordinates from OSRM geometry")
        else:
            logger.warning(f"No geometry found in OSRM response. Route geometry: {route_geometry}")
        
        return {
            "steps": steps,
            "total_distance": route.get("distance", 0.0),
            "total_duration": route.get("duration", 0.0),
            "route_coordinates": route_coords
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OSRM API request failed: {str(e)}")
        raise Exception(f"Routing service unavailable: {str(e)}")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse OSRM response: {str(e)}")
        raise Exception(f"Invalid routing response: {str(e)}")
    except Exception as e:
        logger.error(f"Routing calculation failed: {str(e)}")
        raise
