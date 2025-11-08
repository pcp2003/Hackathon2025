# Commit: Refactor Text-to-Speech to Use ElevenLabs Only

Date: 2025-11-08
Author: Pedro

## Changes Made

- **Simplified text_to_speech module**: Removed all fallback mechanisms (pyttsx3, dummy WAV generation)
- **ElevenLabs as mandatory dependency**: Now requires ELEVENLABS_API_KEY to be configured
- **Moved imports to top level**: All imports are now at the module level for better dependency clarity
- **Created audio_output folder**: All generated WAV files are stored in `backend/audio_output/`
- **Improved code structure**:
  - `_format_text()`: Handles text formatting logic
  - `_load_env()`: Loads environment variables from .env file
  - `text_to_speech()`: Main function that generates audio using ElevenLabs API

## Files Modified/Created

- `backend/services/text_to_speech.py`: Refactored to use only ElevenLabs
- `backend/tests/test_text_to_speech.py`: Updated tests with proper mocking of ElevenLabs client
- `backend/audio_output/`: New folder for storing generated WAV files

## Tests Added

All 4 tests passing:
- `test_text_to_speech_creates_file`: Verifies WAV file is created successfully in audio_output/
- `test_text_to_speech_with_different_filename`: Tests custom output filename in audio_output/
- `test_text_to_speech_calls_elevenlabs_correctly`: Verifies API is called with correct parameters
- `test_text_to_speech_missing_api_key`: Tests error handling when API key is missing

## How to Test

1. Ensure `.env` file exists with `ELEVENLABS_API_KEY` configured:
   ```
   ELEVENLABS_API_KEY=your-api-key-here
   ```

2. Run tests:
   ```bash
   cd backend
   python -m pytest tests/test_text_to_speech.py -v
   ```

3. Expected output: All 4 tests pass

4. Manual test:
   ```python
   from services.text_to_speech import text_to_speech
   
   data = {
       "steps": [{"instruction": "Turn left", "distance": 100}],
       "total_distance": 100
   }
   output = text_to_speech(data, output_file="output.wav")
   # File will be saved to: backend/audio_output/output.wav
   ```

## Notes

- Requires valid ELEVENLABS_API_KEY in `.env` file
- Will raise `RuntimeError` if API key is not configured
- Uses ElevenLabs API v1.5.0 from requirements.txt
- Default voice: Rachel (ID: 21m00Tcm4TlvDq8ikWAM)
- Removed dependencies on pyttsx3 and wave-generation fallback
- All audio files are automatically saved to `backend/audio_output/` directory

