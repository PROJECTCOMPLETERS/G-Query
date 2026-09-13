"""Compatibility utilities for the SatQuery Data Engine."""

from data_engine.compatibility.spatial import (
    check_spatial_compatibility,
)
from data_engine.compatibility.temporal import (
    check_temporal_compatibility,
)

__all__ = [
    "check_spatial_compatibility",
    "check_temporal_compatibility",
]
