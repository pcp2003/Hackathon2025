"""
Navigation endpoints for voice-based routing
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import logging
import json

from services.transcription import transcribe_audio
from services.nlp import (
    text_to_places, 
    speak_destination_summary, 
    speak_user_comment_response,
    speak_error_response
)
from services.routing import calculate_route
from services.text_to_speech import text_to_speech, text_to_speech_stream, _format_initial_guidance
from schemas.navigation import (
    TranscribeResponse,
    DestinationResponse,
    RouteResponse,
    RouteStep,
    LocationUpdateResponse,
    SpeakResponse,
    InitialGuidanceRequest,
    InitialGuidanceResponse,
    StepGuidanceRequest,
    StepGuidanceResponse,
    ErrorResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["navigation"])

# Store current user location and route state
current_user_location = {"latitude": None, "longitude": None}
current_route_state = {
    "steps": [],
    "total_distance": 0.0,
    "total_duration": 0.0,
    "current_step_index": 0,
}




@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Convert audio to text using ElevenLabs STT

    - **audio**: Audio file to transcribe
    - Returns: Transcribed text with confidence score
    """
    try:
        result = await transcribe_audio(audio)
        return TranscribeResponse(text=result["text"], confidence=result.get("confidence", 0.9))
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise


@router.post("/analyze", response_model=DestinationResponse)
async def analyze_destination(text: str = Form(...)):
    """
    Extract destination from natural language using NLP with user location context.
    Uses the current user location from the last /update-location call.

    - **text**: Natural language input describing destination
    - Returns: Destination name and coordinates
    """
    try:
        # Get transcription data from text
        transcription_data = {"text": text, "confidence": 1.0}

        # Build user coordinates from stored location
        user_coords = None
        if current_user_location["latitude"] is not None and current_user_location["longitude"] is not None:
            user_coords = {
                "latitude": current_user_location["latitude"],
                "longitude": current_user_location["longitude"]
            }
            logger.info(f"Using user location: {user_coords}")
        else:
            logger.warning("No user location available. Using generic analysis.")

        # Extract destination address (with or without user location context)
        destination_data = text_to_places(transcription_data, user_coords=user_coords)
        return DestinationResponse(**destination_data)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise


@router.post("/route")
async def get_route(
    origin_lat: float = Form(...),
    origin_lon: float = Form(...),
    dest_lat: float = Form(...),
    dest_lon: float = Form(...),
):
    """
    Calculate optimal route using OSRM
    
    Only routes under 50 km are calculated. Longer routes are not supported.
    
    - **origin_lat**: Starting point latitude
    - **origin_lon**: Starting point longitude
    - **dest_lat**: Destination latitude
    - **dest_lon**: Destination longitude
    - Returns: Route with steps, distance, and duration (if under 50 km)
    
    On error, returns audio explanation of what went wrong
    """
    try:
        route_data = await calculate_route(
            origin=(origin_lat, origin_lon),
            destination=(dest_lat, dest_lon)
        )
        
        # Check if route distance exceeds 50 km
        total_distance_km = route_data["total_distance"] / 1000
        max_distance_km = 50
        
        if total_distance_km > max_distance_km:
            logger.warning(
                f"Route distance ({total_distance_km:.2f} km) exceeds maximum limit ({max_distance_km} km). "
                "Route calculation rejected."
            )
            error_details = f"Route is {total_distance_km:.1f} kilometers away, maximum is {max_distance_km} kilometers"
            
            # Generate error response with audio
            error_response = speak_error_response("distance_exceeded", error_details)
            
            # Return error response as JSON instead of raising exception
            return {
                "success": False,
                "error_type": "distance_exceeded",
                "error_message": error_response["error_message"],
                "audio": error_response["audio_path"]
            }
        
        # Store route state for later use in location updates
        current_route_state["steps"] = route_data["steps"]
        current_route_state["total_distance"] = route_data["total_distance"]
        current_route_state["total_duration"] = route_data["total_duration"]
        current_route_state["current_step_index"] = 0
        
        steps = [RouteStep(**step) for step in route_data["steps"]]
        return {
            "success": True,
            "steps": [step.model_dump() for step in steps],
            "total_distance": route_data["total_distance"],
            "total_duration": route_data["total_duration"],
            "route_coordinates": route_data.get("route_coordinates", [])
        }
    except Exception as e:
        # Handle other errors (routing service errors, etc)
        error_msg = str(e)
        logger.error(f"Routing error: {error_msg}")
        
        # Determine error type based on error message
        if "routing" in error_msg.lower() or "osrm" in error_msg.lower():
            error_type = "routing_service_error"
        elif "no route" in error_msg.lower():
            error_type = "no_route_found"
        else:
            error_type = "unknown"
        
        try:
            error_response = speak_error_response(error_type, error_msg)
            
            return {
                "success": False,
                "error_type": error_type,
                "error_message": error_response["error_message"],
                "audio": error_response["audio_path"]
            }
        except Exception as audio_error:
            logger.error(f"Failed to generate error audio: {str(audio_error)}")
            # Return error without audio if generation fails
            return {
                "success": False,
                "error_type": error_type,
                "error_message": f"Routing error: {error_msg}",
                "audio": None
            }


