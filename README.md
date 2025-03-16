# Video Edit Toolkit

A comprehensive toolkit for video processing and manipulation, designed to handle various video-related tasks efficiently.

## TLDR - What Can This Do?

Quick overview of all features:

🎬 **Video Processing**
- Download videos from various platforms
- Extract audio from videos (MP4, MKV, AVI, etc.)
- Support for custom time segments and bitrates

🔊 **Audio Handling**
- Convert videos to multiple audio formats (WAV, MP3, AAC)
- Batch process multiple videos at once
- Custom audio quality settings

📝 **Transcription & Translation**
- Convert audio to text using AI (OpenAI's Whisper)
- Automatic language detection for 98 languages
- Multiple accuracy levels (from fast to high-accuracy)
- Real-time progress tracking
- High-quality translation using NLLB-200 model
- Support for multiple file formats (SRT, VTT, JSON, TXT)
- Real-time translation progress monitoring

**Quick Start:**
```bash
# Extract audio from a video
cd audio-extractor
python extract_audio.py video.mp4

# Transcribe the audio
cd ../transcriber
python transcribe.py audio.mp3

# Translate subtitles or text
cd ../translator
python translate.py --lang fr  # Translates to French
python translate.py --lang es --model large  # Use larger model for Spanish
```

## Modules

### 1. Audio Transcriber
Located in `/transcriber`

A powerful audio transcription tool that converts audio files to text using OpenAI's Whisper model. Features include:
- Multiple audio format support (MP3, WAV, M4A, OGG, FLAC)
- Various output formats (TXT, SRT, VTT, JSON)
- Word-level or sentence-level timestamps
- Batch processing capabilities
- Word count statistics
- See [Transcriber README](transcriber/README.md) for detailed documentation

### 2. Audio Extractor
Located in `/audio-extractor`

A powerful tool for extracting audio from video files, supporting:
- Multiple video formats (MP4, MKV, AVI, MOV, FLV, WMV)
- Multiple audio formats (WAV, MP3, AAC)
- Batch processing
- Special character handling in filenames
- Time segment extraction
- Custom audio bitrate

Example usage:
```bash
# Extract audio from all videos in the output directory
cd audio-extractor
python extract_audio.py

# Extract specific video(s)
python extract_audio.py video1.mp4 video2.mkv

# Extract with custom format and bitrate
python extract_audio.py video.mp4 --format mp3 --bitrate 320k
```

### 3. Video Downloader
Located in `/downloader`

[Description and features of the video downloader component]

### 4. Translation System
Located in `/translator`

A powerful translation system using Meta's NLLB-200 model, supporting:
- Multiple file formats:
  - SRT subtitles
  - WebVTT subtitles
  - JSON files (both array and dictionary formats)
  - Plain text files
- 200+ language pairs
- Two model sizes:
  - Standard (1.3B parameters) - Balanced quality and performance
  - Large (3.3B parameters) - Highest quality translation
- Real-time progress tracking
- Batch processing
- GPU acceleration (when available)

Example usage:
```bash
# Basic translation to French
python translate.py --lang fr

# Use large model for highest quality
python translate.py --lang es --model large

# Translate specific file
python translate.py --lang de path/to/file.srt

# Memory-efficient processing
python translate.py --lang fr --memory-efficient
```

Key features:
- Preserves subtitle timing and formatting
- Maintains JSON structure while translating text fields
- Smart text chunking for optimal translation
- Progress bars for all operations
- Automatic GPU detection and optimization
- Memory-efficient processing for large files

### 5. Audio Preservation in Translation
Located in `/translator`

When translating videos, preserving background music and sound effects while replacing only the speech is crucial for maintaining video quality. Our planned approach includes:

**Audio Track Separation:**
- Use AI-powered audio separation (Demucs/Spleeter) to split audio into:
  - Vocals (speech) track
  - Music track
  - Sound effects/ambient track
- Replace only the vocals with translated speech
- Remix all tracks to preserve original audio elements

**Pipeline for Audio-Preserved Translation:**
```bash
Original Video
    ↓
Extract Audio
    ↓
Audio Track Separation
    ├── Extract Speech Track
    └── Keep Other Tracks (music, effects)
    ↓
Transcribe Speech
    ↓
Translate Text
    ↓
Generate TTS Audio
    ↓
Mix Audio Tracks:
    ├── New TTS Audio (translated speech)
    └── Original Non-Speech Tracks
    ↓
Combine with Video
```

Key considerations:
- Timing synchronization between translated speech and video
- Volume balancing between speech and background
- Quality preservation of music and effects
- Support for multiple audio tracks

## Requirements

### System Requirements
- Python 3.7 or higher
- FFmpeg installed and accessible in system PATH
- Sufficient disk space for video processing
- CUDA-compatible GPU (recommended for translation)
- Minimum 8GB RAM (16GB recommended for large model)

### Python Dependencies
Main dependencies are organized in the root `requirements.txt`, with specific requirements for each component in their respective directories.

**Translation System Dependencies:**
- torch
- transformers
- sentencepiece
- tqdm
- pysrt
- webvtt-py

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd video-edit
```

2. Install FFmpeg:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

3. Install Python dependencies:
```bash
# Install base requirements
pip install -r requirements.txt

# For specific components (optional)
cd translator
pip install -r requirements.txt
```

## Project Structure
```
video-edit/
├── audio-extractor/    # Audio extraction module
├── transcriber/        # Audio transcription module
├── translator/         # Translation module
│   ├── translate.py    # Main translation script
│   ├── models/        # Translation models
│   ├── core/          # Core processing logic
│   └── config/        # Configuration files
├── downloader/         # Video downloading module
├── output/            # Default output directory
└── README.md
```

## Usage

Each component has its own README with detailed usage instructions:
- [Audio Extractor Documentation](./audio-extractor/README.md)
- [Audio Transcriber Documentation](./transcriber/README.md)
- [Video Downloader Documentation](./downloader/README.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgments

- [MoviePy](https://zulko.github.io/moviepy/) for video processing
- [FFmpeg](https://ffmpeg.org/) for media handling
- [OpenAI Whisper](https://github.com/openai/whisper) for audio transcription 