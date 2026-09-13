"""Generic raster reprojection utilities for the SatQuery Data Engine."""

from pathlib import Path
from typing import Any

import rasterio
from rasterio.warp import calculate_default_transform, reproject


def reproject_raster(
    input_path: str | Path,
    output_path: str | Path,
    *,
    target_crs: str,
    target_resolution: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Reproject a raster to a target CRS.

    This is a generic spatial operation. It does not perform model-specific
    normalization, tiling, band selection, or inference.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not str(target_crs).strip():
        raise ValueError("Target CRS must be provided.")

    if target_resolution is not None:
        x_resolution, y_resolution = target_resolution
        if x_resolution <= 0 or y_resolution <= 0:
            raise ValueError("Target resolution values must be positive.")
        resolution = (float(x_resolution), float(y_resolution))
    else:
        resolution = None

    with rasterio.open(input_path) as source:
        transform, width, height = calculate_default_transform(
            source.crs,
            target_crs,
            source.width,
            source.height,
            *source.bounds,
            resolution=resolution,
        )

        profile = source.profile.copy()
        profile.update(
            {
                "crs": target_crs,
                "transform": transform,
                "width": width,
                "height": height,
                "tiled": False,
            }
        )
        profile.pop("blockxsize", None)
        profile.pop("blockysize", None)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(output_path, "w", **profile) as destination:
            for band_index in range(1, source.count + 1):
                reproject(
                    source=rasterio.band(source, band_index),
                    destination=rasterio.band(destination, band_index),
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    src_nodata=source.nodata,
                    dst_nodata=source.nodata,
                    resampling=rasterio.enums.Resampling.bilinear,
                )

        return {
            "path": str(output_path),
            "width": width,
            "height": height,
            "bands": source.count,
            "crs": str(target_crs),
            "resolution": [abs(transform.a), abs(transform.e)],
        }
