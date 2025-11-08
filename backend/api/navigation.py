"""
Navigation endpoints for voice-based routing
"""
from fastapi import APIRouter, UploadFile, File, Form
import logging

from services.transcription import transcribe_audio
from services.nlp import text_to_places
from services.routing import calculate_route
from services.text_to_speech import text_to_speech
from services.image_alert import analyze_image
from schemas.navigation import (
    TranscribeResponse,
    DestinationResponse,
    RouteResponse,
    RouteStep,
    LocationUpdateResponse,
    ImageAnalysisResponse
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["navigation"])

# Store current user location
current_user_location = {"latitude": None, "longitude": None}


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(image: UploadFile = File(...)):
    """
    Analyze an uploaded image using GPT-4o-mini and detect potential danger.
    """
    try:
        description = await analyze_image(image)

        return ImageAnalysisResponse(
            description=description
        )

    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return ImageAnalysisResponse(
            description="Unable to analyze image.",
            danger_detected=False,
            danger_type=None
        )



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


@router.post("/route", response_model=RouteResponse)
async def get_route(
    origin_lat: float = Form(...),
    origin_lon: float = Form(...),
    dest_lat: float = Form(...),
    dest_lon: float = Form(...),
):
    """
    Calculate optimal route using OSRM

    - **origin_lat**: Starting point latitude
    - **origin_lon**: Starting point longitude
    - **dest_lat**: Destination latitude
    - **dest_lon**: Destination longitude
    - Returns: Route with steps, distance, and duration
    """
    try:
        route_data = await calculate_route(
            origin=(origin_lat, origin_lon),
            destination=(dest_lat, dest_lon)
        )
        steps = [RouteStep(**step) for step in route_data["steps"]]
        return RouteResponse(
            steps=steps,
            total_distance=route_data["total_distance"],
            total_duration=route_data["total_duration"]
        )
    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        raise


@router.post("/speak")
async def speak_text(text: str = Form(...)):
    """
    Convert text to speech audio.

    - **text**: Instruction text to convert to audio
    - Returns: Audio file path and format
    """
    try:
        # text_to_speech is implemented as a synchronous helper that writes a
        # file and returns the filename. Call it directly (do not await).
        audio_content = text_to_speech(text)
        return {
            "audio": audio_content,
            "format": "wav"
        }
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
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
    - Returns: Route status and whether recalculation is needed
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


async def check_route_deviation(current, destination):
    """Helper function to check if user is off-route"""
    # TODO: Implement route deviation detection
    return {
        "on_route": True,
        "needs_recalculation": False,
        "message": "User is on route"
    }
