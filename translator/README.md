# Translation Module

A powerful translation module that leverages Meta's NLLB-200 model to provide high-quality translations while preserving formatting and structure across multiple file formats.

## Features

🌍 **Translation Capabilities**
- Support for 200+ language pairs using NLLB-200 model
- Two model options:
  - Standard (1.3B parameters) - Balanced quality and performance
  - Large (3.3B parameters) - Highest quality translation
- Real-time progress tracking with detailed status updates
- Automatic GPU detection and optimization
- Memory-efficient processing for large files

📄 **Supported File Formats**
- SRT (SubRip Text) subtitles
- VTT (WebVTT) subtitles
- JSON files (both array and dictionary formats)
- Plain text files

🚀 **Performance Features**
- GPU acceleration (when available)
- Smart text chunking for optimal translation
- Batch processing for efficiency
- Progress bars for all operations
- Memory-efficient processing

## Requirements

### System Requirements
- Python 3.7 or higher
- CUDA-compatible GPU recommended (8GB+ VRAM)
- Minimum 8GB RAM (16GB recommended for large model)

### Python Dependencies
```bash
# Core dependencies
torch>=2.0.0
transformers>=4.30.0
sentencepiece>=0.1.99
tqdm>=4.65.0
pysrt>=1.1.2
webvtt-py>=0.4.6
```

## Installation

1. Install Python dependencies:
```bash
cd translator
pip install -r requirements.txt
```

2. For GPU support (recommended):
```bash
# For CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Basic Usage

```bash
# Translate all supported files to French
python translate.py --lang fr

# Use large model for highest quality
python translate.py --lang es --model large

# Translate specific file
python translate.py --lang de path/to/file.srt

# Memory-efficient processing
python translate.py --lang fr --memory-efficient
```

### Command Line Arguments

- `--lang`: Target language code (e.g., 'fr' for French)
- `--model`: Model size ('standard' or 'large', default: standard)
- `--memory-efficient`: Enable memory-efficient processing
- `input_file`: Optional path to specific file (processes all supported files in output directory if not specified)

## Output Format

Translated files follow this naming convention:
```
{original_name}_{language_code}.{extension}
```

Example:
```
output/
├── video1.srt           # Original file
├── video1_fr.srt       # French translation
└── video1_es.srt       # Spanish translation
```

## File Format Support

### SRT Files
- Preserves all timing information
- Maintains subtitle numbering
- Keeps original formatting

### VTT Files
- Preserves WebVTT header
- Maintains cue settings and formatting
- Supports styling information

### JSON Files
- Array format: Translates text fields while preserving structure
- Dictionary format: Recursively processes all text fields
- Maintains original JSON structure and formatting

### Text Files
- Preserves line breaks and spacing
- Maintains document structure
- Supports Unicode characters

## Performance Optimization

### GPU Acceleration
The translator automatically detects and uses available NVIDIA GPUs:
- Displays GPU model and available memory
- Shows CUDA version information
- Automatically optimizes batch size based on available memory

### Memory Management
- Smart text chunking for large files
- Batch processing for optimal GPU utilization
- Memory-efficient mode for large files

## Progress Tracking

Real-time progress information includes:
- File detection and counting
- Model loading status
- Translation progress with ETA
- Memory usage statistics

## Error Handling

- Validates input file formats
- Checks for valid language codes
- Preserves original files
- Provides detailed error messages
- Handles GPU memory limitations gracefully

## Language Support

Supports 200+ languages through NLLB-200. Common language codes:
- English: eng_Latn
- French: fra_Latn
- Spanish: spa_Latn
- German: deu_Latn
- Chinese: zho_Hans
- Japanese: jpn_Jpan
- Korean: kor_Hang

For a complete list of supported languages:
```bash
python translate.py --list-languages
```

## Integration

This module can be used:
1. Standalone for translation tasks
2. As part of the video-edit toolkit pipeline
3. In combination with the audio preservation system

## Contributing

Contributions are welcome! Areas of interest:
- Additional file format support
- Performance optimizations
- Language-specific improvements
- Documentation enhancements

# Video Translation Module

This module handles the translation of video subtitles and transcripts using neural machine translation models.

## Features

- Supports multiple file formats (SRT, VTT, JSON, TXT)
- Multiple translation models (MarianMT, M2M100)
- GPU acceleration support
- Batch processing for efficient translation
- Progress tracking and error handling

## Installation

1. Install the basic requirements:
```bash
pip install -r requirements.txt
```

2. For GPU acceleration (recommended for faster translation):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Note: The CUDA version (cu121) might need to be adjusted based on your NVIDIA drivers. Common versions are:
- cu121 (CUDA 12.1)
- cu118 (CUDA 11.8)
- cu117 (CUDA 11.7)

## GPU Support

The translator will automatically use your GPU if:
1. You have an NVIDIA GPU
2. You have NVIDIA drivers installed
3. PyTorch is installed with CUDA support

To verify GPU support, run any translation command and check the output:
- `🚀 Using GPU for translation` indicates GPU is being used
- `💻 Using CPU for translation` indicates CPU-only mode

## Usage

Basic translation command:
```bash
python translate.py --target_lang fr
```

This will translate all supported files in the output directory to French.

For a specific file:
```bash
python translate.py path/to/file.srt --target_lang fr
```

List supported languages:
```bash
python translate.py --list-languages
```

## Performance

- GPU acceleration can provide 5-10x faster translation compared to CPU
- Batch processing is automatically enabled when using GPU
- Memory usage is optimized for long texts through chunking 