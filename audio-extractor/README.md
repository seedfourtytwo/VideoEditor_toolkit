# Audio Extractor

A powerful Python tool for extracting audio from video files, with support for batch processing and special character handling.

## Features

- Extract audio from multiple video formats:
  - MP4 (.mp4)
  - Matroska (.mkv)
  - AVI (.avi)
  - QuickTime (.mov)
  - Flash Video (.flv)
  - Windows Media (.wmv)

- Support for multiple audio formats:
  - WAV (default, high quality uncompressed)
  - MP3 (compressed, good for music)
  - AAC (compressed, good for speech)

- Advanced features:
  - Batch processing of multiple files
  - Recursive directory processing
  - Time segment extraction
  - Custom audio bitrate
  - Progress bar and detailed status updates
  - Automatic handling of special characters in filenames

## Requirements

- Python 3.7 or higher
- FFmpeg installed and accessible in system PATH
- Python packages (installed via requirements.txt):
  - moviepy>=2.1.2
  - decorator>=4.0.2
  - imageio>=2.5
  - imageio-ffmpeg>=0.2.0
  - numpy>=1.25.0
  - proglog<=1.0.0
  - pillow>=9.2.0
  - tqdm>=4.65.0
  - ffmpeg-python>=0.2.0

## Installation

1. Ensure FFmpeg is installed:
   ```bash
   # Check FFmpeg installation
   ffmpeg -version
   ```
   If not installed:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

1. Extract audio from a single video:
   ```bash
   python extract_audio.py video.mp4
   ```

2. Extract audio from multiple videos:
   ```bash
   python extract_audio.py video1.mp4 video2.mkv video3.avi
   ```

3. Process all videos in a directory:
   ```bash
   python extract_audio.py /path/to/videos/
   ```

4. Process all videos in the default output directory:
   ```bash
   python extract_audio.py
   ```

### Advanced Options

1. Specify output format and bitrate:
   ```bash
   python extract_audio.py video.mp4 --format mp3 --bitrate 320k
   ```

2. Extract a specific time segment:
   ```bash
   python extract_audio.py video.mp4 --start 10.5 --end 20.5
   ```

3. Process directories recursively:
   ```bash
   python extract_audio.py /path/to/videos/ --recursive
   ```

4. Specify custom output directory:
   ```bash
   python extract_audio.py video.mp4 --output /path/to/output/
   ```

### Command Line Arguments

- `input`: Input video file(s) or directory. If not specified, processes all videos in the output directory.
- `--output`, `-o`: Output directory (default: central output directory)
- `--format`, `-f`: Output audio format: 'wav', 'mp3', or 'aac' (default: wav)
- `--bitrate`, `-b`: Output audio bitrate (default: 192k)
- `--start`, `-s`: Start time in seconds for extraction
- `--end`, `-e`: End time in seconds for extraction
- `--recursive`, `-r`: Process subdirectories when input is a directory

## Special Character Handling

The tool automatically handles special characters in filenames:
- Replaces full-width characters with their regular equivalents
- Sanitizes problematic characters for compatibility
- Provides clear warnings when filenames are modified
- Suggests manual filename changes when automatic renaming fails

## Error Handling

The tool includes robust error handling:
- Validates FFmpeg installation
- Checks input file existence
- Verifies output directory permissions
- Handles special characters in filenames
- Provides clear error messages and suggestions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgments

- [MoviePy](https://zulko.github.io/moviepy/) for video processing
- [FFmpeg](https://ffmpeg.org/) for media handling 