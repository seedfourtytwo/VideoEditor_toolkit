#!/usr/bin/env python3
import os
import argparse
import whisper
from pathlib import Path
from tqdm import tqdm
import logging
import time
import warnings
import sys
import signal
import threading
import _thread

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore"

# Configure logging with a simpler format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Global flag for handling interrupts
interrupted = False

def force_exit():
    """Force exit the program"""
    _thread.interrupt_main()
    os._exit(1)

def signal_handler(signum, frame):
    """Handle interrupt signal"""
    global interrupted
    if interrupted:  # If already interrupted once, force exit
        print("\n\nForced exit.")
        force_exit()
    interrupted = True
    print("\n\nTranscription interrupted by user. Press Ctrl+C again to force quit...\n")
    # Set a timer to force exit if cleanup takes too long
    threading.Timer(5.0, force_exit).start()

# Set up the signal handler
signal.signal(signal.SIGINT, signal_handler)

def format_time(seconds):
    """Convert seconds to a human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes)} minutes {int(seconds)} seconds"

class AudioTranscriber:
    # Supported audio formats
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = {'txt', 'srt', 'vtt', 'json'}
    
    # TODO: Future video format support
    # SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mkv', '.avi', '.mov', '.webm'}
    
    def __init__(self, model_name="base"):
        """
        Initialize the transcriber with specified model.
        Args:
            model_name (str): Whisper model name ('tiny', 'base', 'small', 'medium', 'large')
        """
        print(f"\nLoading {model_name} model...")
        with tqdm(total=100, desc="Loading model", unit="%") as pbar:
            self.model = whisper.load_model(model_name)
            pbar.update(100)
        print("Model loaded successfully!\n")

    def format_timestamp(self, seconds):
        """Convert seconds to SRT/VTT timestamp format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"

    def save_as_srt(self, segments, output_path, word_timestamps=False):
        """Save transcription in SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            counter = 1
            if not segments:
                print("Warning: No segments found in transcription result")
                return
            
            for seg in segments:
                if word_timestamps and 'words' in seg:
                    # Process word-level timestamps
                    words = seg['words']
                    
                    for word in words:
                        if not isinstance(word, dict):
                            continue
                            
                        word_text = str(word.get('word', '')).strip()
                        word_start = word.get('start', None)
                        word_end = word.get('end', None)
                        
                        if word_text and word_start is not None and word_end is not None:
                            try:
                                start_time = self.format_timestamp(float(word_start))
                                end_time = self.format_timestamp(float(word_end))
                                f.write(f"{counter}\n{start_time} --> {end_time}\n{word_text}\n\n")
                                counter += 1
                            except Exception as e:
                                print(f"Error writing word timestamp: {str(e)}")
                else:
                    # Regular segment-level timestamps
                    start_time = self.format_timestamp(seg['start'])
                    end_time = self.format_timestamp(seg['end'])
                    text = seg['text'].strip()
                    if text:
                        f.write(f"{counter}\n{start_time} --> {end_time}\n{text}\n\n")
                        counter += 1

    def save_as_vtt(self, segments, output_path, word_timestamps=False):
        """Save transcription in VTT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for seg in segments:
                if word_timestamps and 'words' in seg:
                    # Process word-level timestamps
                    for word in seg['words']:
                        if isinstance(word, dict) and 'start' in word and 'end' in word:
                            text = word.get('text', '').strip()
                            if text:
                                start_time = self.format_timestamp(word['start']).replace(',', '.')
                                end_time = self.format_timestamp(word['end']).replace(',', '.')
                                f.write(f"{start_time} --> {end_time}\n{text}\n\n")
                else:
                    # Regular segment-level timestamps
                    start_time = self.format_timestamp(seg['start']).replace(',', '.')
                    end_time = self.format_timestamp(seg['end']).replace(',', '.')
                    text = seg['text'].strip()
                    if text:
                        f.write(f"{start_time} --> {end_time}\n{text}\n\n")

    def count_words(self, result, format='txt'):
        """Count words in the transcription result"""
        try:
            if format == 'txt':
                return len(result['text'].split())
            elif format in ['srt', 'vtt']:
                word_count = 0
                for segment in result['segments']:
                    word_count += len(segment['text'].split())
                return word_count
            elif format == 'json':
                return len(result['text'].split())
        except Exception as e:
            print(f"Error counting words: {str(e)}")
            return 0

    def save_transcription(self, result, output_path, format='txt', word_timestamps=False):
        """
        Save transcription in specified format
        Args:
            result: Whisper transcription result
            output_path: Path to save the output
            format: Output format (txt, srt, vtt, json)
            word_timestamps: Whether to include word-level timestamps
        """
        output_path = Path(output_path).with_suffix(f'.{format}')
        
        try:
            if format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result["text"])
            elif format == 'srt':
                if "segments" not in result:
                    print("Warning: No segments found in transcription result")
                    return None
                self.save_as_srt(result["segments"], output_path, word_timestamps)
            elif format == 'vtt':
                self.save_as_vtt(result["segments"], output_path, word_timestamps)
            elif format == 'json':
                import json
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            
            if output_path.stat().st_size == 0:
                print("Warning: Output file is empty!")
            
            # Count words after saving
            word_count = self.count_words(result, format)
            if word_count > 0:
                print(f"Word count: {word_count:,} words")
            
            return str(output_path)
        except Exception as e:
            print(f"Error saving transcription: {str(e)}")
            raise

    def transcribe_file(self, audio_path, output_path=None, language=None, output_format='txt', word_timestamps=False):
        """
        Transcribe an audio file and save the result.
        Args:
            audio_path (str): Path to the audio file
            output_path (str, optional): Path to save the transcription
            language (str, optional): Language code for transcription
            output_format (str): Output format (txt, srt, vtt, json)
            word_timestamps (bool): Whether to include word-level timestamps
        Returns:
            str: Path to the output file
        """
        if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"Unsupported output format: {output_format}. "
                           f"Supported formats: {', '.join(self.SUPPORTED_OUTPUT_FORMATS)}")
        
        global interrupted
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if output_path is None:
            output_path = audio_path.with_suffix(f'.{output_format}')
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Transcribing: {audio_path.name}")
        print("Press Ctrl+C to stop")
        
        start_time = time.time()
        progress_thread = None
        transcription_thread = None
        result = None
        
        try:
            with tqdm(total=0, desc="Progress", bar_format='{desc}: {elapsed}') as pbar:
                transcription_options = {
                    'task': 'transcribe',
                    'verbose': None,
                }
                
                if word_timestamps:
                    transcription_options.update({
                        'word_timestamps': True,
                        'condition_on_previous_text': True,
                        'max_initial_timestamp': None
                    })
                
                if language:
                    transcription_options['language'] = language
                    
                def update_progress():
                    while not interrupted:
                        pbar.update()
                        time.sleep(1)
                
                def perform_transcription():
                    nonlocal result
                    try:
                        result = self.model.transcribe(
                            str(audio_path),
                            **transcription_options
                        )
                    except Exception as e:
                        if not interrupted:
                            print(f"Error during transcription: {str(e)}")
                
                progress_thread = threading.Thread(target=update_progress, daemon=True)
                progress_thread.start()
                
                transcription_thread = threading.Thread(target=perform_transcription, daemon=True)
                transcription_thread.start()
                
                while transcription_thread.is_alive() and not interrupted:
                    transcription_thread.join(timeout=0.1)

                if interrupted:
                    print("Transcription cancelled")
                    return None

                if result is None:
                    print("Transcription failed")
                    return None

            if result:
                try:
                    output_file = self.save_transcription(
                        result, 
                        output_path, 
                        output_format,
                        word_timestamps
                    )
                    duration = time.time() - start_time
                    print(f"✓ Completed in {format_time(duration)}")
                    print(f"✓ Saved to: {output_file}")
                    return output_file
                except Exception as e:
                    print(f"Error saving transcription: {str(e)}")
                    return None

        except KeyboardInterrupt:
            print("Transcription cancelled")
            return None
        finally:
            if progress_thread and progress_thread.is_alive():
                progress_thread.join(timeout=0.5)

    def batch_transcribe(self, input_dir, output_dir=None, language=None, output_format='txt', word_timestamps=False):
        """
        Transcribe all audio files in a directory.
        Args:
            input_dir (str): Directory containing audio files
            output_dir (str, optional): Directory to save transcriptions
            language (str, optional): Language code for transcription
            output_format (str): Output format (txt, srt, vtt, json)
            word_timestamps (bool): Whether to include word-level timestamps
        """
        global interrupted
        input_dir = Path(input_dir)
        if not input_dir.exists():
            raise NotADirectoryError(f"Input directory not found: {input_dir}")

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = [
            f for f in input_dir.iterdir()
            if f.suffix.lower() in self.SUPPORTED_AUDIO_FORMATS
        ]

        if not audio_files:
            print(f"No supported audio files found in: {input_dir}")
            print(f"Supported formats: {', '.join(self.SUPPORTED_AUDIO_FORMATS)}")
            return

        print(f"Found {len(audio_files)} audio files to process")
        print("Press Ctrl+C to stop")
        
        processed_files = 0
        try:
            for i, audio_file in enumerate(audio_files, 1):
                if interrupted:
                    print("Batch processing cancelled")
                    break
                    
                try:
                    print(f"\nFile {i}/{len(audio_files)}: {audio_file.name}")
                    output_path = None
                    if output_dir:
                        output_path = output_dir / audio_file.with_suffix(f'.{output_format}').name
                    
                    interrupted = False
                    
                    result = self.transcribe_file(
                        audio_file,
                        output_path=output_path,
                        language=language,
                        output_format=output_format,
                        word_timestamps=word_timestamps
                    )
                    
                    if interrupted:
                        print("Batch processing cancelled")
                        break
                    
                    if result is not None:
                        processed_files += 1
                    
                except Exception as e:
                    print(f"Error transcribing {audio_file.name}: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            print("Batch processing cancelled")
        finally:
            if processed_files > 0:
                print(f"\nCompleted {processed_files} out of {len(audio_files)} files")
            if processed_files < len(audio_files):
                print(f"Remaining: {len(audio_files) - processed_files}")

def get_default_directories():
    """Get default input and output directories"""
    # Default to the 'output' directory in the parent folder
    default_dir = Path(__file__).parent.parent / 'output'
    return default_dir, default_dir

def main():
    parser = argparse.ArgumentParser(
        description="Audio Transcription Tool - Convert audio files to text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription (default: txt):
  transcribe.py path/to/audio.mp3

  # Generate subtitles with word-level timestamps:
  transcribe.py path/to/audio.mp3 --format srt --word-timestamps
  transcribe.py path/to/audio.mp3 -f vtt -w

  # Get detailed JSON output (always includes word timestamps):
  transcribe.py path/to/audio.mp3 --format json

Supported Audio Formats: .mp3, .wav, .m4a, .ogg, .flac
Supported Output Formats: txt (default), srt, vtt, json
        """
    )
    
    default_input, default_output = get_default_directories()
    
    parser.add_argument(
        "input",
        nargs='?',
        default=default_input,
        help=f"Input audio file or directory (default: {default_input})"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file or directory (default: same as input directory)"
    )
    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help="Whisper model to use (default: base)"
    )
    parser.add_argument(
        "-l", "--language",
        help="Language code (e.g., 'en' for English)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=['txt', 'srt', 'vtt', 'json'],
        default='txt',
        help="Output format (default: txt)"
    )
    parser.add_argument(
        "-w", "--word-timestamps",
        action="store_true",
        help="Include word-level timestamps in supported formats"
    )
    
    args = parser.parse_args()
    
    try:
        transcriber = AudioTranscriber(model_name=args.model)
        
        input_path = Path(args.input)
        
        # If input path doesn't exist and no explicit path was given, create the default directory
        if not input_path.exists() and str(input_path) == str(default_input):
            print(f"Creating default directory: {default_input}")
            input_path.mkdir(parents=True, exist_ok=True)
        
        # Determine output format from output file extension or format argument
        output_format = args.format
        if args.output:
            output_suffix = Path(args.output).suffix
            if output_suffix and output_suffix[1:] in transcriber.SUPPORTED_OUTPUT_FORMATS:
                output_format = output_suffix[1:]
        
        if input_path.is_file():
            if input_path.suffix.lower() not in transcriber.SUPPORTED_AUDIO_FORMATS:
                print(f"\nError: Unsupported file format: {input_path.suffix}")
                print(f"Supported formats: {', '.join(transcriber.SUPPORTED_AUDIO_FORMATS)}")
                sys.exit(1)
                
            transcriber.transcribe_file(
                args.input,
                output_path=args.output,
                language=args.language,
                output_format=output_format,
                word_timestamps=args.word_timestamps
            )
        elif input_path.is_dir():
            transcriber.batch_transcribe(
                args.input,
                output_dir=args.output,
                language=args.language,
                output_format=output_format,
                word_timestamps=args.word_timestamps
            )
        else:
            raise FileNotFoundError(f"Input path not found: {args.input}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        sys.exit(0) 