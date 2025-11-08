import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
import logging
import math

logger = logging.getLogger(__name__)

load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    radius_km = 6371
    
    return c * radius_km


def geocode_address(address: str) -> dict:
    """
    Geocode an address using OSRM (Nominatim) to get coordinates.
    
    Args:
        address: The address string to geocode
        
    Returns:
        dict with latitude, longitude, and the address
        Example: {"latitude": 38.7369, "longitude": -9.1399, "address": "R. Neves Ferreira, Lisbon, Portugal"}
    """
    try:
        # Use Nominatim API (OSM's geocoding service)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        
        # Add User-Agent as required by Nominatim
        headers = {
            "User-Agent": "NaviAccess-App/1.0"
        }
        
        logger.info(f"Geocoding address with Nominatim: {address}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        
        if not results:
            logger.warning(f"Nominatim found no results for: {address}")
            return None
        
        result = results[0]
        lat = float(result.get("lat"))
        lon = float(result.get("lon"))
        display_name = result.get("display_name", address)
        
        logger.info(f"Geocoded '{address}' to ({lat}, {lon})")
        
        return {
            "latitude": lat,
            "longitude": lon,
            "address": display_name
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Nominatim API request failed: {str(e)}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse Nominatim response: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Geocoding failed: {str(e)}")
        return None


def text_to_places(transcription_data: dict, user_coords: dict = None):
    """
    Extract destination address from transcribed text using OpenAI and geocode it with OSRM/Nominatim.
    
    Args:
        transcription_data: Dictionary from transcription service with keys:
            - text: The transcribed text
            - confidence: Confidence score of transcription
        user_coords: Optional dict with user's current location:
            - latitude: User's latitude
            - longitude: User's longitude
    
    Returns:
        dict with destination_address, latitude, and longitude
        Example: {
            "destination_address": "R. Neves Ferreira, Lisbon, Portugal",
            "latitude": 38.7369,
            "longitude": -9.1399
        }
    """
    # Extract text from the transcription JSON response
    transcript_text = transcription_data.get("text", "")
    confidence = transcription_data.get("confidence", 0)
    
    print(f"Transcription: {transcript_text} (confidence: {confidence})")

    # Create prompt to extract destination address from transcribed text
    # The address should be suitable for geocoding services like OSRM
    user_context = ""
    if user_coords and user_coords.get("latitude") and user_coords.get("longitude"):
        user_lat = user_coords.get("latitude")
        user_lon = user_coords.get("longitude")
        user_context = f"""
    
    IMPORTANT: The user is currently at coordinates ({user_lat}, {user_lon}).
    Make sure the extracted destination is reasonable for someone in that area.
    Prefer destinations that are nearby (within ~25-30km of the user's position).
    If the destination seems too far, try to find a closer location with a similar name.
    """
    
    prompt = f"""
    From this conversation, extract the destination address.
    Return a clean, complete address that can be used for geocoding (like with OpenStreetMap/OSRM).
    Include street name, city, and country when possible.
    {user_context}
    
    Respond strictly in JSON with this format:
    {{"destination_address": "<complete_address>"}}
    
    Examples of good addresses:
    - "R. Neves Ferreira, Lisbon, Portugal"
    - "Times Square, New York, United States"
    - "Central Park, Manhattan, New York, United States"
    
    Conversation: {transcript_text}
    """

    # Call OpenAI API to extract destination
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "OpenAI-Project-Id": os.getenv("OPENAI_PROJECT_ID")
        } if os.getenv("OPENAI_PROJECT_ID") else {}
    )

    # Parse the JSON response
    data = json.loads(response.choices[0].message.content)
    destination_address = data.get("destination_address", "")

    print(f"Extracted destination address: {destination_address}")

    # Now geocode the address using Nominatim (part of OSRM ecosystem)
    geocode_result = geocode_address(destination_address)
    
    if geocode_result:
        result = {
            "destination_address": geocode_result.get("address", destination_address),
            "latitude": geocode_result.get("latitude"),
            "longitude": geocode_result.get("longitude")
        }
    else:
        # If geocoding fails, return just the address without coordinates
        logger.warning(f"Could not geocode address: {destination_address}")
        result = {
            "destination_address": destination_address,
            "latitude": None,
            "longitude": None
        }

    print(f"Final result: {json.dumps(result, indent=2)}")
    return result


