import os
import datetime
import glob
import json
import openai
from pathlib import Path
import subprocess

class InterviewProcessor:
    def __init__(self, recordings_dir="Recordings", output_dir="Output"):
        """Initialize the interview processor with default directories"""
        self.recordings_dir = recordings_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Set up OpenAI API (requires API key in environment variables)
        self.client = openai.OpenAI()
        
        # Validate API key
        self._validate_api_key()
        
    def _validate_api_key(self):
        """Validate that the OpenAI API key is set"""
        if not os.environ.get('OPENAI_API_KEY'):
            print("Warning: OPENAI_API_KEY not found in environment variables.")
            print("Please set your API key with: export OPENAI_API_KEY='your-api-key'")
            
    def find_todays_recording(self):
        """Find the recording file that matches today's date"""
        # Format date as YYYY-MM-DD to match the first 10 characters of the recording filename
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Get all mp3 files in the recordings directory
        all_files = glob.glob(os.path.join(self.recordings_dir, "*.mp3"))
        
        # Filter files where the first 10 characters match today's date
        matching_files = [f for f in all_files if os.path.basename(f)[:10] == today]
        
        if not matching_files:
            print(f"No recording found for today ({today}) in {self.recordings_dir}")
            return None
            
        # Sort by modification time to get the most recent one
        latest_file = max(matching_files, key=os.path.getmtime) 
        print(f"Found recording for today: {latest_file}")
        return latest_file
    
    def transcribe_audio(self, audio_file):
        """Transcribe the audio file using OpenAI Whisper API"""
        print(f"Transcribing audio file: {audio_file}")
        
        try:
            with open(audio_file, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    response_format="text"
                )
            
            print(f"Transcription completed: {len(transcription)} characters")
            return transcription
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None