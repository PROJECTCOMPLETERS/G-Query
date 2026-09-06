"""Exceptions raised by the SatQuery Data Engine."""

class DataEngineError(Exception):
    """Base exception for data-engine failures."""

class UnsupportedFileTypeError(DataEngineError):
    """Raised when an input format is not supported by the data engine."""

class RasterReadError(DataEngineError):
    """Raised when a raster cannot be opened or read."""
