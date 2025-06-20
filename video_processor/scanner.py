"""Scanner module for finding camera MP4 files."""
import logging
import re
from pathlib import Path
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import List, Tuple

IST = ZoneInfo("Asia/Kolkata")

def scan_folder(folder: str, camera: str, date: date) -> List[Tuple[str, datetime]]:
    """
    Scan input folder for MP4 files for given camera and date.
    Returns list of (filepath, timestamp) where timestamp is timezone-aware IST datetime.
    """
    folder_path = Path(folder)
    pattern = re.compile(rf"^{re.escape(camera)}_(\d{{14}})\.mp4$")
    results: List[Tuple[str, datetime]] = []
    for file in folder_path.iterdir():
        if not file.is_file():
            continue
        m = pattern.match(file.name)
        if m:
            ts_str = m.group(1)
            try:
                ts = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
                ts = ts.replace(tzinfo=IST)
                if ts.date() == date:
                    results.append((str(file), ts))
            except ValueError:
                logging.warning(f"Skipping file with invalid timestamp: {file.name}")
    results.sort(key=lambda x: x[1])
    return results