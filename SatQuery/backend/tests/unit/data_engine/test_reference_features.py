"""Tests for observation-AOI reference feature querying."""

import json
from pathlib import Path

import pytest

from data_engine.reference import (
    ReferenceLayer,
    ReferenceLayerRegistry,
    query_reference_features,
)


def _write_geojson(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def _feature(feature_id, geometry, properties=None):
    return {
        "type": "Feature",
        "id": feature_id,
        "geometry": geometry,
        "properties": properties or {},
    }


def test_reference_query_uses_observation_wgs84_bounds_and_returns_geojson(tmp_path):
    source = tmp_path / "roads.geojson"
    _write_geojson(
        source,
        [
            _feature(
                "inside",
                {
                    "type": "LineString",
                    "coordinates": [[80.05, 13.05], [80.15, 13.15]],
                },
                {"name": "Inside Road"},
            ),
            _feature(
                "outside",
                {
                    "type": "LineString",
                    "coordinates": [[81.0, 14.0], [81.1, 14.1]],
                },
            ),
        ],
    )

    observation = {
        "observation_id": "obs-001",
        "valid": True,
        "spatial": {
            "wgs84_bounds": {
                "west": 80.0,
                "south": 13.0,
                "east": 80.2,
                "north": 13.2,
            }
        },
    }

    registry = ReferenceLayerRegistry([
        ReferenceLayer("roads", "Roads", source, category="transportation")
    ])

    result = query_reference_features(observation, registry)

    assert result["output_crs"] == "EPSG:4326"
    assert result["format"] == "GeoJSON"
    assert result["aoi"]["crs"] == "EPSG:4326"
    assert result["aoi"]["bounds"]["west"] == 80.0
    assert len(result["layers"]) == 1
    layer = result["layers"][0]
    assert layer["status"] == "available"
    assert layer["feature_count"] == 1
    assert layer["geojson"]["type"] == "FeatureCollection"
    assert layer["geojson"]["features"][0]["id"] == "inside"


def test_reference_query_falls_back_to_process_file_bounds_shape(tmp_path):
    source = tmp_path / "water.geojson"
    _write_geojson(
        source,
        [_feature(
            "water-1",
            {"type": "Polygon", "coordinates": [[
                [80.05, 13.05], [80.15, 13.05], [80.15, 13.15],
                [80.05, 13.15], [80.05, 13.05]
            ]]},
            {"type": "lake"},
        )]
    )

    observation = {
        "observation_id": "obs-002",
        "valid": True,
        "spatial": {
            "bounds": {
                "west": 80.0, "south": 13.0,
                "east": 80.2, "north": 13.2,
            }
        },
    }

    result = query_reference_features(
        observation,
        [ReferenceLayer("water", "Water bodies", source, category="hydrology")],
    )

    assert result["layers"][0]["feature_count"] == 1
    assert result["layers"][0]["geojson"]["features"][0]["properties"]["type"] == "lake"


def test_reference_query_rejects_invalid_observation(tmp_path):
    source = tmp_path / "buildings.geojson"
    _write_geojson(source, [])

    with pytest.raises(ValueError, match="invalid observation"):
        query_reference_features(
            {"observation_id": "bad", "valid": False},
            [ReferenceLayer("buildings", "Buildings", source)],
        )


def test_reference_registry_lists_sources_without_embedding_features(tmp_path):
    roads = tmp_path / "roads.geojson"
    water = tmp_path / "water.geojson"
    _write_geojson(roads, [])
    _write_geojson(water, [])

    registry = ReferenceLayerRegistry([
        ReferenceLayer("roads", "Roads", roads, category="transportation"),
        ReferenceLayer("water", "Water bodies", water, category="hydrology"),
    ])

    layers = registry.list_layers()

    assert [layer["layer_id"] for layer in layers] == ["roads", "water"]
    assert all("features" not in layer for layer in layers)
    assert all(layer["output_crs"] == "EPSG:4326" for layer in layers)


def test_reference_geometry_is_reprojected_to_wgs84(tmp_path):
    from pyproj import Transformer

    source = tmp_path / "buildings_utm.geojson"
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True)
    x1, y1 = transformer.transform(80.05, 13.05)
    x2, y2 = transformer.transform(80.15, 13.15)

    _write_geojson(
        source,
        [_feature(
            "building-1",
            {"type": "Polygon", "coordinates": [[
                [x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]
            ]]},
            {"building": True},
        )]
    )

    observation = {
        "observation_id": "obs-utm",
        "valid": True,
        "spatial": {
            "wgs84_bounds": {
                "west": 80.0, "south": 13.0,
                "east": 80.2, "north": 13.2,
            }
        },
    }

    result = query_reference_features(
        observation,
        [ReferenceLayer("buildings", "Buildings", source, source_crs="EPSG:32644")],
    )

    feature = result["layers"][0]["geojson"]["features"][0]
    coordinates = feature["geometry"]["coordinates"][0]
    assert result["layers"][0]["output_crs"] == "EPSG:4326"
    assert all(-180 <= point[0] <= 180 and -90 <= point[1] <= 90 for point in coordinates)
    assert min(point[0] for point in coordinates) == pytest.approx(80.05, abs=1e-3)
    assert max(point[0] for point in coordinates) == pytest.approx(80.15, abs=1e-3)


def test_missing_reference_source_is_reported_per_layer(tmp_path):
    missing = tmp_path / "missing.geojson"
    observation = {
        "observation_id": "obs-missing",
        "valid": True,
        "spatial": {
            "wgs84_bounds": {
                "west": 80.0, "south": 13.0,
                "east": 80.2, "north": 13.2,
            }
        },
    }

    result = query_reference_features(
        observation,
        [ReferenceLayer("roads", "Roads", missing)],
    )

    layer = result["layers"][0]
    assert layer["status"] == "unavailable"
    assert layer["feature_count"] == 0
    assert layer["geojson"]["features"] == []
    assert "not found" in layer["error"]
