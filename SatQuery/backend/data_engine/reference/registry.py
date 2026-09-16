"""Registry for external reference geospatial layers.

Reference layers are deliberately kept separate from satellite observations.
The registry stores only source definitions; feature geometries are queried
against an observation AOI at request time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReferenceLayer:
    """Definition of a reference geospatial layer source."""

    layer_id: str
    name: str
    source_path: str | Path
    source_crs: str = "EPSG:4326"
    category: str | None = None

    def as_metadata(self) -> dict[str, str | None]:
        """Return frontend/backend-safe layer metadata without feature data."""

        return {
            "layer_id": self.layer_id,
            "name": self.name,
            "category": self.category,
            "source_crs": self.source_crs,
            "output_crs": "EPSG:4326",
        }


class ReferenceLayerRegistry:
    """In-memory registry of separate reference data sources."""

    def __init__(self, layers: Iterable[ReferenceLayer] | None = None) -> None:
        self._layers: dict[str, ReferenceLayer] = {}
        if layers:
            for layer in layers:
                self.register(layer)

    def register(self, layer: ReferenceLayer) -> None:
        """Register or replace a reference layer by stable layer ID."""

        if not layer.layer_id.strip():
            raise ValueError("Reference layer_id cannot be empty.")
        if not layer.name.strip():
            raise ValueError("Reference layer name cannot be empty.")
        self._layers[layer.layer_id] = layer

    def get(self, layer_id: str) -> ReferenceLayer:
        """Return a registered layer or raise KeyError."""

        return self._layers[layer_id]

    def list_layers(self) -> list[dict[str, str | None]]:
        """Return available layer definitions without embedding features."""

        return [
            self._layers[layer_id].as_metadata()
            for layer_id in sorted(self._layers)
        ]

    def __iter__(self):
        return iter(self._layers.values())