def generate_destination_summary(destination_address: str, destination_coords: dict, user_coords: dict) -> str:
    """
    Generate a natural language summary of the destination with distance information.
    
    Args:
        destination_address: The destination address string
        destination_coords: dict with latitude and longitude of destination
        user_coords: dict with latitude and longitude of user
        
    Returns:
        str: A natural language description to be read aloud to the user
        Example: "Your destination is R. Neves Ferreira in Lisbon, Portugal. 
                 It is zero point seven kilometers away from your current location."
    """
    if not destination_coords or not user_coords:
        return f"Your destination is {destination_address}."
    
    dest_lat = destination_coords.get("latitude")
    dest_lon = destination_coords.get("longitude")
    user_lat = user_coords.get("latitude")
    user_lon = user_coords.get("longitude")
    
    # Calculate distance
    distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
    
    # Format distance for natural speech
    if distance < 1:
        distance_text = f"{distance*1000:.0f} meters"
    elif distance < 25:
        distance_text = f"{distance:.1f} kilometers"
    else:
        distance_text = f"{distance:.0f} kilometers"
    
    # Create natural language summary
    summary = f"""Your destination is {destination_address}. 
It is {distance_text} away from your current location. 
Please confirm if you want to proceed with directions to this location."""
    
    return summary.strip()


def speak_destination_summary(destination_address: str, destination_coords: dict, user_coords: dict, output_file: str = "destination_confirmation.wav") -> str:
    """
    Generate a spoken confirmation of the destination with distance details.
    
    Args:
        destination_address: The destination address string
        destination_coords: dict with latitude and longitude of destination
        user_coords: dict with latitude and longitude of user
        output_file: Output filename for the audio file
        
    Returns:
        str: Path to the generated audio file
        
    Example:
        audio_path = speak_destination_summary(
            "R. Neves Ferreira, Lisbon, Portugal",
            {"latitude": 38.7307, "longitude": -9.1299},
            {"latitude": 38.7369, "longitude": -9.1299}
        )
        # Plays: "Your destination is R. Neves Ferreira in Lisbon, Portugal. 
        #         It is 0.7 kilometers away from your current location. 
        #         Please confirm if you want to proceed with directions to this location."
    """
    try:
        # Import here to avoid circular imports
        from services.text_to_speech import text_to_speech
        
        # Generate the summary text
        summary = generate_destination_summary(destination_address, destination_coords, user_coords)
        
        logger.info(f"Speaking destination confirmation: {summary}")
        
        # Convert to speech
        audio_path = text_to_speech(summary, output_file=output_file)
        
        logger.info(f"Destination confirmation audio saved to: {audio_path}")
        return audio_path
        
    except Exception as e:
        logger.error(f"Failed to generate destination confirmation audio: {str(e)}")
        raise


