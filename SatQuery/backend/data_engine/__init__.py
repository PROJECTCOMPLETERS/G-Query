"""Public interface for the SatQuery Data Engine."""

from data_engine.controller import process_file
from data_engine.ingestion import (
    detect_file_type,
    extract_metadata,
    validate_file,
)
from data_engine.model_input import build_model_input
from data_engine.reference import (
    ReferenceLayer,
    ReferenceLayerRegistry,
    query_reference_features,
)

__all__ = [
    "process_file",
    "detect_file_type",
    "extract_metadata",
    "validate_file",
    "build_model_input",
    "ReferenceLayer",
    "ReferenceLayerRegistry",
    "query_reference_features",
]
