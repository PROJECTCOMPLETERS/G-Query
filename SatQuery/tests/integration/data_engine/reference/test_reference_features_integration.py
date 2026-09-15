"""Integration test: processed raster AOI -> separate reference layers."""

import json
from pathlib import Path

import rasterio
from rasterio.transform import from_origin

from data_engine import process_file, query_reference_features
from data_engine.reference import ReferenceLayer, ReferenceLayerRegistry


def _write_synthetic_raster(path: Path) -> None:
    # UTM 44N bounds chosen to cover approximately 80E / 13N.
    transform = from_origin(407820, 1453880, 10, 10)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=20,
        height=20,
        count=4,
        dtype="uint16",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        for index in range(1, 5):
            dst.write((index * 10) * __import__("numpy").ones((20, 20), dtype="uint16"), index)
        for index, name in enumerate(("B02", "B03", "B04", "B08"), start=1):
            dst.update_tags(index, NAME=name)


def _write_geojson(path: Path, feature):
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": [feature]}),
        encoding="utf-8",
    )


def test_realistic_observation_aoi_queries_separate_reference_layer(tmp_path):
    raster_path = tmp_path / "observation.tif"
    reference_path = tmp_path / "roads.geojson"
    _write_synthetic_raster(raster_path)

    observation = process_file(raster_path)
    assert observation["valid"] is True
    assert observation["spatial"]["wgs84_bounds"] is not None

    bounds = observation["spatial"]["wgs84_bounds"]
    mid_lon = (bounds["west"] + bounds["east"]) / 2
    mid_lat = (bounds["south"] + bounds["north"]) / 2

    feature = {
        "type": "Feature",
        "id": "road-1",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [bounds["west"], mid_lat],
                [bounds["east"], mid_lat],
            ],
        },
        "properties": {"name": "AOI Road"},
    }
    _write_geojson(reference_path, feature)

    result = query_reference_features(
        observation,
        ReferenceLayerRegistry([
            ReferenceLayer("roads", "Roads", reference_path, category="transportation")
        ]),
    )

    assert result["aoi"]["bounds"] == bounds
    assert result["layers"][0]["feature_count"] == 1
    assert result["layers"][0]["geojson"]["features"][0]["id"] == "road-1"
