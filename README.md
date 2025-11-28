# OpenAI Compatible TTS Server (pyttsx3)

This project uses a local TTS engine powered by [pyttsx3](https://github.com/abdelkareem-s/pyttsx3) to generate audio from text. It implements the OpenAI TTS API and can be used as a drop-in replacement for the OpenAI TTS API.

## Features

- ✅ **OpenAI API Compatible**: Implements standard OpenAI TTS API endpoints
- 🔊 **Local Processing**: Uses system built-in TTS engine, no internet connection required
- 🎙️ **Multiple Voice Support**: Supports all available system voices
- 🎵 **Multiple Audio Formats**: Supports MP3, WAV, FLAC, AAC, Opus, and PCM
- ⚡ **Adjustable Speed**: Supports speed adjustment from 0.25x to 4.0x
- 🏥 **Health Check Endpoint**: Built-in health check API for monitoring and container deployment

## System Requirements

- Python 3.11 or higher
- FFmpeg (for audio format conversion)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd openai-pyttsx3
```

2. Install dependencies using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r pyproject.toml
```

## Starting the Server

```bash
uv run server.py
# or using python directly
python server.py
```

The server will start at `http://0.0.0.0:8100`.

## API Endpoints

### 1. Health Check

Check server status.

**Endpoints:**
- `GET /health`
- `GET /healthz`

**Response Example:**
```json
{
  "status": "healthy",
  "service": "OpenAI Compatible TTS Server (pyttsx3)"
}
```

### 2. Generate Speech

Convert text to speech.

**Endpoints:**
- `POST /v1/audio/speech`
- `POST /audio/speech`

**Request Parameters:**
```json
{
  "model": "pyttsx3.drivers.nsss",
  "input": "Hello, world!",
  "voice": "com.apple.voice.compact.zh-HK.Sinji",
  "response_format": "mp3",
  "speed": 1.0
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `pyttsx3.drivers.nsss` | TTS model (usually the system driver) |
| `input` | string | **Required** | The text to convert to speech |
| `voice` | string | `com.apple.voice.compact.zh-HK.Sinji` | Voice ID |
| `response_format` | string | `mp3` | Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` |
| `speed` | float | `1.0` | Speech speed (0.25 - 4.0) |

**Response:**
- Success: Returns audio file in the specified format
- Failure: HTTP 500 with error message

### 3. List Available Models

Get a list of available TTS models.

**Endpoints:**
- `GET /v1/audio/models`
- `GET /audio/models`
- `GET /v1/models`
- `GET /models`

**Response Example:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "pyttsx3.drivers.nsss",
      "object": "model",
      "created": 0,
      "owned_by": "system"
    }
  ]
}
```

### 4. List Available Voices

Get a list of all available system voices.

**Endpoints:**
- `GET /v1/audio/voices`
- `GET /audio/voices`
- `GET /v1/voices`

**Response Example:**
```json
{
  "voices": [
    {
      "id": "com.apple.voice.compact.zh-HK.Sinji",
      "name": "Sinji",
      "language": "zh-HK",
      "gender": "female"
    },
    {
      "id": "alloy",
      "name": "Alloy",
      "gender": "neutral",
      "language": "en-US"
    }
  ]
}
```

## Usage Examples

### cURL

```bash
# Generate speech
curl -X POST http://localhost:8100/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pyttsx3.drivers.nsss",
    "input": "Hello, world!",
    "voice": "com.apple.voice.compact.zh-HK.Sinji",
    "response_format": "mp3",
    "speed": 1.0
  }' \
  --output speech.mp3

# Health check
curl http://localhost:8100/health

# List available voices
curl http://localhost:8100/v1/audio/voices
```

## OpenWebUI Integration

This server is compatible with [OpenWebUI](https://github.com/open-webui/open-webui). In OpenWebUI settings:

1. Go to **Settings** → **Audio**
2. Set the TTS endpoint to: `http://localhost:8100/v1`
3. Select a voice (e.g., `com.apple.voice.compact.zh-HK.Sinji` or a system-supported voice ID)

## Project Structure

```
.
├── server.py         # FastAPI server main file
├── tts_engine.py     # TTS engine wrapper
├── utils.py          # Utility functions
├── pyproject.toml    # Project configuration and dependencies
└── README.md         # This file
```

## Development

### Running the Development Server

```bash
# Using uvicorn with auto-reload
uv run uvicorn server:app --reload --host 0.0.0.0 --port 4000
```

## Notes

- This project is primarily tested on macOS using the NSSpeechSynthesizer driver
- Different operating systems may have different available voices, checkout the [pyttsx3](https://github.com/nateshmbhat/pyttsx3?tab=readme-ov-file) documentation for more details
- Audio quality depends on the system's built-in TTS engine
- Some voices may not support all languages
- Special characters and symbols may affect speech synthesis

## Acknowledgments

- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Cross-platform text-to-speech engine
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenAI](https://platform.openai.com/docs/guides/text-to-speech) - API design reference
- [openai-edge-tts](https://github.com/travisvn/openai-edge-tts) - Reference implementation