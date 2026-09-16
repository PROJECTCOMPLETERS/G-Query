from __future__ import annotations

from typing import Any

import mapbox_vector_tile

from data_engine.reference.tile.source import (
    get_features_for_tile,
    tile_bounds,
)


def generate_tile(
    source_path: str,
    layer_name: str,
    z: int,
    x: int,
    y: int,
) -> bytes:
    """
    Generate a Mapbox Vector Tile (.pbf)
    for a reference layer.
    """

    features = get_features_for_tile(
        path=source_path,
        z=z,
        x=x,
        y=y,
    )

    if not features:
        return b""

    tile_features: list[dict[str, Any]] = []

    for feature in features:
        geometry = feature.get("geometry")

        if not geometry:
            continue

        tile_feature: dict[str, Any] = {
            "geometry": geometry,
            "properties": feature.get(
                "properties",
                {},
            ),
        }

        # Preserve feature ID if available.
        if feature.get("id") is not None:
            tile_feature["id"] = feature["id"]

        tile_features.append(tile_feature)

    if not tile_features:
        return b""

    west, south, east, north = tile_bounds(
        z,
        x,
        y,
    )

    tile = mapbox_vector_tile.encode(
        {
            "name": layer_name,
            "features": tile_features,
        },
        quantize_bounds=(
            west,
            south,
            east,
            north,
        ),
    )

    return tile