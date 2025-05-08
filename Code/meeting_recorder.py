# Import libraries

import os
import datetime
import subprocess
import time
import signal
import sys


class WSLMeetingRecorder:
    def __init__(self, output_dir="recordings"):
        
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.recording_process = None
        self.output_file = None
        
        # WSL PulseAudio socket
        self.pulse_server = os.environ.get('PULSE_SERVER', 'unix:/mnt/wslg/PulseServer')
    
    def check_wsl_audio(self):
        """Check if WSL audio setup is working"""
        print("\nChecking WSL audio configuration...")
        
        # Check for WSL environment
        if not os.path.exists('/mnt/wslg'):
            print("Not running in WSL or WSLg not mounted. This script is designed for WSL.")
            return False
            
        # Check if the PULSE_SERVER environment variable is set
        print(f"PULSE_SERVER environment variable: {os.environ.get('PULSE_SERVER', 'Not set')}")
        
        # Check if the PulseServer socket exists
        if os.path.exists('/mnt/wslg/PulseServer'):
            print("WSLg PulseServer socket found.")
        else:
            print("WSLg PulseServer socket not found. Audio might not work.")
            
        # Try to list PulseAudio sources
        try:
            env = os.environ.copy()
            if 'PULSE_SERVER' not in env:
                env['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'
                
            sources = subprocess.check_output(
                ["pactl", "list", "sources", "short"], 
                env=env,
                stderr=subprocess.PIPE, 
                text=True
            )
            print("\nAvailable audio sources:")
            print(sources)
            
            sinks = subprocess.check_output(
                ["pactl", "list", "sinks", "short"], 
                env=env,
                stderr=subprocess.PIPE, 
                text=True
            )
            print("\nAvailable audio sinks (outputs):")
            print(sinks)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error listing audio devices: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error checking audio: {e}")
            return False
    
    def list_recording_devices(self):
        """List available recording devices"""
        try:
            # Set environment variables for PulseAudio
            env = os.environ.copy()
            if 'PULSE_SERVER' not in env:
                env['PULSE_SERVER'] = self.pulse_server
            
            # List audio devices using ffmpeg
            print("\nListing available audio devices with ffmpeg:")
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-sources", "pulse"], 
                env=env
            )
            
            # Try to get more detailed info with pactl
            print("\nDetailed PulseAudio sources:")
            subprocess.run(
                ["pactl", "list", "sources"], 
                env=env
            )
            
            return True
        except Exception as e:
            print(f"Error listing devices: {e}")
            return False
        
        def start_recording(self):
            """Start recording audio using ffmpeg with WSL PulseAudio configuration"""
        try:
            # Generate filename with current date
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = os.path.join(self.output_dir, f"meeting_{timestamp}.wav")
            
            print(f"\nStarting recording to {self.output_file}...")
            print("Press Ctrl+C to stop recording.")
            
            # Set environment variables for PulseAudio
            env = os.environ.copy()
            if 'PULSE_SERVER' not in env:
                env['PULSE_SERVER'] = self.pulse_server
            
            # Try to record with ffmpeg via PulseAudio
            cmd = [
                "ffmpeg",
                "-f", "pulse",
                "-i", "default",
                "-ac", "2",
                "-ar", "44100",
                self.output_file
            ]
            
            print(f"Command: {' '.join(cmd)}")
            print(f"Using PULSE_SERVER: {env.get('PULSE_SERVER')}")
            
            self.recording_process = subprocess.Popen(
                cmd, 
                env=env,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Check if the process started successfully
            time.sleep(1)
            if self.recording_process.poll() is not None:
                # Process already terminated
                stdout, stderr = self.recording_process.communicate()
                print(f"Recording process failed to start:")
                print(f"Error: {stderr.decode('utf-8')}")
                return False
            
            return True
            
        except Exception as e:
            print(f"\nError starting recording: {e}")
            return False
