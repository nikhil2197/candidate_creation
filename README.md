# Video Processing Toolkit

This Python tool scans a folder of camera MP4 recordings, extracts a specified time window, concatenates the segments, splits the result into equal-duration chunks, and generates a JSON manifest of all outputs.

## Features
- Scan input directory for files named `{camera}_{YYYYMMDDHHMMSS}.mp4` (IST timezone).
- Extract and concatenate footage between configurable start/end times (default 09:00–12:00).
- Split the combined video into fixed-length chunks (default 5 minutes).
- Produce a JSON manifest listing each output file with camera ID and ISO-formatted start/end timestamps.

## Prerequisites
- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) (and ffprobe) installed and available on `PATH`
- `pip install -r requirements.txt`

## Installation
```bash
git clone <repo-url>
cd <repo>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration
See `config.yaml` for an example configuration (camera and date are optional; auto-detected from input filenames):
```yaml
camera: "D1"               # Camera identifier (optional; auto-detected if omitted)
date: "2025-06-20"        # Date to process (YYYY-MM-DD) (optional; auto-detected if omitted)
input_folder: "./input"    # Directory of source MP4 files
output_folder: "./output"  # Directory for combined and chunk outputs
start_time: "09:00"        # Extraction window start (HH:MM)
end_time: "12:00"          # Extraction window end (HH:MM)
chunk_length: 300           # Chunk duration in seconds (default 300)
reencode: false             # Re-encode segments (slower) or copy streams
```

## Usage
```bash
python main.py --config config.yaml
```

Outputs in `./output`:
- Combined video: `{camera}_{YYYYMMDD}_{HHMMSS}_{HHMMSS}.mp4`
- Chunk files: `{camera}_{HHMMSS}_{HHMMSS}.mp4`
- Manifest: `manifest.json` (array of entries `{camera, file, start_time, end_time}`)

## Project Structure
```
.
├── config.yaml
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── video_processor/
    ├── __init__.py
    ├── scanner.py      # scan_folder()
    ├── extractor.py    # get_duration(), extract_time_segment()
    ├── splitter.py     # split_into_chunks()
    └── manifest.py     # generate_manifest()
```

## Modules & APIs
- **scanner.scan_folder(folder, camera, date)**: list of `(filepath, datetime)`
- **extractor.extract_time_segment(inputs, start, end, output_file, reencode)**
- **splitter.split_into_chunks(video_file, chunk_duration, start_time, camera, output_folder, reencode)**
- **manifest.generate_manifest(entries, output_file)**

## License & Contributing
Contributions and issues are welcome. This project is provided as-is without warranty.