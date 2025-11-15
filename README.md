# NaviAcess - Voice-Guided Navigation for the Visually Impaired

<div align="center">
  <img src="https://raw.githubusercontent.com/pcp2003/Hackathon2025/main/docs/landing-page.png" alt="NaviAcess Landing Page" width="600">
</div>

**"Waze for Accessibility"** – An AI-powered voice navigation system that empowers visually impaired users to navigate urban environments independently through natural voice commands and real-time audio guidance.

## Project Overview

**NaviAcess** is a proof-of-concept built during Portugal biggest AI Hackathon that demonstrates how modern AI APIs can be combined to create an accessible navigation experience.

### What It Does
Users **speak their destination naturally** (e.g., "Take me to Central Library"), and the system:
1. Transcribes the audio using ElevenLabs speech-to-text
2. Extracts the destination using OpenAI GPT-4o-mini NLP
3. Looks up coordinates using Nominatim geocoding
4. Validates the distance (must be < 50 km for OSRM routing)
5. Calculates an optimal pedestrian route
6. **Delivers turn-by-turn audio guidance** using ElevenLabs text-to-speech

Users can also **capture images** to get audio descriptions of their surroundings using GPT-4o-mini vision, helping them understand potential obstacles and hazards.

### Target Users
- Visually impaired individuals who want independent urban mobility
- People with low vision seeking accessible navigation
- Anyone who prefers voice-based rather than visual navigation

### Tech Stack
- **Backend:** FastAPI + Python (59 pytest tests)
- **Frontend:** React + Vite (48 Vitest tests)
- **AI Services:** OpenAI (NLP + Vision), ElevenLabs (STT + TTS)
- **Routing:** OSRM (Open Source Routing Machine)
- **Geocoding:** Nominatim (OpenStreetMap)
- **DevOps:** Docker Compose, Nginx

### Status
✅ **107 tests passing** (0 failures)  
✅ **Full audio pipeline working** (transcribe → analyze → route → speak)  
✅ **Image analysis implemented** (surroundings description + hazard detection)  
✅ **Production-ready error handling** (user-friendly audio messages)

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API Keys: [OpenAI](https://platform.openai.com/api-keys) + [ElevenLabs](https://elevenlabs.io/)

### Run It

```bash
git clone https://github.com/pcp2003/Hackathon2025.git
cd Hackathon2025

# Create .env with your API keys
cp .env.example .env
# Edit .env: OPENAI_API_KEY and ELEVENLABS_API_KEY

# Start
docker compose up --build

# Open: http://localhost:3000
```

That's it! Frontend at http://localhost:3000, API at http://localhost:8000

---

## How to Use

### Step 1: Grant Location Permission
Open the app and allow it to access your GPS location.

### Step 2: Record Your Destination
Click the **blue "Record" button** and speak naturally:
- *"Take me to Central Library"*
- *"Navigate to the train station"*
- *"I want the shopping mall downtown"*

### Step 3: Follow Audio Guidance
Listen to step-by-step instructions:
- *"Step 1: Start walking east on Main Street. 200 meters."*
- *"Step 2: Turn left onto Rua de Santa Justa. 150 meters."*

Click each step button to hear the audio guidance.

### Step 4: Analyze Surroundings (Optional)
Click **"Analyze Image"** to get audio description of what your camera sees:
- Describes the street environment
- Detects obstacles and hazards
- Provides safety alerts

---

## Core Features

| Feature | How It Works | Technology |
|---------|-------------|-----------|
| ** Voice Input** | Speak destination in natural language | ElevenLabs STT |
| ** AI Recognition** | Extracts destination from conversational speech | OpenAI GPT-4o-mini |
| ** Geolocation** | Tracks user position in real-time | HTML5 Geolocation API |
| ** Smart Routing** | Calculates optimal pedestrian paths | OSRM + Nominatim |
| ** Voice Output** | Delivers turn-by-turn instructions as speech | ElevenLabs TTS (Rachel) |
| ** Image Analysis** | Describes surroundings & detects hazards | GPT-4o-mini Vision |
| ** Error Handling** | Specific, actionable audio error messages | Custom validation logic |
| ** Accessibility** | Large buttons, touch-friendly, voice-first | React components |

---

## System Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React + Vite)                                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. useGeolocation()           → Get user's GPS coordinates      │
│ 2. VoiceInput.jsx             → Record user's voice             │
│ 3. Send audio to /api/transcribe                                │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTP request
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                               │
├─────────────────────────────────────────────────────────────────┤
│ POST /transcribe              → Audio file → ElevenLabs STT     │
│                                 Returns: { text, confidence }   │
│                                                                 │
│ POST /analyze                 → Text + User location            │
│   └─ OpenAI GPT-4o-mini: Extract destination name               │
│   └─ Nominatim: Convert address → Lat/Long coordinates          │
│   └─ Haversine: Check distance (must be < 50 km)                │
│   └─ Returns: { destination_address, latitude, longitude }      │
│                                                                 │
│ POST /route                   → Origin + Destination            │
│   └─ OSRM: Calculate pedestrian route                           │
│   └─ Returns: { steps[], total_distance, total_duration }       │
│                                                                 │
│ POST /speak-step (for each step)                                │
│   └─ ElevenLabs TTS: Convert instruction → Audio                │
│   └─ Returns: Binary WAV file                                   │
│                                                                 │
│ POST /analyze-image           → Image file                      │
│   └─ GPT-4o-mini Vision: Describe scene + detect hazards        │
│   └─ Convert to speech if needed                                │
│   └─ Returns: { description, danger_detected, danger_type }     │
│                                                                 │
│ GET /health                   → Application status check        │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTP responses
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React + Vite)                                         │
├─────────────────────────────────────────────────────────────────┤
│ Map.jsx           → Display route on Leaflet map (visual aid)   │
│ RouteDisplay.jsx  → Show each step with buttons                 │
│ playStepGuidance()→ Play audio for each step (TTS response)     │
│ EnableAudio.jsx   → Request microphone & speaker permissions    │
└─────────────────────────────────────────────────────────────────┘
```

### Error Handling Strategy

Multi-stage validation prevents cascade failures:

```
USER INPUT
    ↓
