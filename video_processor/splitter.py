"""Splitter module to divide video into chunks."""
import logging
import subprocess
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from .extractor import get_duration

def split_into_chunks(
    video_file: str,
    chunk_duration: int,
    start_time: datetime,
    camera: str,
    output_folder: str,
    reencode: bool = False
) -> List[str]:
    """
    Split video into chunks of chunk_duration (seconds).
    Returns list of chunk file paths.
    """
    total_duration = get_duration(video_file)
    num_chunks = math.ceil(total_duration / chunk_duration)
    output_paths: List[str] = []
    for i in range(num_chunks):
        offset = i * chunk_duration
        remaining = total_duration - offset
        this_duration = chunk_duration if remaining >= chunk_duration else remaining
        if this_duration <= 0:
            break
        chunk_start_dt = start_time + timedelta(seconds=offset)
        chunk_end_dt = chunk_start_dt + timedelta(seconds=this_duration)
        chunk_start_str = chunk_start_dt.strftime("%H%M%S")
        chunk_end_str = chunk_end_dt.strftime("%H%M%S")
        chunk_name = f"{camera}_{chunk_start_str}_{chunk_end_str}.mp4"
        chunk_path = Path(output_folder) / chunk_name
        cmd = ["ffmpeg", "-y", "-ss", str(offset), "-i", str(video_file), "-t", str(this_duration)]
        if not reencode:
            # copy video stream, re-encode audio to AAC for MP4 compatibility
            cmd += ["-c:v", "copy", "-c:a", "aac"]
        cmd += [str(chunk_path)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logging.error(f"Error creating chunk {chunk_name}: {result.stderr}")
            continue
        output_paths.append(str(chunk_path))
    return output_paths