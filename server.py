from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal
import uvicorn
from tts_engine import tts_engine
from utils import AUDIO_FORMAT_MIME_TYPES, clean_up_file

app = FastAPI(title="OpenAI Compatible TTS Server (pyttsx3)")

@app.get("/health")
@app.get("/healthz")
async def health_check():
    """
    Health check endpoint, returns server status.
    """
    try:
        return {
            "status": "healthy",
            "service": "OpenAI Compatible TTS Server (pyttsx3)"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

class SpeechRequest(BaseModel):
    model: str = Field(default="pyttsx3.drivers.nsss", description="The model to use for generating the audio.")
    input: str = Field(..., description="The text to generate audio for.")
    voice: str = Field(default="com.apple.voice.compact.zh-HK.Sinji", description="The voice to use for generating the audio.")
    response_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = Field(default="mp3", description="The format to return audio in.")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0, description="The speed of the generated audio.")

@app.post("/v1/audio/speech")
@app.post("/audio/speech") # Alias
async def generate_speech(
    request: SpeechRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generates audio from the input text.
    """
    
    try:
        output_file_path = tts_engine.generate_audio(
            text=request.input,
            voice_id=request.voice,
            speed=request.speed,
            output_format=request.response_format
        )
        
        mime_type = AUDIO_FORMAT_MIME_TYPES.get(request.response_format, "audio/mpeg")
        
        from starlette.background import BackgroundTask
        
        return FileResponse(
            output_file_path, 
            media_type=mime_type, 
            background=BackgroundTask(clean_up_file, output_file_path),
            filename=f"speech.{request.response_format}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/audio/models")
@app.get("/audio/models")
@app.get("/v1/models")
@app.get("/models")
async def list_models():
    """
    Lists the available models.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": tts_engine.get_driver(),
                "object": "model",
                "created": 0,
                "owned_by": "system"
            }
        ]
    }

@app.get("/v1/audio/voices")
@app.get("/audio/voices")
@app.get("/v1/voices")
async def list_voices():
    """
    Lists the available voices on the system.
    """
    voices = tts_engine.get_voices()
    return {"voices": voices}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