Frontend Validation (Microphone check, audio duration)
    ↓
API Call
    ↓
Backend Validation (Coordinates, distance check, API response checks)
    ↓
Service Integration (OpenAI, ElevenLabs, OSRM)
    ↓
Error Response Generation
    ↓
Convert Error to Audio Message
    ↓
Frontend Plays Audio Error to User
```

**Result:** Users always hear clear, actionable error messages instead of generic exceptions.

---

## Quality & Test Status

✅ **48 Frontend Tests Passing**
- 24 useNavigation tests (core routing logic)
- 24 ImageAnalyzer tests (image recognition)
- 0 failures, 4 skipped (hardware camera tests)

✅ **59 Backend Tests Passing**
- NLP & destination extraction
- Routing & distance validation
- Text-to-speech & audio generation
- Error handling & response formatting

✅ **Total: 107 Passing Tests** (0 failures)

### Test Coverage Areas
```
Backend Tests (59):
├── test_health.py          → Health check endpoints
├── test_nlp.py             → NLP extraction & geocoding
├── test_routing.py         → OSRM integration & distance checks
├── test_text_to_speech.py  → TTS audio generation
├── test_navigation.py      → Full API workflows
└── test_helpers.py         → Utility functions

Frontend Tests (48):
├── useNavigation.test.jsx  → Core hook logic (24 tests)
├── ImageAnalyzer.test.jsx  → Image upload & parsing (24 tests)
└── (4 skipped - require physical camera)
```

---

## API Endpoints Reference

### Core Navigation Pipeline

```
1. TRANSCRIBE (Audio → Text)
   POST /api/transcribe
   Input:  Audio file (WAV/MP3)
   Output: { "text": "Take me to...", "confidence": 0.95 }

2. ANALYZE (Text → Destination)
   POST /api/analyze
   Input:  { "text": "..." }
   Output: { "destination_address": "...", "latitude": 38.7369, "longitude": -9.1299 }
   
   Validation:
   - Must be a valid street address
   - Must not be > 50 km away (haversine check)
   - Nominatim geocoding must succeed

3. ROUTE (Destination → Steps)
   POST /api/route
   Input:  { "origin_lat": 38.7, "origin_lon": -9.1, 
             "dest_lat": 38.7369, "dest_lon": -9.1299 }
   Output: { "steps": [...], "total_distance": 5300, "total_duration": 1200 }
   
   Uses: OSRM service for pedestrian-optimized routing

4. SPEAK-STEP (Instruction → Audio)
   POST /api/speak-step
   Input:  { "instruction": "Turn left", "step_number": 1, 
             "language": "en" }
   Output: Binary WAV file
   
   Tech: ElevenLabs Rachel voice (English only in this version)
