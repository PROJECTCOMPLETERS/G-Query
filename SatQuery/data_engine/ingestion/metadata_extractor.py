"""Extract a stable, JSON-serializable metadata representation from imagery."""
from pathlib import Path
from typing import Any
import mimetypes
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from PIL import Image
from data_engine.ingestion.file_type_detector import InputKind, detect_file_type


def _transform_dict(transform) -> dict[str, float]:
    return {k: float(v) for k, v in {
        "a": transform.a, "b": transform.b, "c": transform.c,
        "d": transform.d, "e": transform.e, "f": transform.f,
    }.items()}


def _bounds_dict(bounds) -> dict[str, float]:
    return {"west": float(bounds.left), "south": float(bounds.bottom),
            "east": float(bounds.right), "north": float(bounds.top)}


def _wgs84_bounds(src_crs, bounds) -> dict[str, float] | None:
    if src_crs is None:
        return None
    try:
        west, south, east, north = transform_bounds(src_crs, "EPSG:4326", bounds.left, bounds.bottom, bounds.right, bounds.top)
        return {"west": float(west), "south": float(south), "east": float(east), "north": float(north)}
    except Exception:
        return None


def _geo_info(crs, bounds) -> dict[str, Any]:
    native = _bounds_dict(bounds)
    if crs is None:
        return {
            "crs_status": "missing", "source_crs": None,
            "native_bounds": native, "wgs84_bounds": None,
            "footprint_geojson": None, "centroid_wgs84": None,
            "map_ready": False, "map_unavailable_reason": "CRS is missing",
        }
    try:
        wgs = _wgs84_bounds(crs, bounds)
        if wgs is None:
            raise ValueError("Unable to transform bounds to WGS84")
        centroid = [(wgs["west"] + wgs["east"]) / 2.0, (wgs["south"] + wgs["north"]) / 2.0]
        return {
            "crs_status": "valid", "source_crs": crs.to_string(),
            "native_bounds": native, "wgs84_bounds": wgs,
            "footprint_geojson": None, "centroid_wgs84": centroid,
            "map_ready": True, "map_unavailable_reason": None,
        }
    except Exception as exc:
        return {
            "crs_status": "invalid", "source_crs": str(crs),
            "native_bounds": native, "wgs84_bounds": None,
            "footprint_geojson": None, "centroid_wgs84": None,
            "map_ready": False, "map_unavailable_reason": str(exc),
        }


def _source(path: Path, kind: InputKind) -> dict[str, Any]:
    return {"kind": "local_file", "locator": str(path.resolve()), "display_name": path.name,
            "media_type": mimetypes.guess_type(path.name)[0]}


def extract_metadata(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser()
    kind = detect_file_type(p)
    if kind == InputKind.GEOTIFF:
        with rasterio.open(p) as src:
            descriptions = list(src.descriptions)
            names = [d if d else f"band_{i}" for i, d in enumerate(descriptions, 1)]
            nodata = None if src.nodata is None else float(src.nodata)
            tags = {str(k): str(v) for k, v in src.tags().items()}
            return {
                "source": _source(p, kind), "input_kind": kind.value,
                "driver": src.driver, "width": src.width, "height": src.height,
                "band_count": src.count, "dtypes": [str(x) for x in src.dtypes],
                "band_names": names, "nodata": nodata,
                "transform": _transform_dict(src.transform),
                "resolution": [float(src.res[0]), float(src.res[1])],
                "geographic": _geo_info(src.crs, src.bounds), "tags": tags,
            }
    with Image.open(p) as image:
        bands = len(image.getbands())
        dtype = str(np.asarray(image).dtype)
        names = [f"band_{i}" for i in range(1, bands + 1)]
        return {
            "source": _source(p, kind), "input_kind": kind.value,
            "driver": None, "width": image.width, "height": image.height,
            "band_count": bands, "dtypes": [dtype] * bands, "band_names": names,
            "nodata": None, "transform": None, "resolution": None,
            "geographic": {
                "crs_status": "missing", "source_crs": None, "native_bounds": None,
                "wgs84_bounds": None, "footprint_geojson": None,
                "centroid_wgs84": None, "map_ready": False,
                "map_unavailable_reason": "JPG/PNG has no geospatial CRS/transform metadata",
            },
            "tags": {str(k): str(v) for k, v in image.info.items()},
        }
