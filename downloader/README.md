# YouTube Video Downloader

A Python script to download videos from YouTube. It supports downloading either all videos from a channel or a single video by URL. The script uses `yt-dlp` for efficient downloading and supports various options for customization.

## Features

- Download all videos and/or shorts from a YouTube channel
- Download single videos by URL (including regular videos and shorts)
- High-quality MP4 format downloads
- Progress tracking for each video
- Configurable retry mechanism
- Geo-restriction bypass
- Option to limit the number of downloads for testing (channel downloads only)
- Support for FFmpeg post-processing
- Smart duplicate detection when downloading both videos and shorts

## Prerequisites

1. Python 3.6 or higher
2. FFmpeg installed and in system PATH

### Installing FFmpeg

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the archive to a folder (e.g., `C:\ffmpeg`)
3. Add the bin folder (e.g., `C:\ffmpeg\bin`) to your system PATH:
   - Open System Properties > Advanced > Environment Variables
   - Under System Variables, find and select "Path"
   - Click "Edit" and add the path to FFmpeg's bin folder
4. Restart your terminal/command prompt

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/seedfourtytwo/youtubeDownload.git
cd youtubeDownload
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download a single video:
```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```
This will download the video to the central output directory.

To specify a custom output directory:
```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --output /path/to/output/
```

### Channel Downloads

Download all videos from a channel:
```bash
python youtube_downloader.py "https://www.youtube.com/c/CHANNEL_NAME"
```

Download only shorts from a channel:
```bash
python youtube_downloader.py "https://www.youtube.com/c/CHANNEL_NAME" --type shorts
```

Download with a limit:
```bash
python youtube_downloader.py "https://www.youtube.com/c/CHANNEL_NAME" --limit 10
```

### Options

- `url`: YouTube video URL or channel URL (required)
- `--output`, `-o`: Output directory (default: central output directory)
- `--type`, `-t`: Content type to download: 'shorts', 'videos', or 'all' (default: 'all')
- `--retries`, `-r`: Number of retries for failed downloads (default: 3)
- `--no-geo-bypass`: Disable geo-restriction bypassing
- `--limit`, `-l`: Limit the number of videos to download from a channel

### Output Directory Structure

By default, videos are downloaded to the central output directory at the root of the project. Each video is saved with its title as the filename, with special characters removed or replaced to ensure filesystem compatibility.

You can specify a custom output directory using the `--output` option if you need the files saved elsewhere.

## Error Handling

The script includes robust error handling for common issues:
- FFmpeg not installed
- Network connectivity problems
- Geo-restricted content
- Invalid URLs
- Missing videos

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.