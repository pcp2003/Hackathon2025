"""
Routing service using OSRM (Open Source Routing Machine)
"""
import logging
import os
import requests
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# OSRM API endpoint - can be overridden via environment variable
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")

def _format_instruction(maneuver: Dict, name: str) -> str:
    """
    Format OSRM maneuver into human-readable instruction
    
    Args:
        maneuver: OSRM maneuver object
        name: Street/road name
        
    Returns:
        Formatted instruction string
    """
    maneuver_type = maneuver.get("type", "")
    modifier = maneuver.get("modifier", "")
    
    instructions = {
        "depart": f"Head {modifier or 'straight'} on {name}" if name else "Start navigation",
        "turn": f"Turn {modifier} onto {name}" if modifier else f"Turn onto {name}",
        "new name": f"Continue on {name}",
        "continue": f"Continue straight on {name}" if name else "Continue straight",
        "arrive": f"Arrive at destination",
    }
    
    if maneuver_type in instructions:
        return instructions[maneuver_type]
    
    # Fallback for other maneuver types
    if modifier:
        return f"{modifier.capitalize()} onto {name}" if name else modifier.capitalize()
    return f"Follow {name}" if name else "Continue"

async def calculate_route(origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
    """
    Calculate optimal route between two coordinates using OSRM
    
    Args:
        origin: tuple of (latitude, longitude)
        destination: tuple of (latitude, longitude)
        
    Returns:
        dict with route steps and duration/distance:
        {
            "steps": [
                {
                    "instruction": str,
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
        url = f"{OSRM_BASE_URL}/route/v1/driving/{coordinates}"
        
        params = {
            "overview": "false",
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
        
        return {
            "steps": steps,
            "total_distance": route.get("distance", 0.0),
            "total_duration": route.get("duration", 0.0)
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
