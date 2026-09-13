"""Generic raster grid-alignment utilities."""

from pathlib import Path
from typing import Any

import rasterio
from rasterio.warp import reproject


def align_raster_to_reference(
    input_path: str | Path,
    reference_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Align a raster to the exact CRS/grid of a reference raster.

    The reference determines CRS, transform, width and height. Rasterio's
    reprojection/resampling machinery is used when the source does not
    already share that grid. This is grid alignment, not feature-based image
    registration.
    """
    input_path = Path(input_path)
    reference_path = Path(reference_path)
    output_path = Path(output_path)

    with rasterio.open(reference_path) as reference:
        with rasterio.open(input_path) as source:
            profile = source.profile.copy()
            profile.update(
                {
                    "crs": reference.crs,
                    "transform": reference.transform,
                    "width": reference.width,
                    "height": reference.height,
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
                        dst_transform=reference.transform,
                        dst_crs=reference.crs,
                        src_nodata=source.nodata,
                        dst_nodata=source.nodata,
                        resampling=rasterio.enums.Resampling.bilinear,
                    )

            return {
                "path": str(output_path),
                "width": reference.width,
                "height": reference.height,
                "bands": source.count,
                "crs": reference.crs.to_string() if reference.crs else None,
                "resolution": [abs(reference.transform.a), abs(reference.transform.e)],
                "reference_path": str(reference_path),
            }
