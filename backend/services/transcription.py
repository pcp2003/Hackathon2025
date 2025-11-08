import aiohttp
import os
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)


async def transcribe_audio(audio: UploadFile):
    """
    Convert audio file to text using ElevenLabs Speech-to-Text API
    """
    # Input validation
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")


    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY environment variable not set")

    try:
        # Read audio content
        audio_content = await audio.read()

        # Prepare form data for the API request
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            audio_content,
            filename=audio.filename,
            content_type=audio.content_type
        )
        form_data.add_field('model_id', 'scribe_v1')

        # API headers
        headers = {
            "xi-api-key": api_key,
            "Accept": "application/json"
        }

        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://api.elevenlabs.io/v1/speech-to-text",
                    data=form_data,
                    headers=headers
            ) as response:

                if response.status == 200:
                    # Success - parse the response
                    result = await response.json()
                    logger.info(f"Transcription successful: {result}")
                    return result
                else:
                    # Handle API errors
                    error_text = await response.text()
                    logger.error(f"ElevenLabs API error {response.status}: {error_text}")

                    # Provide more user-friendly error messages
                    if response.status == 401:
                        raise HTTPException(status_code=401, detail="Invalid API key")
                    elif response.status == 402:
                        raise HTTPException(status_code=402, detail="Insufficient credits or quota exceeded")
                    elif response.status == 404:
                        raise HTTPException(status_code=404,
                                            detail="Speech-to-text endpoint not found - check your API tier")
                    elif response.status == 422:
                        raise HTTPException(status_code=422, detail="Invalid audio file format")
                    else:
                        raise HTTPException(status_code=response.status, detail=f"API error: {error_text}")

    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription service error: {str(e)}")