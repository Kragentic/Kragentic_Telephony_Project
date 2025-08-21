from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from stt_service import STTService
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Orchestrator Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize STT service
stt_service = STTService()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-orchestrator"}

@app.post("/api/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file."""
    try:
        audio_data = await file.read()
        result = await stt_service.transcribe_audio_file(audio_data, file.content_type)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/api/stt/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio transcription."""
    await websocket.accept()
    
    async def audio_generator():
        while True:
            try:
                data = await websocket.receive_bytes()
                yield data
            except WebSocketDisconnect:
                break
    
    try:
        async for result in stt_service.transcribe_audio_stream(audio_generator()):
            await websocket.send_text(json.dumps(result))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

@app.post("/api/stt/test")
async def test_stt():
    """Test endpoint for STT functionality."""
    return {
        "message": "STT service is running",
        "supported_formats": ["wav", "mp3", "flac"],
        "features": ["real-time transcription", "profanity filtering", "Google Speech API"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
