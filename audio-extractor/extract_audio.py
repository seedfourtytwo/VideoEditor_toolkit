#!/usr/bin/env python3
"""
Audio Extractor

A robust Python module for extracting audio from video files, with support for batch processing
and handling of special characters in filenames.

Features:
- Extract audio in multiple formats (WAV, MP3, AAC)
- Batch processing of multiple video files
- Support for recursive directory processing
- Automatic handling of special characters in filenames
- Progress bar and detailed status updates
- Time segment extraction support
- Configurable audio bitrate

Supported video formats:
- MP4 (.mp4)
- Matroska (.mkv)
- AVI (.avi)
- QuickTime (.mov)
- Flash Video (.flv)
- Windows Media (.wmv)

Supported audio formats:
- WAV (default, high quality uncompressed)
- MP3 (compressed, good for music)
- AAC (compressed, good for speech)

Requirements:
- FFmpeg must be installed and accessible in system PATH
- Python 3.7 or higher
- moviepy library
- Additional dependencies listed in requirements.txt

Usage examples:
    # Extract audio from a single video
    python extract_audio.py video.mp4

    # Extract audio from multiple videos
    python extract_audio.py video1.mp4 video2.mkv

    # Process all videos in a directory
    python extract_audio.py /path/to/videos/

    # Extract audio in MP3 format with custom bitrate
    python extract_audio.py video.mp4 --format mp3 --bitrate 320k

    # Extract a specific time segment
    python extract_audio.py video.mp4 --start 10.5 --end 20.5

    # Process all videos in the default output directory
    python extract_audio.py
"""

import os
import argparse
import sys
from pathlib import Path
import re
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.config as mpconfig
import tempfile
import wave
import contextlib
import tqdm
from proglog import TqdmProgressBarLogger

# Configure moviepy to be less verbose
mpconfig.VERBOSE = False

