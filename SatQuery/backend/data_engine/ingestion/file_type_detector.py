"""Detect supported input types from file extension."""
from enum import Enum
from pathlib import Path
from data_engine.exceptions import UnsupportedFileTypeError

class InputKind(str, Enum):
    GEOTIFF = "geotiff"
    JPEG = "jpeg"
    PNG = "png"


def detect_file_type(path: str | Path) -> InputKind:
    suffix = Path(path).suffix.lower()
    if suffix in {".tif", ".tiff"}:
        return InputKind.GEOTIFF
    if suffix in {".jpg", ".jpeg"}:
        return InputKind.JPEG
    if suffix == ".png":
        return InputKind.PNG
    raise UnsupportedFileTypeError(f"Unsupported satellite image format: {suffix or '<none>'}")
