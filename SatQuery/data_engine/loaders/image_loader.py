"""JPG/PNG loader backed by Pillow."""
from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError
from data_engine.exceptions import RasterReadError

class ImageLoader:
    def open(self, path: str | Path):
        try:
            return Image.open(path)
        except (UnidentifiedImageError, OSError) as exc:
            raise RasterReadError(f"Unable to open image '{path}': {exc}") from exc

    def read(self, path: str | Path) -> np.ndarray:
        with self.open(path) as image:
            return np.asarray(image).copy()

    def inspect(self, path: str | Path) -> dict:
        from data_engine.ingestion.metadata_extractor import extract_metadata
        return extract_metadata(path)
