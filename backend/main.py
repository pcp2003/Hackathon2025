"""
NaviAcess Backend - Main FastAPI Application
Voice navigation for visually impaired users
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from api import health_router, navigation_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NaviAcess API",
    description="AI-powered voice navigation for visually impaired users",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration - MUST be added before routes
# Allow requests from frontend running on different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",      # Self (for testing)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
    expose_headers=["*"],
)

# Serve static audio files
audio_dir = Path(__file__).parent / "audio_output"
audio_dir.mkdir(exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")

# Include routers
app.include_router(health_router)
app.include_router(navigation_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
