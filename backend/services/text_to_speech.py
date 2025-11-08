import os
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


def _load_env() -> None:
    """Carrega variáveis de ambiente do arquivo .env."""
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path)


def _format_text(data: Union[str, dict]) -> str:
    """Formata dados para texto a ser falado."""
    if isinstance(data, dict):
        text_to_speak = "Navigation instructions: "
        for step in data.get("steps", []):
            instr = step.get("instruction", "")
            dist = step.get("distance", 0)
            text_to_speak += f"{instr} for {dist} meters. "
        text_to_speak += f"Total distance: {data.get('total_distance', 0)} meters."
    else:
        text_to_speak = str(data)
    return text_to_speak


def text_to_speech(data: Union[str, dict], output_file: str = "navigation.wav") -> str:
    """
    Converte texto ou dados estruturados de navegação para um arquivo WAV usando ElevenLabs.

    Args:
        data: String ou dict com:
            - steps: lista de {"instruction": str, "distance": float}
            - total_distance: float
        output_file: Caminho do arquivo WAV de saída (salvo em audio_output/)

    Returns:
        Caminho do arquivo WAV gerado

    Raises:
        RuntimeError: Se ELEVENLABS_API_KEY não estiver configurada
    """
    _load_env()
    text_to_speak = _format_text(data)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY não definida no arquivo .env")

    # Cria pasta audio_output se não existir
    audio_dir = Path(__file__).parent.parent / "audio_output"
    audio_dir.mkdir(exist_ok=True)
    
    # Define caminho completo do arquivo
    output_path = audio_dir / output_file

    # Inicializa cliente ElevenLabs
    client = ElevenLabs(api_key=api_key)

    # Gera áudio com ElevenLabs (voz padrão)
    response = client.text_to_speech.convert(
        text=text_to_speak,
        voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel
    )

    # Salva em arquivo WAV
    with open(output_path, "wb") as f:
        for chunk in response:
            f.write(chunk)

    return str(output_path)
