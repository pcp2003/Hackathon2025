import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def text_to_places(transcription_data: dict):
    """
    Extract destination address from transcribed text using OpenAI.
    
    Args:
        transcription_data: Dictionary from transcription service with keys:
            - text: The transcribed text
            - confidence: Confidence score of transcription
    
    Returns:
        dict with extracted destination_address in JSON format
    """
    # Extract text from the transcription JSON response
    transcript_text = transcription_data.get("text", "")
    confidence = transcription_data.get("confidence", 0)
    
    print(f"Transcription: {transcript_text} (confidence: {confidence})")

    # Create prompt to extract destination address from transcribed text
    prompt = f"""
    From this conversation, extract the destination address and its coordinates.
    Respond strictly in JSON with this format:
    {{"destination_address": "<address>", "latitude": <latitude>, "longitude": <longitude>}}
    
    Use real world coordinates for the destination. If you can't determine exact coordinates, use approximate ones for the city/area mentioned.
    
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

    print(f"Extracted places: {json.dumps(data, indent=2)}")

    return data