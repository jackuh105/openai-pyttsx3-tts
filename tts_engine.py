import os
import pyttsx3
import subprocess
from typing import List, Dict, Optional
from utils import get_temp_file_path, clean_up_file

import multiprocessing
import traceback

def _run_tts_process(text: str, voice_id: Optional[str], speed: float, output_path: str):
    """
    Function to run in a separate process. Initializes a fresh engine instance,
    generates audio, and saves it to the output path.
    """
    try:
        engine = pyttsx3.init()
        
        if voice_id:
            try:
                # if voice_id is alloy, use Sinji
                if voice_id == "alloy" or voice_id == "af_alloy":
                    voice_id = "com.apple.voice.compact.zh-HK.Sinji"
                engine.setProperty('voice', voice_id)
            except Exception as e:
                print(f"Error setting voice {voice_id}: {e}")
                pass

        # Set speed (rate), mapping OpenAI speed to pyttsx3 rate
        base_rate = 200
        new_rate = int(base_rate * speed)
        engine.setProperty('rate', new_rate)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
    except Exception as e:
        print(f"Process error: {e}")
        traceback.print_exc()
        raise e

class TTSEngine:
    def __init__(self):
        # We don't initialize the engine here for generation anymore
        # But we might need it for listing voices.
        # However, initializing it here might still cause issues if we spawn processes.
        # For safety, we'll initialize it on-demand for listing voices, or just once.
        pass

    def get_driver(self):
        # This is a bit tricky without an engine instance. 
        # We'll create a temporary one just to get the driver name.
        try:
            engine = pyttsx3.init()
            driver = engine.proxy._driver.__module__
            del engine
            return driver
        except:
            return "unknown"
        
    def get_voices(self) -> List[Dict]:
        """Returns a list of available voices."""
        # We create a fresh instance to get voices
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_list = []
        for voice in voices:
            voice_list.append({
                "id": voice.id,
                "name": voice.name,
                "language": voice.languages[0],
                "gender": voice.gender
            })
        # adding Alloy to the list for OpenWebUI compatibility
        voice_list.append({
            "id": "alloy",
            "name": "Alloy",
            "gender": "neutral",
            "language": "en-US"
        })
        del engine
        return voice_list

    def generate_audio(self, text: str, voice_id: Optional[str], speed: float, output_format: str) -> str:
        """
        Generates audio from text using pyttsx3 in a separate process and converts it to the requested format.
        Returns the path to the generated audio file.
        """
        
        # Generate to a temporary WAV/AIFF file first
        # macOS pyttsx3 usually saves as aiff or wav depending on implementation
        temp_input_path = get_temp_file_path("aiff") 
        
        # Run generation in a separate process
        process = multiprocessing.Process(
            target=_run_tts_process,
            args=(text, voice_id, speed, temp_input_path)
        )
        process.start()
        process.join(timeout=30) # 30 seconds timeout
        
        if process.is_alive():
            process.terminate()
            clean_up_file(temp_input_path)
            raise RuntimeError("TTS generation timed out")
            
        if process.exitcode != 0:
            clean_up_file(temp_input_path)
            raise RuntimeError(f"TTS generation process failed with exit code {process.exitcode}")

        if not os.path.exists(temp_input_path):
             raise RuntimeError("pyttsx3 failed to create output file")
        
        # check generated file size
        input_size = os.path.getsize(temp_input_path)
        print(f"Generated temp file: {temp_input_path}, size: {input_size} bytes")
        
        if input_size < 100:
            print("Warning: Generated file is very small!")
        
        final_output_path = get_temp_file_path(output_format)
        
        # Format conversion using ffmpeg
        try:
            command = [
                'ffmpeg',
                '-y', # Overwrite output file
                '-i', temp_input_path,
                final_output_path
            ]
            
            # Suppress ffmpeg output unless error
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            
            output_size = os.path.getsize(final_output_path)
            print(f"Converted file: {final_output_path}, size: {output_size} bytes")
            
        except subprocess.CalledProcessError as e:
            clean_up_file(temp_input_path)
            clean_up_file(final_output_path)
            raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}")
        finally:
            # Clean up the intermediate file
            clean_up_file(temp_input_path)

        return final_output_path

# Global instance
tts_engine = TTSEngine()
