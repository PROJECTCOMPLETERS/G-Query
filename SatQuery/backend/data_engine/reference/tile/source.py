from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from shapely.geometry import box, shape
from shapely.strtree import STRtree


# Process-local cache.
# Each FastAPI worker keeps its own spatial index.
_LAYER_CACHE: dict[str, dict[str, Any]] = {}


def load_geojson(path: str | Path) -> dict[str, Any]:
    """
    Load a GeoJSON file from disk.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"GeoJSON file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def tile_bounds(
    z: int,
    x: int,
    y: int,
) -> tuple[float, float, float, float]:
    """
    Return XYZ Web Mercator tile bounds in WGS84.

    Returns:
        (west, south, east, north)
    """

    if z < 0:
        raise ValueError("Zoom level cannot be negative.")

    n = 2**z

    if x < 0 or x >= n:
        raise ValueError(
            f"Invalid tile x={x} for zoom={z}"
        )

    if y < 0 or y >= n:
        raise ValueError(
            f"Invalid tile y={y} for zoom={z}"
        )

    west = x / n * 360.0 - 180.0
    east = (x + 1) / n * 360.0 - 180.0

    north = math.degrees(
        math.atan(
            math.sinh(
                math.pi * (1 - 2 * y / n)
            )
        )
    )

    south = math.degrees(
        math.atan(
            math.sinh(
                math.pi * (
                    1 - 2 * (y + 1) / n
                )
            )
        )
    )

    return west, south, east, north


def build_spatial_index(
    path: str | Path,
) -> dict[str, Any]:
    """
    Load a GeoJSON layer and build an STRtree spatial index.

    The index is cached per process.
    """

    path = Path(path).resolve()
    cache_key = str(path)

    if cache_key in _LAYER_CACHE:
        return _LAYER_CACHE[cache_key]

    print(
        f"Building spatial index for {path.name}..."
    )

    document = load_geojson(path)

    geometries = []
    features = []

    for feature in document.get("features", []):
        geometry_data = feature.get("geometry")

        if not geometry_data:
            continue

        try:
            geometry = shape(geometry_data)
        except Exception:
            continue

        if geometry.is_empty:
            continue

        geometries.append(geometry)
        features.append(feature)

    spatial_index = STRtree(geometries)

    result = {
        "geometries": geometries,
        "features": features,
        "spatial_index": spatial_index,
    }

    _LAYER_CACHE[cache_key] = result

    print(
        f"Indexed {len(features):,} features."
    )

    return result


def get_features_for_tile(
    path: str | Path,
    z: int,
    x: int,
    y: int,
) -> list[dict[str, Any]]:
    """
    Return features intersecting a specific XYZ tile.
    """

    layer = build_spatial_index(path)

    west, south, east, north = tile_bounds(
        z,
        x,
        y,
    )

    tile_bbox = box(
        west,
        south,
        east,
        north,
    )

    spatial_index = layer["spatial_index"]
    geometries = layer["geometries"]
    features = layer["features"]

    candidate_indexes = spatial_index.query(
        tile_bbox
    )

    result = []

    for index in candidate_indexes:
        geometry = geometries[index]

        if not geometry.intersects(tile_bbox):
            continue

        result.append(features[index])

    return result