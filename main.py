"""Main CLI entrypoint for video processing."""
import argparse
import sys
import logging
import yaml
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo
from video_processor.scanner import scan_folder
from video_processor.extractor import extract_time_segment
from video_processor.splitter import split_into_chunks
from video_processor.manifest import generate_manifest

def parse_args():
    parser = argparse.ArgumentParser(description="Process camera footage.")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config file")
    return parser.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    try:
        with open(args.config) as cf:
            cfg = yaml.safe_load(cf)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        sys.exit(1)

    camera = cfg.get("camera")
    if not camera:
        logging.error("camera not specified in config")
        sys.exit(1)
    date_str = cfg.get("date")
    if not date_str:
        logging.error("date not specified in config")
        sys.exit(1)
    try:
        dt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Invalid date format, expected YYYY-MM-DD")
        sys.exit(1)

    tz = ZoneInfo("Asia/Kolkata")
    try:
        start_t = datetime.strptime(cfg.get("start_time", "09:00"), "%H:%M").time()
        end_t = datetime.strptime(cfg.get("end_time", "12:00"), "%H:%M").time()
    except ValueError:
        logging.error("Invalid time format, expected HH:MM")
        sys.exit(1)
    start_dt = datetime.combine(dt_date, start_t, tzinfo=tz)
    end_dt = datetime.combine(dt_date, end_t, tzinfo=tz)
    if end_dt <= start_dt:
        logging.error("end_time must be after start_time")
        sys.exit(1)

    chunk_length = cfg.get("chunk_length", 300)
    try:
        chunk_length = int(chunk_length)
    except ValueError:
        logging.error("chunk_length must be integer (seconds)")
        sys.exit(1)
    reencode = bool(cfg.get("reencode", False))

    input_folder = cfg.get("input_folder", ".")
    output_folder = cfg.get("output_folder", "./output")
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    files = scan_folder(input_folder, camera, dt_date)
    if not files:
        logging.error("No input files found")
        sys.exit(1)

    date_compact = dt_date.strftime("%Y%m%d")
    start_compact = start_dt.strftime("%H%M%S")
    end_compact = end_dt.strftime("%H%M%S")
    combined_name = f"{camera}_{date_compact}_{start_compact}_{end_compact}.mp4"
    combined_path = str(Path(output_folder) / combined_name)
    try:
        extract_time_segment(files, start_dt, end_dt, combined_path, reencode=reencode)
    except Exception as e:
        logging.error(f"Failed to extract time segment: {e}")
        sys.exit(1)

    entries = [{
        "camera": camera,
        "file": combined_name,
        "start_time": start_dt,
        "end_time": end_dt
    }]

    chunk_files = split_into_chunks(combined_path, chunk_length, start_dt, camera, output_folder, reencode=reencode)
    for cf in chunk_files:
        fname = Path(cf).name
        parts = fname.split("_")
        if len(parts) >= 3:
            cs_str = parts[1]
            ce_str = parts[2].split(".")[0]
            cs_time = datetime.combine(dt_date, datetime.strptime(cs_str, "%H%M%S").time(), tz)
            ce_time = datetime.combine(dt_date, datetime.strptime(ce_str, "%H%M%S").time(), tz)
        else:
            cs_time = None
            ce_time = None
        entries.append({
            "camera": camera,
            "file": fname,
            "start_time": cs_time,
            "end_time": ce_time
        })

    manifest_path = str(Path(output_folder) / "manifest.json")
    generate_manifest(entries, manifest_path)
    logging.info(f"Processing complete. Manifest saved to {manifest_path}")

if __name__ == "__main__":
    main()