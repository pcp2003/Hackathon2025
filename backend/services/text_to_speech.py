import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def text_to_speech(data, output_file="navigation.wav", voice="Adam"):
    text_to_speak = "Navigation instructions: "
    for step in data["steps"]:
        text_to_speak += f"{step['instruction']} for {step['distance']} meters. "
    text_to_speak += f"Total distance: {data['total_distance']} meters."

    response = elevenlabs.text_to_speech.convert(
        voice=voice,
        model_id="eleven_multilingual_v2",
        text=text_to_speak
    )

    with open(output_file, "wb") as f:
        for chunk in response:
            f.write(chunk)

    return output_file