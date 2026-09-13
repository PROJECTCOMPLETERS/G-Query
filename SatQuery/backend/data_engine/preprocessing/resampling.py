"""Generic raster resampling utilities for the SatQuery Data Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


def resample_raster(
    input_path: str | Path,
    output_path: str | Path,
    *,
    target_resolution: tuple[float, float],
    resampling_method: Resampling = Resampling.bilinear,
) -> dict[str, Any]:
    """
    Resample a raster to a requested spatial resolution.

    The operation preserves the input CRS and spatial extent while
    changing the raster dimensions and transform.

    Args:
        input_path:
            Path to the source raster.

        output_path:
            Path where the resampled raster will be written.

        target_resolution:
            Requested pixel size as (x_resolution, y_resolution).

        resampling_method:
            Rasterio resampling method to use.

    Returns:
        Metadata describing the generated raster.

    Raises:
        ValueError:
            If the requested resolution is invalid.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    x_resolution, y_resolution = target_resolution

    if x_resolution <= 0 or y_resolution <= 0:
        raise ValueError("Target resolution values must be positive.")

    with rasterio.open(input_path) as source:
        source_bounds = source.bounds

        output_width = max(
            1,
            round(
                (source_bounds.right - source_bounds.left)
                / x_resolution
            ),
        )

        output_height = max(
            1,
            round(
                (source_bounds.top - source_bounds.bottom)
                / y_resolution
            ),
        )

        output_transform = rasterio.transform.from_bounds(
            source_bounds.left,
            source_bounds.bottom,
            source_bounds.right,
            source_bounds.top,
            output_width,
            output_height,
        )

        profile = source.profile.copy()

        profile.update(
            {
                "width": output_width,
                "height": output_height,
                "transform": output_transform,
                "tiled": False,
            }
        )

        # Block sizes from a tiled source are not valid when the
        # output is explicitly configured as non-tiled.
        profile.pop("blockxsize", None)
        profile.pop("blockysize", None)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(output_path, "w", **profile) as destination:
            for band_index in range(1, source.count + 1):
                source_array = source.read(band_index)

                destination_array = np.empty(
                    (output_height, output_width),
                    dtype=source_array.dtype,
                )

                reproject(
                    source_array,
                    destination_array,
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=output_transform,
                    dst_crs=source.crs,
                    src_nodata=source.nodata,
                    dst_nodata=source.nodata,
                    resampling=resampling_method,
                )

                destination.write(
                    destination_array,
                    band_index,
                )

        actual_resolution = (
            abs(output_transform.a),
            abs(output_transform.e),
        )

        return {
            "path": str(output_path),
            "width": output_width,
            "height": output_height,
            "bands": source.count,
            "crs": source.crs.to_string() if source.crs else None,
            "resolution": list(actual_resolution),
            "transform": {
                "a": output_transform.a,
                "b": output_transform.b,
                "c": output_transform.c,
                "d": output_transform.d,
                "e": output_transform.e,
                "f": output_transform.f,
            },
        }