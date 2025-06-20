"""Manifest generator for output videos."""
import json
from datetime import datetime
from typing import List, Dict

def generate_manifest(
    entries: List[Dict],
    output_file: str
) -> None:
    """
    Write manifest entries to output_file as JSON.
    Each entry is a dict with keys: camera, file, start_time, end_time.
    """
    def convert(entry: Dict) -> Dict:
        d = dict(entry)
        if isinstance(d.get("start_time"), datetime):
            d["start_time"] = d["start_time"].isoformat()
        if isinstance(d.get("end_time"), datetime):
            d["end_time"] = d["end_time"].isoformat()
        return d
    with open(output_file, "w") as f:
        json.dump([convert(e) for e in entries], f, indent=2)