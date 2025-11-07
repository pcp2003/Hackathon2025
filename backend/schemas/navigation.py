"""
Navigation API schemas
"""
from pydantic import BaseModel, Field
from typing import List


class TranscribeResponse(BaseModel):
    """Transcription response"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class DestinationResponse(BaseModel):
    """Destination analysis response"""
    destination: str = Field(..., description="Destination name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


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