```

### Analysis Endpoint

```
ANALYZE-IMAGE (Image → Description)
POST /api/analyze-image
Input:  Image file (JPEG/PNG)
Output: { "description": "...", "danger_detected": false }

Uses: GPT-4o-mini vision to describe environment & detect hazards
```

### Health Check

```
HEALTH (Status check)
GET /api/health
Output: { "status": "healthy", "timestamp": "..." }
```

** Interactive API Docs:** http://localhost:8000/docs (Swagger UI)

---

## Project Structure

```
Hackathon2025/
│
├─ backend/                    # FastAPI Python Application
│  ├─ api/
│  │  ├─ navigation.py         # Core endpoints (POST /transcribe, /analyze, /route, etc)
│  │  └─ health.py             # GET /health endpoint
│  │
│  ├─ services/                # External service integrations
│  │  ├─ transcription.py      # ElevenLabs speech-to-text
│  │  ├─ nlp.py                # OpenAI NLP + Nominatim geocoding
│  │  ├─ routing.py            # OSRM routing service
│  │  ├─ text_to_speech.py     # ElevenLabs text-to-speech
│  │  └─ image_alert.py        # GPT-4o-mini vision for image analysis
│  │
│  ├─ schemas/                 # Pydantic validation schemas
│  │  ├─ navigation.py         # Request/response models
│  │  └─ health.py             # Health check model
│  │
│  ├─ tests/                   # 59 pytest tests
│  │  ├─ test_nlp.py
│  │  ├─ test_routing.py
│  │  ├─ test_text_to_speech.py
│  │  └─ ...
│  │
│  ├─ utils/
│  │  └─ helpers.py            # Utility functions
│  │
│  ├─ main.py                  # FastAPI app initialization & CORS setup
│  ├─ requirements.txt
│  └─ Dockerfile
│
├─ frontend/                   # React + Vite Application
│  ├─ src/
│  │  ├─ pages/
│  │  │  └─ App.jsx            # Main app layout
│  │  │
│  │  ├─ components/           # React components
│  │  │  ├─ VoiceInput.jsx     # Record button
│  │  │  ├─ Map.jsx            # Leaflet map display
│  │  │  ├─ RouteDisplay.jsx   # Step-by-step route UI
│  │  │  ├─ ImageAnalyzer.jsx  # Camera & image upload
│  │  │  └─ EnableAudio.jsx    # Permissions request
│  │  │
│  │  ├─ hooks/                # Custom React hooks
│  │  │  ├─ useNavigation.js   # Core routing logic (24 tests)
│  │  │  ├─ useGeolocation.js  # GPS tracking
│  │  │  └─ useAudio.js        # Audio playback control
│  │  │
│  │  ├─ services/
│  │  │  └─ api.js             # Axios client to backend
│  │  │
│  │  ├─ styles/               # CSS styling
│  │  └─ tests/                # 24 Vitest tests
│  │
│  ├─ vite.config.js
│  ├─ vitest.config.js
│  ├─ package.json
│  ├─ Dockerfile
│  └─ nginx.conf               # Production serving config
│
├─ docs/
│  ├─ agentInstructions.md     # This development workflow
│  ├─ commit-YYYY-MM-DD-*.md   # 21+ commit documentation files
│  └─ LOCAL_HTTPS.md           # HTTPS setup for local testing
│
├─ docker/
│  └─ certs/                   # SSL certificates (local HTTPS)
│     ├─ cert.pem
│     ├─ key.pem
│     └─ rootCA.pem
│
├─ docker-compose.yml          # Service orchestration
├─ .env.example                # Environment template
└─ README.md                   # This file
```

---

## Running Tests

```bash
# Backend
cd backend && pytest -q

# Frontend
cd frontend && npm test
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Cannot connect to localhost:3000** | Run `docker compose ps` to check services. If down, restart with `docker compose up` |
| **API key errors** | Verify `.env` file with `OPENAI_API_KEY` and `ELEVENLABS_API_KEY`. Restart: `docker compose restart` |
| **Geolocation denied** | Grant location permission in browser settings. Some browsers require HTTPS (see docs/LOCAL_HTTPS.md) |
| **Microphone not working** | Check browser console (F12). Grant microphone permission. Ensure microphone is not muted. |
| **Destination too far / No route** | OSRM only routes within 50 km. Try a closer destination. |
| **Backend 500 error** | Check logs: `docker compose logs backend`. Common causes: invalid API key, rate limit, network timeout. |
| **Frontend not loading** | Clear browser cache. Check: `docker compose logs frontend`. Ensure port 3000 is free. |
| **Audio not playing** | Check speaker is enabled. Verify browser allows audio playback. Check console for errors. |

