"""
Audio transcription service using ElevenLabs
"""
import elevenlabs
import json
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

async def transcribe_audio(audio: UploadFile):
    """
    Convert audio file to text using ElevenLabs STT
    
    Args:
        audio: Audio file upload
        
    Returns:
        dict with text and confidence score
    """
    try:
        audio_file = await audio.read()

        response = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",
            tag_audio_events=True,
            diarize=False
        )
        data = json.loads(response.text)

        return data
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise
