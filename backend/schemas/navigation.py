"""
Navigation API schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class TranscribeResponse(BaseModel):
    """Transcription response"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class DestinationResponse(BaseModel):
    """Destination analysis response"""
    destination_address: str = Field(..., description="Destination address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class RouteStep(BaseModel):
    """Single step in a route"""
    instruction: str = Field(..., description="Navigation instruction")
    distance: float = Field(..., description="Distance in meters")
    duration: float = Field(..., description="Duration in seconds")


class RouteResponse(BaseModel):
    """Route calculation response"""
    steps: List[RouteStep] = Field(..., description="List of navigation steps")
    total_distance: float = Field(..., description="Total distance in meters")
    total_duration: float = Field(..., description="Total duration in seconds")


class LocationUpdateResponse(BaseModel):
    """Location update response"""
    on_route: bool = Field(..., description="Whether user is on the calculated route")
    needs_recalculation: bool = Field(..., description="Whether route needs recalculation")
    message: str = Field(..., description="Status message")


class SpeakResponse(BaseModel):
    """Text-to-speech response"""
    audio: str = Field(..., description="Path to audio file")
    format: str = Field(..., description="Audio format (wav)")


class InitialGuidanceRequest(BaseModel):
    """Request for initial route guidance audio"""
    origin_name: str = Field(..., description="Name/address of starting point")
    destination_name: str = Field(..., description="Name/address of destination")
    total_distance: float = Field(..., description="Total route distance in meters")
    total_duration: float = Field(..., description="Total route duration in seconds")


class InitialGuidanceResponse(BaseModel):
    """Response with initial guidance audio"""
    audio: str = Field(..., description="Path to generated audio file")
    format: str = Field(..., description="Audio format (wav)")
    message: str = Field(..., description="Initial guidance message spoken")


class StepGuidanceRequest(BaseModel):
    """Request for a single step guidance audio"""
    step_index: int = Field(..., description="Index of the step in the route")
    instruction: str = Field(..., description="Navigation instruction for this step")
    step_number: int = Field(..., description="User-facing step number (1-indexed)")


class StepGuidanceResponse(BaseModel):
    """Response with step guidance audio"""
    audio: str = Field(..., description="Path to generated audio file")
    format: str = Field(..., description="Audio format (wav)")
    step_index: int = Field(..., description="Index of the step")
    instruction: str = Field(..., description="The instruction that was spoken")