def generate_user_comment_response(user_comment: str, context: dict = None) -> str:
    """
    Generate an intelligent response to user comments/feedback using OpenAI.
    
    Args:
        user_comment: The user's spoken comment or feedback (from transcription)
        context: Optional dict with additional context:
            - current_destination: Current destination address
            - current_distance: Distance to destination in km
            - current_route_step: Current navigation instruction
            
    Returns:
        str: Natural language response to the user's comment
        
    Example:
        response = generate_user_comment_response(
            "The destination seems too far",
            {"current_destination": "Porto", "current_distance": 273}
        )
        # Returns: "I understand. Porto is 273 kilometers away. 
        #          Would you like to search for an alternative destination closer to you?"
    """
    context_text = ""
    if context:
        if context.get("current_destination"):
            context_text += f"Current destination: {context['current_destination']}. "
        if context.get("current_distance"):
            context_text += f"Distance: {context['current_distance']} km. "
        if context.get("current_route_step"):
            context_text += f"Current instruction: {context['current_route_step']}. "
    
    prompt = f"""
    You are a helpful navigation assistant for visually impaired users.
    The user has made the following comment or request:
    
    "{user_comment}"
    
    {f"Context: {context_text}" if context_text else ""}
    
    Provide a helpful, concise response that:
    1. Acknowledges their comment
    2. Provides relevant information or suggestions
    3. Asks a clarifying question if needed
    
    Keep the response short and natural (2-3 sentences max) - it will be read aloud to the user.
    
    Respond with just the message, no JSON or formatting.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "OpenAI-Project-Id": os.getenv("OPENAI_PROJECT_ID")
            } if os.getenv("OPENAI_PROJECT_ID") else {}
        )
        
        assistant_response = response.choices[0].message.content.strip()
        logger.info(f"Generated response to user comment: {assistant_response}")
        return assistant_response
        
    except Exception as e:
        logger.error(f"Failed to generate response to user comment: {str(e)}")
        return "I didn't quite understand. Could you please repeat that?"


def speak_user_comment_response(user_comment: str, context: dict = None, output_file: str = "user_response.wav") -> dict:
    """
    Process user comment, generate response, and convert to speech.
    
    Args:
        user_comment: The user's spoken comment/feedback (from transcription)
        context: Optional dict with navigation context (destination, distance, route info)
        output_file: Output filename for the audio file
        
    Returns:
        dict with:
        - response_text: The generated response text
        - audio_path: Path to the generated audio file
        - message: Summary message
        
    Example:
        result = speak_user_comment_response(
            "Can I change my destination?",
            {"current_destination": "Porto", "current_distance": 273}
        )
        # Returns: {
        #     "response_text": "Of course! Would you like to set a new destination?",
        #     "audio_path": "/app/audio_output/user_response.wav",
        #     "message": "Response recorded and ready for playback"
        # }
    """
    try:
        # Import here to avoid circular imports
        from services.text_to_speech import text_to_speech
        
        # Generate response to user's comment
        response_text = generate_user_comment_response(user_comment, context)
        
        logger.info(f"User comment: {user_comment}")
        logger.info(f"Generated response: {response_text}")
        
        # Convert response to speech
        audio_path = text_to_speech(response_text, output_file=output_file)
        
        logger.info(f"User response audio saved to: {audio_path}")
        
        return {
            "response_text": response_text,
            "audio_path": audio_path,
            "message": "Response recorded and ready for playback"
        }
        
    except Exception as e:
        logger.error(f"Failed to process and speak user comment: {str(e)}")
        raise


def generate_error_response(error_type: str, error_details: str = None) -> str:
    """
    Generate a user-friendly error message explaining why the route could not be calculated.
    
    Args:
        error_type: Type of error. Options:
            - "distance_exceeded": Route is too far
            - "invalid_destination": Destination could not be found
            - "no_route_found": No route exists between origin and destination
            - "routing_service_error": OSRM service error
            - "geocoding_error": Could not find coordinates
            - "unknown": Generic error
        error_details: Optional additional error details to include
        
    Returns:
        str: Natural language error message to be read aloud to user
        
    Example:
        msg = generate_error_response(
            "distance_exceeded",
            "Route is 273 kilometers away, maximum is 50 kilometers"
        )
        # Returns: "I'm sorry, I could not calculate a route because the destination is too far away. 
        #          The distance exceeds 50 kilometers. Please try a closer destination."
    """
    error_messages = {
        "distance_exceeded": (
            "I'm sorry, I could not calculate a route because the destination is too far away. "
            "The maximum distance I can navigate is 50 kilometers. Please try a closer destination."
        ),
        "invalid_destination": (
            "I'm sorry, I could not find the destination you mentioned. "
            "Please try saying the destination address again, or provide more details like the city or street name."
        ),
        "no_route_found": (
            "I'm sorry, I could not find a route to your destination. "
            "This might be because there is no pedestrian path available. Please try a different destination."
        ),
        "routing_service_error": (
            "I'm sorry, the navigation service is temporarily unavailable. "
            "Please try again in a moment."
        ),
        "geocoding_error": (
            "I'm sorry, I could not find the coordinates for your destination. "
            "Please try saying the destination again with more details."
        ),
        "unknown": (
            "I'm sorry, something went wrong while calculating your route. "
            "Please try again or say your destination once more."
        )
    }
    
    message = error_messages.get(error_type, error_messages["unknown"])
    
    # Add details if provided
    if error_details:
        message = f"{message} Details: {error_details}"
    
    logger.info(f"Generated error response for {error_type}: {message}")
    return message


def speak_error_response(error_type: str, error_details: str = None, output_file: str = "error_response.wav") -> dict:
    """
    Generate an error message and convert it to speech for the user.
    
    This function informs the user why their route request failed and suggests next steps,
    allowing them to refine their request and try again.
    
    Args:
        error_type: Type of error (distance_exceeded, invalid_destination, etc.)
        error_details: Optional error details to include
        output_file: Output filename for the audio file
        
    Returns:
        dict with:
        - error_message: The error explanation text
        - audio_path: Path to the generated audio file
        - error_type: The type of error
        
    Example:
        result = speak_error_response(
            "distance_exceeded",
            "Route is 273 km away, maximum is 50 km"
        )
        # Returns: {
        #     "error_message": "I'm sorry, the destination is too far...",
        #     "audio_path": "/app/audio_output/error_response.wav",
        #     "error_type": "distance_exceeded"
        # }
    """
    try:
        # Import here to avoid circular imports
        from services.text_to_speech import text_to_speech
        
        # Generate error message
        error_message = generate_error_response(error_type, error_details)
        
        logger.info(f"Speaking error response for {error_type}")
        
        # Convert error message to speech
        audio_path = text_to_speech(error_message, output_file=output_file)
        
        logger.info(f"Error response audio saved to: {audio_path}")
        
        return {
            "error_message": error_message,
            "audio_path": audio_path,
            "error_type": error_type
        }
        
    except Exception as e:
        logger.error(f"Failed to generate and speak error response: {str(e)}")
        raise


def validate_and_correct_location(original_address: str, destination_coords: dict, user_coords: dict) -> dict:
    """
    Validate if the destination is within 25km of the user's location.
    If not, use GPT to try to correct the address.
    
    Args:
        original_address: The original address extracted by NLP
        destination_coords: dict with latitude and longitude of destination
        user_coords: dict with latitude and longitude of user
        
    Returns:
        dict with:
        - is_valid: bool, True if within 25km
        - distance_km: float, distance in kilometers
        - corrected_address: str (if corrected), or original if valid
        - corrected_coords: dict with new coordinates (if corrected)
        - message: str with explanation
    """
    MAX_DISTANCE_KM = 25.0
    
    if not destination_coords or not user_coords:
        return {
            "is_valid": False,
            "distance_km": None,
            "corrected_address": original_address,
            "corrected_coords": destination_coords,
            "message": "Missing coordinates for validation"
        }
    
    dest_lat = destination_coords.get("latitude")
    dest_lon = destination_coords.get("longitude")
    user_lat = user_coords.get("latitude")
    user_lon = user_coords.get("longitude")
    
    # Calculate distance
    distance = haversine_distance(user_lat, user_lon, dest_lat, dest_lon)
    
    print(f"Distance from user to destination: {distance:.2f} km")
    
    if distance <= MAX_DISTANCE_KM:
        # Location is valid
        return {
            "is_valid": True,
            "distance_km": distance,
            "corrected_address": original_address,
            "corrected_coords": destination_coords,
            "message": f"Location is valid. {distance:.2f} km from user"
        }
    
    # Location is too far, try to correct using GPT
    logger.warning(f"Destination {distance:.2f}km away, exceeds 25km limit. Attempting to correct...")
    
    prompt = f"""
    The user said they want to go to: "{original_address}"
    But this location is {distance:.2f} km away from the user's current position ({user_lat}, {user_lon}).
    
    This seems too far. The user is likely referring to a similar location that's much closer to them (within 25 km).
    
    Correct the address to a more likely nearby location. 
    Return a corrected address in the same region/city.
    
    Respond strictly in JSON with this format:
    {{"destination_address": "<corrected_address>"}}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "OpenAI-Project-Id": os.getenv("OPENAI_PROJECT_ID")
            } if os.getenv("OPENAI_PROJECT_ID") else {}
        )
        
        corrected_data = json.loads(response.choices[0].message.content)
        corrected_address = corrected_data.get("destination_address", original_address)
        
        print(f"GPT suggested correction: {corrected_address}")
        
        # Geocode the corrected address
        corrected_geocode = geocode_address(corrected_address)
        
        if corrected_geocode:
            corrected_distance = haversine_distance(
                user_lat, user_lon,
                corrected_geocode["latitude"], corrected_geocode["longitude"]
            )
            
            if corrected_distance <= MAX_DISTANCE_KM:
                logger.info(f"Correction accepted: {corrected_distance:.2f} km away")
                return {
                    "is_valid": True,
                    "distance_km": corrected_distance,
                    "corrected_address": corrected_geocode.get("address", corrected_address),
                    "corrected_coords": {
                        "latitude": corrected_geocode["latitude"],
                        "longitude": corrected_geocode["longitude"]
                    },
                    "message": f"Address was corrected to nearby location. {corrected_distance:.2f} km away"
                }
        
        # Correction didn't help, return original with warning
        return {
            "is_valid": False,
            "distance_km": distance,
            "corrected_address": original_address,
            "corrected_coords": destination_coords,
            "message": f"Location {distance:.2f} km away exceeds 25km limit. Could not find nearby alternative."
        }
        
    except Exception as e:
        logger.error(f"Error trying to correct location: {str(e)}")
        return {
            "is_valid": False,
            "distance_km": distance,
            "corrected_address": original_address,
            "corrected_coords": destination_coords,
            "message": f"Location {distance:.2f} km away exceeds 25km limit."
        }