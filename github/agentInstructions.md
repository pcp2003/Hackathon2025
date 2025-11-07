🧭 NaviAcess - Voice Navigation for Visually Impaired Users
Overview
NaviAcess is an AI-powered voice assistant that helps visually impaired people navigate urban environments independently. Users speak their destination and receive real-time audio guidance—like "Waze for accessibility."
Core Features

Voice Input: Speak your destination naturally
Auto-Location: Uses your current position as starting point
Smart Routing: AI calculates optimal paths
Voice Guidance: Real-time audio navigation instructions
Auto-Recalculation: Updates route if you deviate

Tech Stack
Frontend (React + Vite)

Simple, accessible interface
HTML5 Geolocation for position tracking
Leaflet + OpenStreetMap for visual map
Audio recording and playback

Backend (FastAPI)

ElevenLabs STT: Voice → Text
NLP (OpenAI/spaCy): Extract destination
Nominatim: Place name → Coordinates
OSRM: Route calculation
ElevenLabs TTS: Navigation instructions → Voice

How It Works

User speaks destination
Audio captured and sent with current location to backend
Speech-to-text converts audio to text
NLP extracts destination name
Geocoding gets destination coordinates
Routing engine calculates path
Instructions generated step-by-step
Text-to-speech creates audio guidance
Frontend plays instructions and shows map
Live tracking monitors position and recalculates if needed

API Endpoints

POST /transcribe: Audio → Text
POST /analyze: Text → Destination + Coordinates
POST /route: Origin + Destination → Navigation steps
POST /speak: Text → Voice audio
POST /update-location: Track position & recalculate if off-route

Directory Structure
NaviAcess/
├── backend/
│   ├── routes/          # API endpoints
│   ├── services/        # External integrations
│   └── utils/           # Helper functions
├── frontend/
│   ├── components/      # UI elements
│   ├── services/        # API & location handling
│   └── pages/           # App screens
├── docs/                # Documentation for each commit
│   └── commit-YYYY-MM-DD-description.md
└── README.md            # Project overview and setup
Development Workflow Rules
🚨 CRITICAL: Documentation Rule Per Commit
EXACTLY ONE .md FILE PER COMMIT in /docs folder

✅ Create ONE file in /docs/ for each commit
✅ Naming format: commit-YYYY-MM-DD-short-description.md
✅ Example: commit-2024-11-07-added-transcribe-endpoint.md
❌ NEVER create multiple .md files in a single commit
❌ NEVER create .md files outside /docs/ folder (except README.md)

Documentation File Template (in /docs):
markdown# Commit: [Short Description]
Date: YYYY-MM-DD
Author: [Name]

## Changes Made
- List of changes
- What was implemented

## Files Modified/Created
- file1.py
- file2.tsx

## Tests Added
- test_feature.py: Tests X, Y, Z

## How to Test
Steps to verify the changes work

## Notes
Any important considerations or decisions made
🚨 MANDATORY: Before Every Commit

Run ALL tests - No commits without passing tests
Test manually - Verify the feature works as expected
Create ONE documentation file in /docs/ folder describing the commit
Ask user for approval - Present what will be committed (code + 1 doc file) and wait for confirmation
One commit = One approval - Each commit needs explicit user permission

✅ Testing Requirements

Write tests FIRST before implementing features (TDD approach)
Backend: Test each endpoint with pytest (success + error cases)
Frontend: Test components with Vitest/React Testing Library
Integration tests: Test full user flows (voice → route → guidance)
Minimum 80% code coverage for new code
Run tests before every commit: pytest (backend) and npm test (frontend)

📝 Documentation Rules - ABSOLUTE REQUIREMENTS

ONE .md per commit in /docs/ folder - no more, no less
Naming convention: commit-YYYY-MM-DD-description.md
Keep it concise: 200-500 words max per commit doc
Include: Changes made, files modified, tests added, how to test
README.md stays for project overview, setup, and general info only

🤝 User Approval Required Before:

Every single commit - Present changes + doc file, wait for "yes"
Major architectural changes (switching libraries, refactoring structure)
Adding new dependencies or external services
Changing API contracts or endpoint signatures
Deploying to any environment

💬 Decision-Making Protocol
When facing a choice, always ask the user:

"I can implement this using [Option A] or [Option B]. Which do you prefer?"
"Ready to commit these changes: [list code files] + docs/commit-YYYY-MM-DD-description.md. Proceed?"
"This requires adding dependency X. Proceed?"

📋 Commit Checklist (Must Complete Before Asking User)

 All tests pass (pytest and npm test)
 Manual testing completed
 Exactly ONE .md file created in /docs/
 Doc file follows naming: commit-YYYY-MM-DD-description.md
 No console.logs or debug code
 No commented-out code
 Code coverage ≥ 80%

Then ask user: "Ready to commit? Here's what will be committed: [list all files including the doc]"
⚠️ What NOT to Do

❌ NO commits without testing
❌ NO commits without ONE doc file in /docs/
❌ NO multiple .md files per commit
❌ NO commits without user approval
❌ NO "TODO" comments without GitHub issues
❌ NO commented-out code in commits
❌ NO console.logs or print statements in production code

Impact
Empowers visually impaired users with autonomous urban mobility through accessible AI technology.
Future Goals: Wearable integration, obstacle detection, offline mode, multi-language support.