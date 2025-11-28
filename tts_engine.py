import pyttsx3
import threading
import os
import subprocess
from typing import List, Dict, Optional
from utils import get_temp_file_path, clean_up_file

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.lock = threading.Lock()

    def get_driver(self):
        return self.engine.proxy._driver.__module__
        
    def get_voices(self) -> List[Dict]:
        """Returns a list of available voices."""
        voices = self.engine.getProperty('voices')
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
        return voice_list

    def generate_audio(self, text: str, voice_id: Optional[str], speed: float, output_format: str) -> str:
        """
        Generates audio from text using pyttsx3 and converts it to the requested format.
        Returns the path to the generated audio file.
        """
        with self.lock:
            if voice_id:
                try:
                    # if voice_id is alloy, use Sinji
                    if voice_id == "alloy" or voice_id == "af_alloy":
                        voice_id = "com.apple.voice.compact.zh-HK.Sinji"
                    self.engine.setProperty('voice', voice_id)
                except Exception as e:
                    print(f"Error setting voice {voice_id}: {e}")
                    # TODO: Add fallback to default voice
                    pass

            # Set speed (rate), mapping OpenAI speed to pyttsx3 rate
            base_rate = 200
            new_rate = int(base_rate * speed)
            self.engine.setProperty('rate', new_rate)

            # Generate to a temporary WAV/AIFF file first
            # macOS pyttsx3 usually saves as aiff or wav depending on implementation
            temp_input_path = get_temp_file_path("aiff") 
            
            try:
                self.engine.save_to_file(text, temp_input_path)
                self.engine.runAndWait()
            except Exception as e:
                clean_up_file(temp_input_path)
                raise RuntimeError(f"pyttsx3 generation failed: {e}")

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
