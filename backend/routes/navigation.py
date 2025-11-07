"""
Navigation endpoints for voice-based routing
"""
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import logging

from services.transcription import transcribe_audio
from services.nlp import extract_destination
from services.routing import calculate_route
from services.text_to_speech import generate_audio_guidance

logger = logging.getLogger(__name__)
router = APIRouter()

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class TranscribeResponse(BaseModel):
    text: str
    confidence: float

class DestinationResponse(BaseModel):
    destination: str
    latitude: float
    longitude: float

class RouteStep(BaseModel):
    instruction: str
    distance: float
    duration: float

class RouteResponse(BaseModel):
    steps: List[RouteStep]
    total_distance: float
    total_duration: float

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Convert audio to text using ElevenLabs STT
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
    Extract destination from natural language using NLP
    """
    try:
        destination_data = await extract_destination(text)
        return DestinationResponse(**destination_data)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise

@router.post("/route", response_model=RouteResponse)
async def get_route(
    origin_lat: float = Form(...),
    origin_lon: float = Form(...),
    dest_lat: float = Form(...),
    dest_lon: float = Form(...)
):
    """
    Calculate optimal route using OSRM
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
async def text_to_speech(text: str = Form(...)):
    """
    Convert text to speech audio using ElevenLabs TTS
    """
    try:
        audio_content = await generate_audio_guidance(text)
        return {
            "audio": audio_content,
            "format": "mp3"
        }
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise

@router.post("/update-location")
async def update_location(
    latitude: float = Form(...),
    longitude: float = Form(...),
    destination_lat: float = Form(...),
    destination_lon: float = Form(...)
):
    """
    Update user location and recalculate if off-route
    """
    try:
        result = await check_route_deviation(
            current=(latitude, longitude),
            destination=(destination_lat, destination_lon)
        )
        return result
    except Exception as e:
        logger.error(f"Location update error: {str(e)}")
        raise

async def check_route_deviation(current, destination):
    """Helper function to check if user is off-route"""
    # TODO: Implement route deviation detection
    return {"on_route": True, "needs_recalculation": False}