@router.post("/speak", response_model=SpeakResponse)
async def speak_text(text: str = Form(...)):
    """
    Convert text to speech audio.

    - **text**: Instruction text to convert to audio
    - Returns: Audio file URL and format
    """
    try:
        # text_to_speech_stream generates individual step audio
        audio_path = text_to_speech_stream(text, output_file="guidance.wav")
        
        # Convert file path to URL
        audio_url = f"/audio/guidance.wav"
        
        return SpeakResponse(
            audio=audio_url,
            format="wav"
        )
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise


@router.post("/speak-initial", response_model=InitialGuidanceResponse)
async def speak_initial_guidance(
    origin_name: str = Form(...),
    destination_name: str = Form(...),
    total_distance: float = Form(...),
    total_duration: float = Form(...),
):
    """
    Generate initial guidance audio describing the entire route.
    Called after route calculation to give user overview.
    
    - **origin_name**: Starting location name
    - **destination_name**: Destination name
    - **total_distance**: Total route distance in meters
    - **total_duration**: Total route duration in seconds
    - Returns: Audio file URL with initial guidance message
    """
    try:
        # Format the initial guidance message
        guidance_text = _format_initial_guidance(
            origin_name,
            destination_name,
            total_distance,
            total_duration
        )
        
        # Generate audio
        audio_path = text_to_speech_stream(
            guidance_text,
            output_file="initial_guidance.wav"
        )
        
        # Convert file path to URL
        audio_url = f"/audio/initial_guidance.wav"
        
        return InitialGuidanceResponse(
            audio=audio_url,
            format="wav",
            message=guidance_text
        )
    except Exception as e:
        logger.error(f"Initial guidance TTS error: {str(e)}")
        raise


@router.post("/speak-step", response_model=StepGuidanceResponse)
async def speak_step_guidance(
    step_index: int = Form(...),
    instruction: str = Form(...),
    step_number: int = Form(...),
):
    """
    Generate audio for a single navigation step.
    Called when user reaches the point to execute this step.
    
    - **step_index**: Index of step in the route
    - **instruction**: The navigation instruction text
    - **step_number**: User-facing step number (for context)
    - Returns: Audio file URL with step instruction
    """
    try:
        # Format the step instruction with context
        step_text = f"Step {step_number}. {instruction}"
        
        # Generate audio for this specific step
        output_filename = f"step_{step_index}.wav"
        audio_path = text_to_speech_stream(
            step_text,
            output_file=output_filename
        )
        
        # Convert file path to URL
        audio_url = f"/audio/{output_filename}"
        
        return StepGuidanceResponse(
            audio=audio_url,
            format="wav",
            step_index=step_index,
            instruction=instruction
        )
    except Exception as e:
        logger.error(f"Step guidance TTS error: {str(e)}")
        raise


@router.post("/update-location", response_model=LocationUpdateResponse)
async def update_location(
    latitude: float = Form(...),
    longitude: float = Form(...),
    destination_lat: float = Form(...),
    destination_lon: float = Form(...),
):
    """
    Update user location and recalculate if off-route

    - **latitude**: Current latitude
    - **longitude**: Current longitude
    - **destination_lat**: Destination latitude
    - **destination_lon**: Destination longitude
    - Returns: Route status, next step instruction if needed, and audio if step completed
    """
    try:
        # Store current user location for use in /analyze endpoint
        current_user_location["latitude"] = latitude
        current_user_location["longitude"] = longitude
        logger.info(f"Updated user location: ({latitude}, {longitude})")

        result = await check_route_deviation(
            current=(latitude, longitude),
            destination=(destination_lat, destination_lon)
        )
        return LocationUpdateResponse(**result)
    except Exception as e:
        logger.error(f"Location update error: {str(e)}")
        raise


@router.post("/user-comment")
async def process_user_comment(
    text: str = Form(...),
    destination_address: str = Form(None),
    destination_distance: float = Form(None),
    route_instruction: str = Form(None),
):
    """
    Process user comments/feedback and generate intelligent voice responses.
    
    - **text**: User's spoken comment or feedback (from transcription)
    - **destination_address**: Optional current destination
    - **destination_distance**: Optional distance to destination in km
    - **route_instruction**: Optional current navigation instruction
    - Returns: Response text and audio path
    """
    try:
        # Build context from optional parameters
        context = {}
        if destination_address:
            context["current_destination"] = destination_address
        if destination_distance is not None:
            context["current_distance"] = destination_distance
        if route_instruction:
            context["current_route_step"] = route_instruction
        
        # Generate response and convert to speech
        result = speak_user_comment_response(
            text,
            context=context if context else None
        )
        
        return {
            "response_text": result["response_text"],
            "audio": result["audio_path"],
            "format": "wav",
            "message": result["message"]
        }
    except Exception as e:
        logger.error(f"User comment processing error: {str(e)}")
        raise


async def check_route_deviation(current, destination):
    """
    Check if user is off-route and determine next step.
    Returns next instruction audio if user has completed current step.
    """
    # TODO: Implement advanced route deviation detection with geofencing
    # For now, basic implementation
    return {
        "on_route": True,
        "needs_recalculation": False,
        "message": "User is on route"
    }
