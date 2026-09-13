"""GeoTIFF loader backed by Rasterio."""
from pathlib import Path
from typing import Any
import numpy as np
import rasterio
from data_engine.exceptions import RasterReadError

class GeoTiffLoader:
    """Open and read GeoTIFF rasters without hiding Rasterio errors."""
    def open(self, path: str | Path):
        try:
            return rasterio.open(path)
        except Exception as exc:
            raise RasterReadError(f"Unable to open GeoTIFF '{path}': {exc}") from exc

    def read(self, path: str | Path, indexes=None) -> np.ndarray:
        with self.open(path) as dataset:
            try:
                return dataset.read(indexes=indexes)
            except Exception as exc:
                raise RasterReadError(f"Unable to read GeoTIFF '{path}': {exc}") from exc

    def inspect(self, path: str | Path) -> dict[str, Any]:
        from data_engine.ingestion.metadata_extractor import extract_metadata
        return extract_metadata(path)
