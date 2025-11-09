import logging
import base64
import io
from PIL import Image
import os
from openai import OpenAI
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _resize_image(image_bytes, max_size=512):
    """
    Reduz o tamanho da imagem antes do envio para o GPT.
    512px é suficiente para boa compreensão e muito mais rápido.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail((max_size, max_size))
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=75)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return image_bytes


async def analyze_image(upload_file):
    """
    Envia uma imagem para o GPT-4o-mini (Vision) e retorna uma descrição curta e prática
    para contexto de rua — otimizado para velocidade.
    
    TODO: Phase 2 - Replace with continuous video stream analysis
    Currently analyzes single image frames. Future version will:
    - Process video stream (1 frame every 2-3 seconds)
    - Real-time obstacle/danger detection
    - Alert user without stopping navigation
    - Integrate with mobile app vibration alerts
    """
    try:
        # ⚡ Lê e comprime a imagem
        image_bytes = await upload_file.read()
        image_bytes = _resize_image(image_bytes)

        # ⚡ Codifica para base64
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # ⚡ Prompt super enxuto
        prompt = (
            "Briefly describe this street scene for a blind pedestrian. "
            "Mention only key navigation elements like cars, people, sidewalks, "
            "crosswalks, obstacles, or traffic lights. One short sentence."
        )

        # ⚡ Chamada de baixa latência ao modelo
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}" }},
                    ],
                }
            ],
            max_tokens=50,          # menos tokens = resposta mais rápida
            temperature=0.2,        # reduz variação
            timeout=5,              # corta chamadas longas
        )

        description = response.choices[0].message.content.strip()
        logger.info(f"Ultra-fast street description: {description}")
        return description

    except Exception as e:
        logger.error(f"Ultra-fast analyze error: {e}")
        return "Unable to analyze image quickly."
