"""Public interface for the SatQuery Data Engine."""

from data_engine.controller import process_file
from data_engine.ingestion import (
    detect_file_type,
    extract_metadata,
    validate_file,
)

__all__ = [
    "process_file",
    "detect_file_type",
    "extract_metadata",
    "validate_file",
]