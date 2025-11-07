import os
import pytest
from services.text_to_speech import text_to_speech

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
def cleanup_output():
    """Remove ficheiro gerado após o teste."""
    yield
    if os.path.exists("navigation.wav"):
        os.remove("navigation.wav")

def test_text_to_speech_creates_file(sample_data, cleanup_output):
    output_path = text_to_speech(sample_data, output_file="navigation.wav")

    # 1️⃣ Verifica se o ficheiro foi criado
    assert os.path.exists(output_path), "O ficheiro .wav não foi criado."

    # 2️⃣ Verifica se o nome retornado é o mesmo
    assert output_path == "navigation.wav", "O nome do ficheiro retornado é incorreto."

    # 3️⃣ Verifica se o ficheiro não está vazio
    file_size = os.path.getsize(output_path)
    assert file_size > 0, "O ficheiro gerado está vazio."

def test_text_to_speech_with_different_filename(sample_data, cleanup_output):
    custom_filename = "route_test.wav"
    output_path = text_to_speech(sample_data, output_file=custom_filename)

    assert os.path.exists(output_path)
    assert output_path == custom_filename

    os.remove(custom_filename)
