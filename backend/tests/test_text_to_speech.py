import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from services.text_to_speech import text_to_speech, text_to_speech_stream, _format_initial_guidance


@pytest.fixture
def sample_data():
    return {
        "steps": [
            {"instruction": "Head north on Main Street", "distance": 100.0},
            {"instruction": "Turn left on 5th Avenue", "distance": 150.0}
        ],
        "total_distance": 250.0
    }


@pytest.fixture
def audio_dir():
    """Cria e limpa a pasta audio_output para testes."""
    audio_path = Path(__file__).parent.parent / "audio_output"
    audio_path.mkdir(exist_ok=True)
    yield audio_path
    # Cleanup após os testes
    for file in audio_path.glob("*.wav"):
        file.unlink()


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client para testes."""
    with patch('services.text_to_speech.ElevenLabs') as mock_client_class:
        # Cria mock do cliente
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Simula resposta do text_to_speech.convert (gerador de chunks)
        mock_client.text_to_speech.convert.return_value = iter([b'audio_chunk_1', b'audio_chunk_2'])
        yield mock_client_class


@pytest.fixture
def mock_env(monkeypatch):
    """Mock variáveis de ambiente."""
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-api-key-123")


def test_text_to_speech_creates_file(sample_data, mock_elevenlabs_client, mock_env, audio_dir):
    """Testa se o arquivo WAV é criado com sucesso na pasta audio_output."""
    output_path = text_to_speech(sample_data, output_file="navigation.wav")

    # Verifica se o ficheiro foi criado
    assert os.path.exists(output_path), "O ficheiro .wav não foi criado."
    
    # Verifica se está na pasta audio_output
    assert "audio_output" in output_path, "O ficheiro não está na pasta audio_output."
    
    # Verifica se o ficheiro não está vazio
    file_size = os.path.getsize(output_path)
    assert file_size > 0, "O ficheiro gerado está vazio."


def test_text_to_speech_with_different_filename(sample_data, mock_elevenlabs_client, mock_env, audio_dir):
    """Testa com nome de ficheiro customizado."""
    custom_filename = "route_test.wav"
    output_path = text_to_speech(sample_data, output_file=custom_filename)

    assert os.path.exists(output_path)
    assert "audio_output" in output_path
    assert custom_filename in output_path


def test_text_to_speech_calls_elevenlabs_correctly(sample_data, mock_elevenlabs_client, mock_env, audio_dir):
    """Testa se ElevenLabs é chamado com parâmetros corretos."""
    text_to_speech(sample_data, output_file="test.wav")

    # Verifica se o cliente foi inicializado com a API key correta
    mock_elevenlabs_client.assert_called_once_with(api_key="test-api-key-123")
    
    # Verifica se convert foi chamado
    client_instance = mock_elevenlabs_client.return_value
    client_instance.text_to_speech.convert.assert_called_once()
    
    # Verifica parâmetros
    call_kwargs = client_instance.text_to_speech.convert.call_args.kwargs
    assert "Navigation instructions:" in call_kwargs["text"]
    assert call_kwargs["voice_id"] == "21m00Tcm4TlvDq8ikWAM"


def test_text_to_speech_missing_api_key(sample_data, monkeypatch, audio_dir):
    """Testa erro quando ELEVENLABS_API_KEY não está definida."""
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY não definida"):
        text_to_speech(sample_data)


def test_text_to_speech_stream_creates_file(mock_elevenlabs_client, mock_env, audio_dir):
    """Testa se text_to_speech_stream cria arquivo para instruções individuais."""
    text = "Turn left on 5th Avenue for 150 meters."
    output_path = text_to_speech_stream(text, output_file="step_instruction.wav")

    assert os.path.exists(output_path)
    assert "audio_output" in output_path
    assert "step_instruction.wav" in output_path
    assert os.path.getsize(output_path) > 0


def test_text_to_speech_stream_calls_elevenlabs(mock_elevenlabs_client, mock_env, audio_dir):
    """Testa se text_to_speech_stream chama ElevenLabs corretamente."""
    text = "Walk straight ahead on Main Street."
    text_to_speech_stream(text, output_file="guidance.wav")

    client_instance = mock_elevenlabs_client.return_value
    client_instance.text_to_speech.convert.assert_called()
    
    call_kwargs = client_instance.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["text"] == text
    assert call_kwargs["voice_id"] == "21m00Tcm4TlvDq8ikWAM"


def test_format_initial_guidance():
    """Testa formatação da mensagem de orientação inicial."""
    guidance_text = _format_initial_guidance(
        origin_name="Central Park",
        destination_name="Times Square",
        total_distance=1200.0,  # 1.2 km
        total_duration=900.0    # 15 minutos
    )

    # Verifica se a mensagem contém informações críticas
    assert "Central Park" in guidance_text
    assert "Times Square" in guidance_text
    assert "1.2" in guidance_text  # km
    assert "15" in guidance_text   # minutos
    assert "You are starting from" in guidance_text
    assert "Your destination is" in guidance_text


def test_format_initial_guidance_with_long_distance():
    """Testa formatação com distância maior."""
    guidance_text = _format_initial_guidance(
        origin_name="Downtown",
        destination_name="Airport",
        total_distance=5500.0,   # 5.5 km
        total_duration=2700.0    # 45 minutos
    )

    assert "5.5" in guidance_text
    assert "45" in guidance_text


def test_text_to_speech_stream_missing_api_key(monkeypatch, audio_dir):
    """Testa erro quando ELEVENLABS_API_KEY não está definida para stream."""
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY não definida"):
        text_to_speech_stream("Test instruction")

