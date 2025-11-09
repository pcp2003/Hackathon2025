NaviAcess - Voice-Guided Navigation for the Visually Impaired

Overview

NaviAcess is an AI-powered voice navigation application designed to help visually impaired individuals navigate urban environments independently. Users speak their destination naturally, and the application provides real-time audio guidance using intelligent routing and voice synthesis technology.

This repository contains both the backend API (FastAPI) and frontend interface (React + Vite) built during the Hackathon 2025.

Key Features

Voice-First Interaction

Users simply speak their destination address in natural language (e.g., "Take me to the Central Library"). The system transcribes speech to text in real-time.

AI-Powered Destination Recognition

The backend uses OpenAI's GPT-4o-mini to intelligently extract destination names from conversational speech, handling ambiguous references and natural variations in how people describe locations.

Real-Time Route Calculation

Uses the Open Source Routing Machine (OSRM) to compute optimal pedestrian routes with turn-by-turn directions specifically optimized for navigation on foot.

Natural Voice Guidance

ElevenLabs text-to-speech technology converts navigation instructions into clear, natural-sounding audio guidance. Users hear step-by-step directions without needing to read anything.

Live Image Analysis

Users can capture images of their surroundings using the device camera. GPT-4o-mini analyzes the image in real-time to describe the street scene, detect obstacles, and alert the user to potential hazards.

Error Detection and User-Friendly Messaging

Multi-stage validation prevents API errors and provides context-aware error messages delivered via audio. If a destination is too far (over 50km), no longer exists, or has no pedestrian route, the user hears a specific, actionable explanation rather than a generic error.

Responsive Mobile-First Design

The frontend is designed to work seamlessly on smartphones, with large, easy-to-tap buttons and touch-friendly controls optimized for accessibility.

Demo vs. Production Version

This version is a demonstration of core AI and voice capabilities. The production version for blind users would feature:
- A drastically simplified interface with a single, always-accessible action button
- Voice-first interaction with minimal visual elements
- Video stream analysis instead of single-frame images
- Mobile app integration with device features (haptic feedback, native audio)
- Offline support for common routes and maps

Tech Stack

Frontend

- React 18 with React DOM
- Vite (fast build tool and development server)
- Leaflet (open-source map library)
- Vitest (unit testing framework)
- Axios (HTTP client for API communication)
- HTML5 Geolocation API for GPS positioning

Backend

- FastAPI (modern Python web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation and settings management)
- OpenAI API (GPT-4o-mini for NLP and vision)
- ElevenLabs API (text-to-speech synthesis)
- OSRM (Open Source Routing Machine for pedestrian routing)
- Nominatim (OpenStreetMap geocoding service)
- Pillow (image manipulation)

DevOps

- Docker and Docker Compose (containerization)
- Nginx (reverse proxy and static file serving in production)

Prerequisites

Before you begin, ensure you have the following installed:

