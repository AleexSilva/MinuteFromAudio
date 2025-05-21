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
    
    def analyze_transcription(self, transcription):
        """Analyze transcription to generate meeting minutes and summary"""
        print("Analyzing transcription with LLM...")
        
        # Prompt for detailed minutes
        minutes_prompt = """
        You are an expert assistant helping to create detailed meeting minutes from an interview transcript.
        This is a recruiting interview between a candidate and recruiter.
        
        Please extract and organize information into these sections:
        1. ABOUT THE COMPANY: Details about the hiring company and any third party recruiters
        2. ROLE/POSITION DETAILS: Specific job requirements, responsibilities, team structure
        3. BENEFITS: Salary, perks, work environment, growth opportunities, etc.
        4. CANDIDATE BACKGROUND: Brief professional history, skills, and experience
        
        Format the output as detailed meeting minutes highlighting key points of discussion.
        Use clean, professional formatting with section headings, bullet points where appropriate.
        """
        
        # Prompt for concise summary
        summary_prompt = """
        You are an expert assistant helping to create a concise summary from an interview transcript.
        This is a recruiting interview between a candidate and recruiter.
        
        Please create a brief summary (maximum 500 words) that highlights:
        1. ABOUT THE COMPANY: Key details about the hiring company and any third party recruiters
        2. ROLE/POSITION DETAILS: Core responsibilities and requirements
        3. BENEFITS: Most important benefits and perks
        4. CANDIDATE BACKGROUND: Relevant highlights from the candidate's background
        
        Format the output as a concise executive summary focusing only on essential information.
        """
        try:
            # Generate minutes
            minutes_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": minutes_prompt},
                    {"role": "user", "content": transcription}
                ]
            )
            
            # Generate summary
            summary_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": transcription}
                ]
            )
            
            minutes = minutes_response.choices[0].message.content
            summary = summary_response.choices[0].message.content
            
            return {
                "minutes": minutes,
                "summary": summary
            }
        except Exception as e:
            print(f"Error analyzing transcription: {e}")
            return None
        
    def generate_html_files(self, content):
        """Generate HTML files for minutes and summary"""
        today_date = datetime.datetime.now().strftime("%d%m%Y")
        output_folder = os.path.join(self.output_dir, f"daily-{today_date}")
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # HTML template
        html_template = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #3498db;
                    margin-top: 20px;
                }}
                .date {{
                    color: #7f8c8d;
                    font-style: italic;
                }}
                .content {{
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="date">Generated on {date}</div>
            <div class="content">
                {content}
            </div>
        </body>
        </html>
        """

        # Format date for display
        display_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        # Create minutes HTML
        minutes_html = html_template.format(
            title="Interview Minutes",
            date=display_date,
            content=content["minutes"].replace("\n", "<br>")
        )
        
        # Create summary HTML
        summary_html = html_template.format(
            title="Interview Summary",
            date=display_date,
            content=content["summary"].replace("\n", "<br>")
        )

        # Write files
        minutes_path = os.path.join(output_folder, "minutes.html")
        summary_path = os.path.join(output_folder, "summary.html")
        
        with open(minutes_path, "w") as f:
            f.write(minutes_html)
            
        with open(summary_path, "w") as f:
            f.write(summary_html)


        print(f"Generated HTML files in {output_folder}:")
        print(f"- Minutes: {minutes_path}")
        print(f"- Summary: {summary_path}")
        
        return {
            "minutes_path": minutes_path,
            "summary_path": summary_path
        }