### Common Error Messages

```
"I did not hear anything useful. Please try again."
→ Microphone recorded no sound. Speak louder or re-record.

"I could not understand the destination. Please try again."
→ GPT-4o-mini couldn't extract a destination. Be more specific.

"Destination is too far away. Please try a closer location."
→ Destination is > 50 km away. OSRM has distance limits.

"Could not find a route. Please try a different location."
→ No pedestrian route exists. Try another destination.

"Service is temporarily unavailable. Please try again in a moment."
→ External API (OpenAI, ElevenLabs, OSRM) is down. Wait and retry.
```

---

## Setup & Installation

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔧 Configuration

Create `.env` in project root:
```env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=sk_...
```

Don't commit to git (already in `.gitignore`).

---

## Development Workflow

This project follows a **strict commit protocol** documented in [`docs/agentInstructions.md`](./docs/agentInstructions.md):

### Commit Requirements

✅ **Before Every Commit:**
1. All tests pass (backend: pytest, frontend: npm test)
2. Manual testing completed
3. Create exactly ONE `.md` file in `/docs/commits/`
4. Filename format: `commit-YYYY-MM-DD-description.md`
5. No console.logs, debug code, or commented-out code
6. Code coverage ≥ 80% for new code

### Commit Documentation Template

Each commit gets one documentation file:

```markdown
# Commit: [Feature Description]
Date: YYYY-MM-DD
Author: [Your Name]

## Changes Made
- What was implemented

## Files Modified/Created
- file1.py
- file2.jsx

## Tests Added
- Description of tests

## How to Test
Steps to verify the changes work

## Notes
Important decisions or considerations
```

### Commit History

All 21+ commits are documented in `/docs/commits/`:
- Most recent: `commit-2025-11-09-force-english-tts.md`
- Session summary: `session-summary-2025-11-09.md`
- Code audit: `code-audit-unused-features.md`

**Review:** `ls docs/commits/` to see full history.

### Testing Requirements (TDD)

- **Write tests FIRST** before implementing features
- **Backend:** pytest with both success and error cases
- **Frontend:** Vitest with React Testing Library
- **Integration tests:** Full user workflows (voice → route → guidance)
- **Minimum 80% coverage** for new code
- **Run full test suite** before every commit

### User Approval

**Every commit requires explicit user approval:**

1. AI presents changes + doc file
2. User reviews code and documentation
3. User says "yes" or requests modifications
4. Only then is code committed

---

## Current Version Status

**This is a DEMO version** built during Hackathon 2025.

**Current Features:**
- ✅ Voice input and audio guidance
- ✅ Full navigation pipeline (transcribe → analyze → route → speak)
- ✅ Image analysis (surroundings description + hazard detection)
- ✅ Visual map display with route
- ✅ 107 tests passing with 0 failures

**Future Enhancements:**
- Video stream analysis (not single images)
- Multi-language support
- Native mobile apps (iOS/Android)
- Offline mode
- Advanced obstacle detection

---

## Known Limitations

- Max 50 km route distance (OSRM limitation)
- English only (single voice configured)
- Single image analysis (not continuous video)
- Requires internet connection
- Browser-based (not native app)

---

## Roadmap & Future Work

### Phase 2: Enhanced Navigation
- Continuous video stream analysis (not single images)
- Multi-language support with different voices
- Advanced route deviation detection
- Offline mode with pre-downloaded maps

### Phase 3: Mobile & Accessibility
- Native iOS app
- Native Android app
- WCAG 2.1 accessibility compliance
- Real user testing with blind users

### Phase 4: Advanced Features
- AI-powered user feedback
- Analytics and error tracking
- Haptic feedback (vibration alerts)
- Transit schedule integration

---

## Contributing

**Fork → Create branch → Write tests → Implement → Run tests → Commit → PR**

Details: [`docs/agentInstructions.md`](./docs/agentInstructions.md)

**Requirements:**
- All tests pass: `pytest -q` (backend), `npm test` (frontend)
- One `.md` doc per commit in `/docs/commits/` (format: `commit-YYYY-MM-DD-description.md`)

---

**Built with ❤️ during Hackathon 2025** • [`Full commit history`](./docs/commits/)