- Docker and Docker Compose (https://docs.docker.com/get-docker/)
- Python 3.9+ (for local backend development without Docker)
- Node.js 18+ (for local frontend development without Docker)
- Git (for cloning the repository)

You will also need API keys for:

- OpenAI API (for GPT-4o-mini vision and NLP) - Get one at https://platform.openai.com/api-keys
- ElevenLabs API (for text-to-speech) - Get one at https://elevenlabs.io/
- Optional: OpenAI Project ID (if your organization uses multiple projects)

Quick Start

Option 1: Using Docker Compose (Recommended)

Docker Compose runs both the frontend and backend in isolated containers, handling all dependencies automatically.

Step 1: Clone the Repository

git clone https://github.com/pcp2003/Hackathon2025.git
cd Hackathon2025

Step 2: Configure Environment Variables

Create a .env file in the project root with your API keys:

OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_PROJECT_ID=your_project_id_optional

Do not commit .env to version control. Add it to .gitignore if not already there.

Step 3: Build and Start Services

docker compose up --build

The build process will:
- Create Docker images for both frontend and backend
- Install all Python dependencies (backend)
- Install all Node.js dependencies (frontend)
- Start the FastAPI backend on http://localhost:8000
- Start the Nginx-served frontend on http://localhost:3000

Step 4: Access the Application

Open your browser and navigate to:

http://localhost:3000

The frontend will communicate with the backend API at http://localhost:8000/api.

Step 5: Stop the Services

When finished, stop the services with:

docker compose down

Option 2: Local Development (Without Docker)

If you prefer to run services locally for debugging or development:

Backend Setup

1. Navigate to the backend directory:
   cd backend

2. Create a Python virtual environment:
   python -m venv .venv

3. Activate the virtual environment:
   On macOS/Linux:
   source .venv/bin/activate
   
   On Windows:
   .venv\Scripts\activate

4. Install Python dependencies:
   pip install -r requirements.txt

5. Create a .env file in the backend directory with your API keys:
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

6. Start the FastAPI server:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   The backend API will be available at http://localhost:8000
   Interactive API documentation at http://localhost:8000/docs

Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   cd frontend

2. Install Node.js dependencies:
   npm install

3. Start the development server:
   npm run dev

   The frontend will typically run on http://localhost:5173 (check terminal output for the exact URL)

4. The frontend automatically connects to the backend at http://localhost:8000/api

Testing the Application

Testing Backend API

The backend includes comprehensive unit tests for all services:

pytest -q

This runs all tests in the backend/tests directory and reports coverage.

Testing Frontend

The frontend includes unit tests for React components and hooks:

npm test

Running specific test files:

npm test useNavigation.test.jsx
npm test ImageAnalyzer.test.jsx

Test Results Summary

Currently, the application includes:
- 59 backend tests covering NLP, routing, error handling, and voice synthesis
- 54 frontend tests covering React hooks and component logic
- 4 skipped tests (camera hardware-specific tests that require physical device)

Total: 113 tests with 0 failures

Using the Application

Starting a Navigation Session

1. Allow Geolocation: When you open the app, the browser will ask for permission to access your location. Grant permission to use GPS coordinates as the starting point.

2. Click the Record Button: A large blue button labeled "Record" is the main interface. Click it to start recording.

3. Speak Your Destination: Say something like:
   - "Take me to Central Library"
   - "Navigate to the train station"
   - "I want to go to the shopping mall downtown"

4. Listen to Confirmation: The system will confirm the destination and provide distance information via audio.

5. Follow Voice Guidance: As you move, listen to step-by-step audio instructions. Each turn is announced clearly.

6. Capture Surroundings: Click the "Analyze Image" button to capture a photo of your surroundings. The system will describe what it sees and alert you to any obstacles.

Example Workflow

User speaks: "Take me to Centro Comercial Colombo"
System responds: "Your destination is Centro Comercial Colombo in Lisbon, Portugal. It is 5.3 kilometers away. Please confirm if you want to proceed."
User can then navigate step by step, with audio guidance like: "Step 1. Start walking east on R. Neves Ferreira. 200 meters. Step 2. Turn left onto Rua de Santa Justa. 150 meters."

API Endpoints

The backend exposes the following REST API endpoints:

Core Navigation Endpoints

POST /api/transcribe
Converts audio input to text using ElevenLabs speech-to-text.
Body: multipart/form-data with audio file
Returns: { "text": "...", "confidence": 0.95 }

POST /api/analyze
Extracts destination address from natural language text using OpenAI.
Body: form data with "text" parameter
Returns: { "destination_address": "...", "latitude": 38.7369, "longitude": -9.1299 }

POST /api/route
Calculates optimal pedestrian route between origin and destination using OSRM.
Body: form data with origin_lat, origin_lon, dest_lat, dest_lon
Returns: { "steps": [...], "total_distance": 5300, "total_duration": 1200 }

POST /api/speak
Converts text instruction to speech audio using ElevenLabs TTS.
Body: form data with "text" parameter
Returns: Binary audio file (WAV format)

POST /api/speak-step
Generates audio for a single navigation step with natural language context.
Body: form data with step_index, instruction, step_number, language (optional)
Returns: Binary audio file (WAV format)

Analysis Endpoints

POST /api/analyze-image
Analyzes an uploaded image using GPT-4o-mini vision to describe the scene.
Body: multipart/form-data with image file
Returns: { "description": "..." }

Health and Status

GET /api/health
Returns application health status.
Returns: { "status": "healthy", "timestamp": "..." }

Project Structure

Hackathon2025/
├── README.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/
│   │   ├── __init__.py
│   │   ├── navigation.py
│   │   └── health.py
│   ├── services/
│   │   ├── transcription.py
│   │   ├── nlp.py
│   │   ├── routing.py
│   │   ├── image_alert.py
│   │   └── text_to_speech.py
│   ├── schemas/
│   │   ├── navigation.py
│   │   └── health.py
│   ├── tests/
│   │   ├── test_*.py
│   │   └── ...
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── vitest.config.js
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   └── App.jsx
│   │   ├── components/
│   │   │   ├── VoiceInput.jsx
│   │   │   ├── Map.jsx
│   │   │   ├── RouteDisplay.jsx
│   │   │   └── ImageAnalyzer.jsx
│   │   ├── hooks/
│   │   │   ├── useNavigation.js
│   │   │   ├── useGeolocation.js
│   │   │   └── useAudio.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   └── variables.css
│   │   └── tests/
│   │       └── *.test.jsx
│   └── public/
├── docker/
│   └── certs/
│       ├── cert.pem (local HTTPS)
│       └── key.pem
└── docs/
    ├── agentInstructions.md
    ├── commit-*.md (detailed commit logs)
    ├── code-audit-unused-features.md
    └── session-summary-2025-11-09.md

How It Works: Data Flow

1. User speaks destination
   - Frontend captures audio via HTML5 MediaRecorder API
   - Audio sent to backend /api/transcribe endpoint

2. Backend transcribes speech
   - ElevenLabs speech-to-text converts audio to text string
   - Returns transcribed text with confidence score

3. Frontend analyzes destination
   - Transcribed text sent to /api/analyze endpoint
   - Backend uses OpenAI to extract destination name and coordinates
   - Nominatim geocoder looks up coordinates

4. Backend calculates route
   - Origin (user location) and destination coordinates sent to /api/route
   - OSRM calculates optimal pedestrian path
   - Returns step-by-step instructions, distance, and duration

5. Frontend displays and narrates route
   - Route displayed on Leaflet map (visual reference)
   - For each step, user clicks button to hear audio narration
   - Backend /api/speak-step converts instruction to ElevenLabs audio

6. Live image analysis
   - User captures image via camera
   - Image sent to /api/analyze-image endpoint
   - GPT-4o-mini describes scene and detects obstacles
   - Response converted to audio and played to user

7. Error handling
   - If any step fails (destination too far, no route found, API error)
   - Backend generates user-friendly error message via /api/speak endpoint
   - Error audio played to user

Known Limitations and Future Work

Current Limitations

- Route calculation limited to distances under 50 kilometers
- Image analysis processes single frames (not continuous video)
- Language fixed to English (Rachel voice from ElevenLabs)
- Visual map display not optimized for accessibility
- Requires internet connection for all operations

Phase 2 Enhancements

- Continuous video stream analysis instead of single image snapshots
- Multi-language support with different ElevenLabs voices
- Advanced route deviation detection and re-routing
- User feedback and comment processing with AI responses
- Offline mode with pre-downloaded maps and routes
- Mobile app integration with haptic feedback and native OS features

Production Roadmap

- Drastically simplified interface (voice-first, minimal UI)
- Native mobile app for iOS and Android
- Accessibility audit and compliance (WCAG 2.1)
- Real blind user testing and feedback iteration
- Obstacle detection and warning system
- Integration with local transit schedules and information

Troubleshooting

Issue: "Cannot connect to localhost:3000"
Solution: Ensure Docker Compose services are running. Run `docker compose ps` to check status. If backend is down, run `docker compose logs backend` to see error details.

Issue: "API key not found" or "OpenAI API error"
Solution: Verify .env file exists in the project root with correct API keys. Check that OPENAI_API_KEY and ELEVENLABS_API_KEY are set. Restart containers after updating .env: `docker compose restart`.

Issue: "Geolocation permission denied"
Solution: Grant location permission in browser settings. On some browsers, geolocation requires HTTPS. Use a local HTTPS certificate (see docs/LOCAL_HTTPS.md).

Issue: "Speech recognition not working"
Solution: Check browser console (F12) for errors. Ensure microphone is not muted in browser settings. Grant microphone permission when prompted.

Issue: "No route found" or "Destination too far"
Solution: Try a destination closer to your current location (within 50 km). Ensure destination is a valid street address or landmark name.

Issue: "Cannot read properties of undefined"
Solution: Check browser console for full error trace. This typically indicates missing data from API response. Verify backend is responding correctly with `curl http://localhost:8000/api/health`.

Running Tests and Validation

Backend Testing

Run all backend tests:
cd backend
pytest -q

Run specific test file:
pytest tests/test_nlp.py -q

Run tests with coverage report:
pytest --cov=services --cov=api tests/

Frontend Testing

Run all frontend tests:
cd frontend
npm test

Run tests in watch mode (re-run on file changes):
npm test -- --watch

View coverage report:
npm run test:coverage

Linting

Check frontend code for style issues:
npm run lint

Building for Production

Backend

The backend Dockerfile is already configured for production. It installs dependencies and runs the FastAPI server.

Frontend

Build frontend for production:
cd frontend
npm run build

This creates an optimized build in the dist/ directory. Nginx serves this during `docker compose up`.

Contributing

This project was built during Hackathon 2025 as a proof of concept. Contributions and suggestions are welcome.

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with clear messages
4. Push to your branch and open a Pull Request

Code Review and Testing

All changes require:
- Backend: All existing tests pass, new code has tests with 80%+ coverage
- Frontend: All existing tests pass, visual regression testing recommended
- Documentation: Clear explanation of changes and how to test them

Architecture and Design Decisions

Why FastAPI and Uvicorn?

FastAPI provides automatic API documentation (Swagger UI), fast performance, and built-in support for async operations. Uvicorn is a production-grade ASGI server ideal for real-time operations like streaming audio.

Why React and Vite?

React is a mature framework for building interactive UIs. Vite provides fast development builds and optimized production bundles. Together they enable quick iteration and responsive user experiences.

Why OSRM for Routing?

OSRM is open-source and free to use via public servers. It provides pedestrian-optimized routes and returns detailed turn-by-turn instructions suitable for audio narration.

Why ElevenLabs for Voice?

ElevenLabs provides high-quality, natural-sounding voice synthesis. The Rachel voice is clear and easy to understand, even at natural reading speeds suitable for navigation.

Why Nominatim for Geocoding?

Nominatim is OpenStreetMap's free geocoding service. It handles varied address formats and is suitable for our use case of recognizing user-spoken addresses.

Error Handling Strategy

The application uses a multi-stage validation approach:
1. Frontend validates user input before sending to backend
2. Backend validates request format and coordinates
3. Backend checks for API errors and generates user-friendly audio responses
4. Frontend handles network errors gracefully with fallback messages

This prevents cascade failures and ensures users always receive clear, actionable feedback even when things go wrong.

License

This project was created during Hackathon 2025. Please see the LICENSE file for details (if included).

Contact and Support

For questions or issues, please open a GitHub issue or contact the project maintainers.

Key Team Insights

This application demonstrates that voice-first, AI-powered navigation is feasible and can significantly improve accessibility for visually impaired users. The combination of modern APIs (OpenAI, ElevenLabs, OSRM) makes building accessible technology more achievable than ever.

The architecture separates concerns cleanly: the backend handles all intelligence and API integration, while the frontend focuses on user interaction and audio playback. This separation makes both parts easy to test, maintain, and extend.
