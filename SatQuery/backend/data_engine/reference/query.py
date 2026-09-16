"""Observation-AOI based reference feature querying."""

from __future__ import annotations

from typing import Any, Iterable

from data_engine.geospatial.bounding_box import validate_bounding_box
from data_engine.reference.geojson_source import WGS84, query_geojson_layer
from data_engine.reference.registry import ReferenceLayer, ReferenceLayerRegistry


def _extract_aoi(observation: dict[str, Any]) -> dict[str, float]:
    """Extract the observation WGS84 AOI from the Data Engine result."""

    spatial = observation.get("spatial", {})
    bounds = spatial.get("wgs84_bounds") or spatial.get("bounds")

    if bounds is None:
        geographic = observation.get("geographic", {})
        bounds = geographic.get("wgs84_bounds")

    result = validate_bounding_box(bounds)
    if not result["valid"]:
        raise ValueError(
            f"Observation does not contain a valid WGS84 AOI: {result['reason']}"
        )

    return result["bounds"]


def _aoi_geojson(bounds: dict[str, float]) -> dict[str, Any]:
    west, south, east, north = (
        bounds["west"],
        bounds["south"],
        bounds["east"],
        bounds["north"],
    )
    return {
        "type": "Polygon",
        "coordinates": [[
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
        ]],
    }


def query_reference_features(
    observation: dict[str, Any],
    layers: ReferenceLayerRegistry | Iterable[ReferenceLayer],
) -> dict[str, Any]:
    """Query registered reference layers for features intersecting an observation AOI.

    The observation supplies only its WGS84 geographic extent. Reference data
    remains in separate source layers and is returned as WGS84 GeoJSON.
    """

    if observation.get("valid") is False:
        raise ValueError("Reference features cannot be queried for an invalid observation.")

    aoi = _extract_aoi(observation)
    registry = layers if isinstance(layers, ReferenceLayerRegistry) else ReferenceLayerRegistry(layers)

    layer_results: list[dict[str, Any]] = []
    for layer in registry:
        try:
            collection = query_geojson_layer(layer, aoi)
            layer_results.append({
                **layer.as_metadata(),
                "status": "available",
                "feature_count": len(collection["features"]),
                "geojson": collection,
                "error": None,
            })
        except (FileNotFoundError, OSError, ValueError) as exc:
            layer_results.append({
                **layer.as_metadata(),
                "status": "unavailable",
                "feature_count": 0,
                "geojson": {"type": "FeatureCollection", "features": []},
                "error": str(exc),
            })

    return {
        "schema_version": "1.0",
        "observation_id": observation.get("observation_id"),
        "aoi": {
            "crs": WGS84,
            "bounds": aoi,
            "geometry": _aoi_geojson(aoi),
        },
        "output_crs": WGS84,
        "format": "GeoJSON",
        "layers": layer_results,
    }

