"""GeoJSON reference-layer reader and spatial filter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pyproj import CRS, Transformer
from shapely.geometry import box, mapping, shape
from shapely.ops import transform as shapely_transform

from data_engine.reference.registry import ReferenceLayer


WGS84 = "EPSG:4326"


def _load_geojson(
    path: str | Path,
) -> dict[str, Any]:

    source_path = Path(path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Reference layer source not found: {source_path}"
        )

    with source_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        document = json.load(handle)

    if document.get("type") == "FeatureCollection":
        return document

    if document.get("type") == "Feature":
        return {
            "type": "FeatureCollection",
            "features": [document],
        }

    raise ValueError(
        "Reference source must be a GeoJSON "
        "FeatureCollection or Feature."
    )


def _transformer(
    source_crs: str,
    target_crs: str = WGS84,
) -> Transformer | None:

    source = CRS.from_user_input(source_crs)
    target = CRS.from_user_input(target_crs)

    if source == target:
        return None

    return Transformer.from_crs(
        source,
        target,
        always_xy=True,
    )


def query_geojson_layer(
    layer: ReferenceLayer,
    aoi_bounds: dict[str, float],
) -> dict[str, Any]:

    document = _load_geojson(
        layer.source_path
    )

    aoi = box(
        float(aoi_bounds["west"]),
        float(aoi_bounds["south"]),
        float(aoi_bounds["east"]),
        float(aoi_bounds["north"]),
    )

    transformer = _transformer(
        layer.source_crs
    )

    features = []

    for index, feature in enumerate(
        document.get("features", [])
    ):

        if (
            not isinstance(feature, dict)
            or feature.get("type") != "Feature"
        ):
            continue

        geometry_data = feature.get("geometry")

        if not geometry_data:
            continue

        try:
            geometry = shape(geometry_data)
        except Exception:
            continue

        if geometry.is_empty:
            continue

        if transformer is not None:
            geometry_wgs84 = shapely_transform(
                transformer.transform,
                geometry,
            )
        else:
            geometry_wgs84 = geometry

        if geometry_wgs84.is_empty:
            continue

        if not geometry_wgs84.intersects(aoi):
            continue

        properties = feature.get("properties")

        if not isinstance(properties, dict):
            properties = {}

        feature_id = feature.get(
            "id",
            index,
        )

        features.append(
            {
                "type": "Feature",
                "id": feature_id,
                "geometry": mapping(
                    geometry_wgs84
                ),
                "properties": properties,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }