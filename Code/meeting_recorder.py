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
            
    