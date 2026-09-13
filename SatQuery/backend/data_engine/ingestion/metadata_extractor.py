"""Extract a stable, JSON-serializable metadata representation from imagery."""

from datetime import datetime
from pathlib import Path
from typing import Any
import mimetypes

import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from PIL import Image

from data_engine.ingestion.file_type_detector import (
    InputKind,
    detect_file_type,
)


def _transform_dict(transform) -> dict[str, float]:
    return {
        k: float(v)
        for k, v in {
            "a": transform.a,
            "b": transform.b,
            "c": transform.c,
            "d": transform.d,
            "e": transform.e,
            "f": transform.f,
        }.items()
    }


def _bounds_dict(bounds) -> dict[str, float]:
    return {
        "west": float(bounds.left),
        "south": float(bounds.bottom),
        "east": float(bounds.right),
        "north": float(bounds.top),
    }


def _wgs84_bounds(src_crs, bounds) -> dict[str, float] | None:
    if src_crs is None:
        return None

    try:
        west, south, east, north = transform_bounds(
            src_crs,
            "EPSG:4326",
            bounds.left,
            bounds.bottom,
            bounds.right,
            bounds.top,
        )

        return {
            "west": float(west),
            "south": float(south),
            "east": float(east),
            "north": float(north),
        }

    except Exception:
        return None


def _geo_info(crs, bounds) -> dict[str, Any]:
    native = _bounds_dict(bounds)

    if crs is None:
        return {
            "crs_status": "missing",
            "source_crs": None,
            "native_bounds": native,
            "wgs84_bounds": None,
            "footprint_geojson": None,
            "centroid_wgs84": None,
            "map_ready": False,
            "map_unavailable_reason": "CRS is missing",
        }

    try:
        wgs = _wgs84_bounds(crs, bounds)

        if wgs is None:
            raise ValueError("Unable to transform bounds to WGS84")

        centroid = [
            (wgs["west"] + wgs["east"]) / 2.0,
            (wgs["south"] + wgs["north"]) / 2.0,
        ]

        return {
            "crs_status": "valid",
            "source_crs": crs.to_string(),
            "native_bounds": native,
            "wgs84_bounds": wgs,
            "footprint_geojson": None,
            "centroid_wgs84": centroid,
            "map_ready": True,
            "map_unavailable_reason": None,
        }

    except Exception as exc:
        return {
            "crs_status": "invalid",
            "source_crs": str(crs),
            "native_bounds": native,
            "wgs84_bounds": None,
            "footprint_geojson": None,
            "centroid_wgs84": None,
            "map_ready": False,
            "map_unavailable_reason": str(exc),
        }


def _source(path: Path, kind: InputKind) -> dict[str, Any]:
    return {
        "kind": "local_file",
        "locator": str(path.resolve()),
        "display_name": path.name,
        "media_type": mimetypes.guess_type(path.name)[0],
    }


def _extract_bands(src) -> list[dict[str, Any]]:
    """
    Extract metadata for every raster band.

    This describes the bands as stored in the raster. It does not
    infer sensor-specific meaning unless that information is present
    in the raster metadata.
    """

    bands = []

    for index in range(1, src.count + 1):
        description = src.descriptions[index - 1]

        nodata = src.nodatavals[index - 1]

        bands.append(
            {
                "index": index,
                "name": description if description else f"band_{index}",
                "dtype": str(src.dtypes[index - 1]),
                "width": src.width,
                "height": src.height,
                "nodata": (
                    None if nodata is None else float(nodata)
                ),
            }
        )

    return bands


def _parse_datetime(value: Any) -> str | None:
    """
    Parse a metadata value into an ISO-8601 datetime string.

    Returns None when the value cannot be interpreted safely.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Handle common ISO-8601 UTC notation.
    normalized = text.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.isoformat()
    except ValueError:
        pass

    # Handle common date-only metadata.
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
        return parsed.date().isoformat()
    except ValueError:
        return None


def _extract_acquisition_datetime(tags: dict[str, Any]) -> str | None:
    """
    Extract acquisition datetime from explicit raster metadata.

    Only metadata fields containing an explicit acquisition/date/time
    value are considered. The function never infers a date from the
    filename or filesystem information.
    """

    if not tags:
        return None

    candidate_keys = (
        "ACQUISITION_DATETIME",
        "ACQUISITION_DATE_TIME",
        "ACQUISITION_DATE",
    )

    normalized_tags = {
        str(key).strip().upper(): value
        for key, value in tags.items()
    }

    for key in candidate_keys:
        if key in normalized_tags:
            parsed = _parse_datetime(normalized_tags[key])

            if parsed is not None:
                return parsed

    return None


def extract_metadata(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser()
    kind = detect_file_type(p)

    if kind == InputKind.GEOTIFF:

        with rasterio.open(p) as src:

            bands = _extract_bands(src)

            names = [
                band["name"]
                for band in bands
            ]

            nodata = (
                None
                if src.nodata is None
                else float(src.nodata)
            )

            tags = {
                str(k): str(v)
                for k, v in src.tags().items()
            }

            acquisition_datetime = _extract_acquisition_datetime(tags)

            return {
                "source": _source(p, kind),
                "input_kind": kind.value,
                "driver": src.driver,

                "width": src.width,
                "height": src.height,

                "band_count": src.count,

                # New: detailed information for every band
                "bands": bands,

                "dtypes": [
                    str(x)
                    for x in src.dtypes
                ],

                "band_names": names,

                "nodata": nodata,

                "transform": _transform_dict(
                    src.transform
                ),

                "resolution": [
                    float(src.res[0]),
                    float(src.res[1]),
                ],

                "geographic": _geo_info(
                    src.crs,
                    src.bounds,
                ),

                "acquisition": {
                    "datetime": acquisition_datetime,
                },

                "tags": tags,
            }

    # JPEG / PNG
    with Image.open(p) as image:

        band_count = len(image.getbands())
        dtype = str(np.asarray(image).dtype)

        bands = []

        for index in range(1, band_count + 1):
            bands.append(
                {
                    "index": index,
                    "name": f"band_{index}",
                    "dtype": dtype,
                    "width": image.width,
                    "height": image.height,
                    "nodata": None,
                }
            )

        names = [
            band["name"]
            for band in bands
        ]

        return {
            "source": _source(p, kind),
            "input_kind": kind.value,
            "driver": None,

            "width": image.width,
            "height": image.height,

            "band_count": band_count,

            # New: detailed information for every band
            "bands": bands,

            "dtypes": [dtype] * band_count,
            "band_names": names,

            "nodata": None,
            "transform": None,
            "resolution": None,

            "geographic": {
                "crs_status": "missing",
                "source_crs": None,
                "native_bounds": None,
                "wgs84_bounds": None,
                "footprint_geojson": None,
                "centroid_wgs84": None,
                "map_ready": False,
                "map_unavailable_reason": (
                    "JPG/PNG has no geospatial "
                    "CRS/transform metadata"
                ),
            },

            "acquisition": {
                "datetime": None,
            },

            "tags": {
                str(k): str(v)
                for k, v in image.info.items()
            },
        }