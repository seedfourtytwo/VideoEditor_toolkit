# Audio Transcription Module

This module provides functionality to transcribe audio files to text using OpenAI's Whisper model. It supports various output formats and timestamp granularities.

## Features

- Supports multiple audio formats: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`
- Multiple output formats: `.txt`, `.srt`, `.vtt`, `.json`
- Word-level or sentence-level timestamps
- Batch processing of multiple files
- Progress tracking with estimated time remaining
- Word count statistics
- Interrupt handling (Ctrl+C)

## Usage

### Basic Usage

```bash
# Basic transcription (outputs txt file)
python transcribe.py path/to/audio.mp3

# Specify output format
python transcribe.py path/to/audio.mp3 -f txt|srt|vtt|json

# Process all audio files in a directory
python transcribe.py path/to/audio/directory/
```

### Timestamp Options

1. **Sentence-level timestamps** (default):
```bash
# JSON format with sentence-level segments
python transcribe.py path/to/audio.mp3 -f json

# SRT format with sentence-level segments
python transcribe.py path/to/audio.mp3 -f srt

# VTT format with sentence-level segments
python transcribe.py path/to/audio.mp3 -f vtt
```

2. **Word-level timestamps**:
```bash
# Add -w or --word-timestamps flag
python transcribe.py path/to/audio.mp3 -f json -w
```

### Output Format Details

#### JSON Format
```json
{
  "text": "Complete transcribed text",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 4.94,
      "text": "Segment text",
      "words": [          // Only present with -w flag
        {
          "word": "Example",
          "start": 0.0,
          "end": 0.38,
          "probability": 0.85
        }
      ]
    }
  ]
}
```

#### SRT Format
```srt
1
00:00:00,000 --> 00:00:04,940
Segment text

2
00:00:05,340 --> 00:00:08,860
Next segment text
```

#### VTT Format
```vtt
WEBVTT

00:00:00.000 --> 00:00:04.940
Segment text

00:00:05.340 --> 00:00:08.860
Next segment text
```

### Additional Options

```bash
# Specify language (e.g., English)
python transcribe.py path/to/audio.mp3 -l en

# Choose Whisper model size
python transcribe.py path/to/audio.mp3 -m tiny|base|small|medium|large

# Specify output location
python transcribe.py path/to/audio.mp3 -o path/to/output.txt

# Combine options
python transcribe.py path/to/audio.mp3 -f json -w -l en -m base -o output.json
```

## Output Statistics

The transcriber provides:
- Word count for the transcribed text
- Processing time
- File location of the output

Example output:
```
Transcribing: audio.mp3
Progress: 45s elapsed
✓ Completed in 45 seconds
Word count: 1,234 words
✓ Saved to: audio.json
```

## Interrupting Transcription

- Press Ctrl+C once to gracefully stop the current transcription
- Press Ctrl+C twice to force quit immediately

## Supported Models

The script supports all Whisper model sizes:
- `tiny`: Fastest, least accurate
- `base`: Good balance for most uses
- `small`: Better accuracy, slower
- `medium`: High accuracy
- `large`: Best accuracy, slowest

## Error Handling

The script handles common errors:
- Unsupported file formats
- Missing files or directories
- Invalid output formats
- Transcription failures

Error messages are clear and provide guidance on how to resolve issues. 