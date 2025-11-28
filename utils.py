import os
import uuid
from typing import Optional

# Supported audio formats and their MIME types
AUDIO_FORMAT_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "opus": "audio/opus",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "audio/pcm",
}

def get_temp_file_path(extension: str = "wav") -> str:
    """Generates a unique temporary file path."""
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join(os.getcwd(), filename)

def clean_up_file(file_path: str):
    """Removes a file if it exists."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
