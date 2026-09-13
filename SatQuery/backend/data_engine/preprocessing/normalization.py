"""Generic numeric raster normalization utilities."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio


def normalize_raster(
    input_path: str | Path,
    output_path: str | Path,
    *,
    lower_percentile: float = 2.0,
    upper_percentile: float = 98.0,
) -> dict[str, Any]:
    """Normalize each raster band independently to the [0, 1] range.

    Percentile clipping is used to reduce the effect of extreme outliers.
    Nodata values remain nodata. The result is written as float32.

    This is a generic numeric normalization primitive. Model-specific
    statistics (for example CROMA/Sentinel-2 channel statistics) remain the
    responsibility of the model/execution layer.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not 0 <= lower_percentile < upper_percentile <= 100:
        raise ValueError(
            "Percentiles must satisfy 0 <= lower < upper <= 100."
        )

    with rasterio.open(input_path) as source:
        profile = source.profile.copy()
        profile.update(dtype="float32", count=source.count, tiled=False)
        profile.pop("blockxsize", None)
        profile.pop("blockysize", None)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(output_path, "w", **profile) as destination:
            for band_index in range(1, source.count + 1):
                array = source.read(band_index).astype(np.float32)
                nodata = source.nodata

                if nodata is None:
                    valid_mask = np.isfinite(array)
                else:
                    valid_mask = np.isfinite(array) & (array != nodata)

                normalized = np.zeros_like(array, dtype=np.float32)

                if np.any(valid_mask):
                    values = array[valid_mask]
                    low, high = np.percentile(
                        values,
                        [lower_percentile, upper_percentile],
                    )

                    if np.isclose(low, high):
                        normalized[valid_mask] = 0.0
                    else:
                        normalized[valid_mask] = np.clip(
                            (values - low) / (high - low),
                            0.0,
                            1.0,
                        )

                if nodata is not None:
                    normalized[~valid_mask] = np.nan

                destination.write(normalized, band_index)

        return {
            "path": str(output_path),
            "width": source.width,
            "height": source.height,
            "bands": source.count,
            "crs": source.crs.to_string() if source.crs else None,
            "dtype": "float32",
            "range": [0.0, 1.0],
            "normalization": {
                "method": "percentile_minmax",
                "lower_percentile": lower_percentile,
                "upper_percentile": upper_percentile,
            },
        }