def sanitize_filename(filename):
    """
    Sanitize filename by replacing problematic characters with standard ASCII equivalents.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace full-width characters with their regular equivalents
    filename = filename.replace('？', '?')
    filename = filename.replace('！', '!')
    filename = filename.replace('"', '"')
    filename = filename.replace('"', '"')
    filename = filename.replace('：', ':')
    
    # Remove or replace other problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove trailing spaces and periods
    filename = filename.strip('. ')
    
    return filename

def check_ffmpeg():
    """Check if FFmpeg is installed and in system PATH."""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        if result.returncode == 0:
            print("FFmpeg is installed")
            return True
        else:
            print("FFmpeg is not installed correctly")
            return False
    except FileNotFoundError:
        print("FFmpeg is not installed")
        print("Please install FFmpeg and add it to your system PATH")
        return False
    except Exception as e:
        print(f"Error checking FFmpeg: {str(e)}")
        return False

def create_output_dir(directory):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_audio(video_path, output_path=None, audio_format='wav', bitrate='192k', start_time=None, end_time=None):
    """
    Extract audio from a video file.
    
    Args:
        video_path (str): Path to the input video file
        output_path (str, optional): Path to save the extracted audio. If None, uses the central output directory.
        audio_format (str, optional): Output audio format ('wav', 'mp3', 'aac'). Defaults to 'wav'.
        bitrate (str, optional): Output audio bitrate. Defaults to '192k'.
        start_time (float, optional): Start time to extract audio from in seconds. Defaults to None (beginning).
        end_time (float, optional): End time to extract audio to in seconds. Defaults to None (end).
    
    Returns:
        str: Path to the extracted audio file
    """
    # Validate input file
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Create default output path if not provided
    if output_path is None:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        # Check if filename needs sanitization
        sanitized_name = sanitize_filename(video_name)
        if sanitized_name != video_name:
            print(f"\nNote: Output filename will be sanitized:")
            print(f"  Original: {video_name}")
            print(f"  Sanitized: {sanitized_name}")
        video_name = sanitized_name
        # Use central output directory instead of input directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        output_path = os.path.join(output_dir, f"{video_name}.{audio_format}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        create_output_dir(output_dir)
    
    # Load the video file while suppressing output
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            video = VideoFileClip(video_path)
        finally:
            sys.stdout = old_stdout
    
    # Print initial information
    print("\nAudio Extraction Task:")
    print(f"Input:  {os.path.abspath(video_path)}")
    print(f"Output: {os.path.abspath(output_path)}")
    print(f"Format: {audio_format.upper()} ({bitrate})")
    print(f"Length: {video.duration:.2f} seconds")
    print("-" * 50)
    
    # Apply time slicing if specified
    if start_time is not None or end_time is not None:
        start_time = 0 if start_time is None else start_time
        end_time = video.duration if end_time is None else end_time
        video = video.subclip(start_time, end_time)
        print(f"Extracting segment: {start_time}s to {end_time}s")
    
    # Extract the audio
    audio = video.audio
    
    try:
        # Configure progress bar
        print("Extracting audio...")
        logger = TqdmProgressBarLogger(print_messages=False)  # Suppress additional messages
        
        # Write the audio file
        audio.write_audiofile(
            output_path,
            bitrate=bitrate,
            codec=get_codec_for_format(audio_format),
            logger=logger
        )
    finally:
        video.close()
    
    print(f"\nAudio extracted successfully!")
    return output_path

def get_codec_for_format(audio_format):
    """Get the appropriate codec for the specified audio format."""
    audio_format = audio_format.lower()
    if audio_format == 'wav':
        return 'pcm_s16le'  # Standard WAV codec
    elif audio_format == 'mp3':
        return 'libmp3lame'  # MP3 codec
    elif audio_format == 'aac':
        return 'aac'  # AAC codec
    else:
        return None  # Let MoviePy decide based on extension

def process_batch(input_dir, output_dir=None, audio_format='wav', bitrate='192k', recursive=False):
    """
    Process a batch of video files in a directory.
    
    Args:
        input_dir (str): Input directory containing video files
        output_dir (str, optional): Output directory for extracted audio files. If None, uses central output directory.
        audio_format (str, optional): Output audio format. Defaults to 'wav'.
        bitrate (str, optional): Output audio bitrate. Defaults to '192k'.
        recursive (bool, optional): Whether to process subdirectories. Defaults to False.
    """
    # Validate input directory
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
    
    # Set default output directory if not provided
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    
    # Create output directory if it doesn't exist
    create_output_dir(output_dir)
    
    # Get list of video files
    video_files = []
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
    
    if recursive:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    try:
                        # Test if the filename can be encoded
                        file.encode('ascii')
                        video_files.append(os.path.join(root, file))
                    except UnicodeEncodeError:
                        sanitized_name = sanitize_filename(file)
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(root, sanitized_name)
                        print(f"\nWarning: Found filename with special characters:")
                        print(f"  Original: {file}")
                        print(f"  Sanitized: {sanitized_name}")
                        try:
                            os.rename(old_path, new_path)
                            print(f"Successfully renamed the file.")
                            video_files.append(new_path)
                        except OSError as e:
                            print(f"Error: Could not automatically rename the file.")
                            print(f"Please manually rename the file to: {sanitized_name}")
    else:
        for file in os.listdir(input_dir):
            if file.lower().endswith(video_extensions):
                try:
                    # Test if the filename can be encoded
                    file.encode('ascii')
                    video_files.append(os.path.join(input_dir, file))
                except UnicodeEncodeError:
                    sanitized_name = sanitize_filename(file)
                    old_path = os.path.join(input_dir, file)
                    new_path = os.path.join(input_dir, sanitized_name)
                    print(f"\nWarning: Found filename with special characters:")
                    print(f"  Original: {file}")
                    print(f"  Sanitized: {sanitized_name}")
                    try:
                        os.rename(old_path, new_path)
                        print(f"Successfully renamed the file.")
                        video_files.append(new_path)
                    except OSError as e:
                        print(f"Error: Could not automatically rename the file.")
                        print(f"Please manually rename the file to: {sanitized_name}")
    
    if not video_files:
        print(f"No video files found in: {input_dir}")
        return
    
    print(f"Found {len(video_files)} video file(s) to process")
    
    # Process each video file
    for video_file in video_files:
        # Create output path with same relative structure as input
        rel_path = os.path.relpath(video_file, input_dir)
        rel_dir = os.path.dirname(rel_path)
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        
        if rel_dir:
            out_subdir = os.path.join(output_dir, rel_dir)
            create_output_dir(out_subdir)
            out_path = os.path.join(out_subdir, f"{base_name}.{audio_format}")
        else:
            out_path = os.path.join(output_dir, f"{base_name}.{audio_format}")
        
        try:
            extract_audio(video_file, out_path, audio_format, bitrate)
            print("")  # Add a blank line between files for better readability
        except Exception as e:
            print(f"Error processing {video_file}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Extract audio from video files")
    
    # Main arguments
    parser.add_argument("input", nargs='*', help="Input video file(s) or directory. If not specified, processes all videos in the output directory.")
    parser.add_argument("--output", "-o", help="Output audio file or directory (default: central output directory)")
    parser.add_argument("--format", "-f", default="wav", choices=["wav", "mp3", "aac"], 
                        help="Output audio format (default: wav)")
    parser.add_argument("--bitrate", "-b", default="192k", 
                        help="Output audio bitrate (default: 192k)")
    
    # Advanced options
    parser.add_argument("--start", "-s", type=float,
                        help="Start time in seconds for extraction (for single file only)")
    parser.add_argument("--end", "-e", type=float,
                        help="End time in seconds for extraction (for single file only)")
    parser.add_argument("--recursive", "-r", action="store_true", 
                        help="Process subdirectories when input is a directory")
    
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # If no input is specified, use the default output directory
    if not args.input:
        default_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        if not os.path.exists(default_dir):
            print(f"Error: Default directory not found: {default_dir}")
            sys.exit(1)
        print(f"No input specified. Processing all videos in: {default_dir}")
        process_batch(default_dir, args.output, args.format, args.bitrate, args.recursive)
        return
    
    # Process each input path
    for input_path in args.input:
        if os.path.isfile(input_path):
            try:
                extract_audio(input_path, args.output, args.format, args.bitrate, args.start, args.end)
            except Exception as e:
                print(f"Error processing {input_path}: {str(e)}")
        elif os.path.isdir(input_path):
            try:
                process_batch(input_path, args.output, args.format, args.bitrate, args.recursive)
            except Exception as e:
                print(f"Error processing directory {input_path}: {str(e)}")
        else:
            print(f"Error: Input path not found: {input_path}")

if __name__ == "__main__":
    main() 