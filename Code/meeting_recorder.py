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