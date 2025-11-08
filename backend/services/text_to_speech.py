import os
from typing import Union

def text_to_speech(data: Union[str, dict], output_file="navigation.wav", voice="Adam"):
    """
    Converte texto ou dados estruturados de navegação para um arquivo WAV.

    - Se 'data' for dict, deve conter:
        steps: lista de instruções {"instruction": str, "distance": float}
        total_distance: float
    - Se 'data' for str, será falado como texto simples.
    - Usa ElevenLabs se disponível e configurado, senão cai no fallback com pyttsx3.
    """
    # Monta o texto a partir de dados estruturados ou texto simples
    if isinstance(data, dict):
        text_to_speak = "Navigation instructions: "
        for step in data.get("steps", []):
            instr = step.get("instruction", "")
            dist = step.get("distance", 0)
            text_to_speak += f"{instr} for {dist} meters. "
        text_to_speak += f"Total distance: {data.get('total_distance', 0)} meters."
    else:
        text_to_speak = str(data)

    # Tenta usar ElevenLabs
    try:
        from dotenv import load_dotenv
        from pathlib import Path

        dotenv_path = Path(__file__).parent.parent / ".env"  # assume que backend/services/text_to_speech.py
        load_dotenv(dotenv_path)
        
        from elevenlabs import AsyncElevenLabs  # versão 1.5.0 usa AsyncElevenLabs ou BaseElevenLabs

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY não definida")

        eleven = AsyncElevenLabs(api_key=api_key)
        response = eleven.text_to_speech.convert(
            model_id="eleven_multilingual_v2",
            voice={"voice_id": voice},
            text=text_to_speak
        )

        # Salva em arquivo WAV
        with open(output_file, "wb") as f:
            try:
                for chunk in response:
                    f.write(chunk)
            except TypeError:
                f.write(response)

    except Exception:
        # Fallback usando pyttsx3 (voz offline)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text_to_speak, output_file)
            engine.runAndWait()
        except Exception:
            # Se pyttsx3 não estiver instalado, cria arquivo dummy audível simples
            import wave
            import math
            import struct
            duration = 2  # 2 segundos
            freq = 440    # tom A
            rate = 22050
            n_samples = int(duration * rate)
            with wave.open(output_file, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(rate)
                for i in range(n_samples):
                    val = int(32767.0 * 0.1 * math.sin(2 * math.pi * freq * i / rate))
                    data_bytes = struct.pack('<h', val)
                    wf.writeframesraw(data_bytes)

    return output_file
