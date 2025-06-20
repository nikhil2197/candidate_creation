"""Extractor module for cutting and concatenating video segments."""
import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple

def get_duration(file_path: str) -> float:
    """
    Return duration of media file in seconds using ffprobe.
    """
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logging.error(f"ffprobe error for {file_path}: {result.stderr}")
        raise RuntimeError(f"ffprobe error for {file_path}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        logging.error(f"Could not parse duration for {file_path}: {result.stdout}")
        raise

def extract_time_segment(
    input_files: List[Tuple[str, datetime]],
    start: datetime,
    end: datetime,
    output_file: str,
    reencode: bool = False
) -> str:
    """
    Extract and concatenate segments between start and end from input files.
    Returns path to the combined output file.
    """
    pieces = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for file_path, file_start in input_files:
            duration = get_duration(file_path)
            file_end = file_start + timedelta(seconds=duration)
            if file_end <= start or file_start >= end:
                continue
            segment_start = max(start, file_start)
            offset = (segment_start - file_start).total_seconds()
            segment_end = min(end, file_end)
            seg_duration = (segment_end - segment_start).total_seconds()
            if seg_duration <= 0:
                continue
            piece_path = Path(tmpdir) / f"{file_start.strftime('%Y%m%d%H%M%S')}_{int(offset)}_{int(seg_duration)}.mp4"
            cmd = ["ffmpeg", "-y", "-ss", str(offset), "-i", file_path, "-t", str(seg_duration)]
            if not reencode:
                cmd += ["-c", "copy"]
            cmd += [str(piece_path)]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logging.error(f"Error extracting segment from {file_path}: {result.stderr}")
                continue
            pieces.append(piece_path)
        if not pieces:
            logging.error("No overlapping segments found for given time range.")
            raise RuntimeError("No overlapping segments found.")
        concat_file = Path(tmpdir) / "concat_list.txt"
        with open(concat_file, "w") as cf:
            for p in pieces:
                cf.write(f"file '{p}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file)]
        if not reencode:
            cmd += ["-c", "copy"]
        cmd += [output_file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logging.error(f"Error concatenating segments: {result.stderr}")
            raise RuntimeError("Concatenation failed.")
    return output_file