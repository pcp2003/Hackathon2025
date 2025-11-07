# 🧭 NaviAcess - Voice Navigation for Visually Impaired Users

NaviAcess is an AI-powered voice navigation assistant that empowers visually impaired people to navigate urban environments independently. Users simply speak their destination and receive real-time audio guidance—like "Waze for accessibility."

## ✨ Core Features

- **🎤 Voice Input**: Speak your destination naturally in your own words
- **📍 Auto-Location**: Uses your current GPS position automatically
- **🧠 Smart Routing**: AI calculates optimal accessible routes
- **🔊 Voice Guidance**: Real-time audio navigation instructions
- **🔄 Auto-Recalculation**: Updates route automatically if you deviate

## 🏗️ Tech Stack

### Frontend (React + Vite)
- **React 18** - Modern UI framework
- **Vite** - Fast development build tool
- **Leaflet + OpenStreetMap** - Visual map display
- **HTML5 Geolocation API** - Position tracking
- **Web Audio API** - Audio recording and playback

### Backend (FastAPI)
- **FastAPI** - High-performance Python web framework
- **ElevenLabs STT** - Speech-to-text conversion
- **OpenAI API** - Natural language processing
- **Nominatim** - Geocoding (place names to coordinates)
- **OSRM** - Open Source Routing Machine
- **ElevenLabs TTS** - Text-to-speech for navigation

## 🔄 How It Works

```
1. User speaks destination
   ↓
2. Audio captured and sent to backend with current location
   ↓
3. Speech-to-text converts audio to text
   ↓
4. NLP extracts destination name from natural language
   ↓
5. Geocoding gets destination coordinates
   ↓
6. Routing engine calculates optimal path
   ↓
7. Instructions generated step-by-step
   ↓
8. Text-to-speech creates audio guidance
   ↓
9. Frontend plays instructions and displays map
   ↓
10. Live tracking monitors position and recalculates if off-route
```

## 📁 Project Structure

```
NaviAcess/
├── backend/
│   ├── routes/              # API endpoints
│   │   ├── health.py        # Health check
│   │   └── navigation.py    # Navigation endpoints
│   ├── services/            # External integrations
│   │   ├── transcription.py # ElevenLabs STT
│   │   ├── nlp.py           # Destination extraction
│   │   ├── routing.py       # OSRM routing
│   │   └── text_to_speech.py# ElevenLabs TTS
│   ├── utils/               # Helper functions
│   │   └── helpers.py       # Distance calculations
│   ├── tests/               # Unit tests
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components
│   │   │   ├── VoiceInput.jsx
│   │   │   ├── Map.jsx
│   │   │   └── RouteDisplay.jsx
│   │   ├── services/        # API & location services
│   │   │   ├── apiClient.js
│   │   │   ├── locationService.js
│   │   │   └── audioService.js
│   │   ├── pages/           # App screens
│   │   │   └── App.jsx
│   │   ├── tests/           # Component tests
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── index.html           # HTML entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── vitest.config.js     # Test configuration
│   └── .env.example         # Environment template
│
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.9+
- Git

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - ELEVENLABS_API_KEY
   # - OPENAI_API_KEY
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v --cov=. --cov-report=term-missing
   ```

6. **Start backend server**
   ```bash
   python main.py
   # API will be available at http://localhost:8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if backend is on different URL
   ```

4. **Run tests**
   ```bash
   npm test
   ```

5. **Start development server**
   ```bash
   npm run dev
   # Frontend will be available at http://localhost:5173
   ```

## 📡 API Endpoints

### Health Check
```
GET /api/health
Response: { status: "healthy", version: "0.1.0" }
```

### Transcription
```
POST /api/transcribe
Body: FormData { audio: File }
Response: { text: string, confidence: float }
```

### Destination Analysis
```
POST /api/analyze
Body: FormData { text: string }
Response: { destination: string, latitude: float, longitude: float }
```

### Route Calculation
```
POST /api/route
Body: FormData { 
  origin_lat: float, 
  origin_lon: float,
  dest_lat: float, 
  dest_lon: float 
}
Response: { 
  steps: [...], 
  total_distance: float, 
  total_duration: float 
}
```

### Text-to-Speech
```
POST /api/speak
Body: FormData { text: string }
Response: { audio: blob, format: "mp3" }
```

### Location Update
```
POST /api/update-location
Body: FormData { 
  latitude: float, 
  longitude: float,
  destination_lat: float,
  destination_lon: float 
}
Response: { on_route: bool, needs_recalculation: bool }
```

## ✅ Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v                    # Run all tests
pytest tests/test_health.py -v      # Run specific test file
pytest --cov=. --cov-report=html    # Coverage report
```

### Frontend Tests
```bash
cd frontend
npm test                            # Run all tests
npm run test:coverage              # Coverage report
```

### Manual Testing Checklist
- [ ] Health endpoint responds
- [ ] Voice recording works
- [ ] Location access works
- [ ] Destination input processed
- [ ] Route displayed on map
- [ ] Audio guidance plays
- [ ] Route recalculates on location change

## 📋 Commit Documentation

Each commit has a dedicated documentation file in the `/docs` folder following the format:
- **Naming:** `commit-YYYY-MM-DD-description.md`
- **Example:** `commit-2025-11-07-initialize-base-project.md`

These files document:
- Changes made in that commit
- Files modified/created
- Tests added
- How to test the changes
- Important notes and decisions

See `/docs` folder for commit history.

## 🔑 Environment Variables

### Backend (.env)
```
ELEVENLABS_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 🤝 Contributing

This project follows strict development guidelines:

1. **Test First** - Write tests before implementing features
2. **Document Always** - Update README.md with changes
3. **Ask Permission** - Get user approval before major changes
4. **Code Coverage** - Maintain minimum 80% coverage

## 🚨 Known Limitations

- Backend services (STT, NLP, TTS) are placeholder implementations
- OSRM routing returns sample data
- Requires HTTPS for production (geolocation)
- Mobile browser support depends on device capabilities

## 🎯 Future Enhancements

- 🎧 Wearable device integration
- 🚧 Obstacle detection
- 📱 Offline mode support
- 🌍 Multi-language support
- 🦽 Accessibility improvements for all disabilities
- 🗺️ Custom route preferences
- 📞 Emergency contact integration

## 📄 License

This project is part of HackerRank2025 - A voice navigation solution for accessibility.

## 💡 Questions or Issues?

Please create a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, Node/Python versions)

---

**Made with ♿ for accessibility** - Empowering everyone to navigate independently.
