"""Print SatQuery Data Engine metadata for a local image."""
import argparse, json
from pathlib import Path
from data_engine.ingestion import extract_metadata, validate_file

def main():
    parser = argparse.ArgumentParser(description="Inspect a local satellite image with the SatQuery Data Engine.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    validate_file(args.path)
    print("SATQUERY IMAGE INSPECTION")
    print(json.dumps(extract_metadata(args.path), indent=2))

if __name__ == "__main__":
    main()
