"""Tests for executable generic spatial preparation operations."""

import numpy as np
import rasterio
from rasterio.transform import from_origin

from data_engine.geospatial.reprojection import reproject_raster
from data_engine.preprocessing.normalization import normalize_raster
from data_engine.preprocessing.pipeline import prepare_raster
from data_engine.preprocessing.registration import align_raster_to_reference


def _create_raster(path, *, width=10, height=8, resolution=10, crs="EPSG:32644", count=1):
    transform = from_origin(200000, 1500000, resolution, resolution)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=count,
        dtype="uint16",
        crs=crs,
        transform=transform,
    ) as dst:
        for index in range(1, count + 1):
            data = np.arange(width * height, dtype=np.uint16).reshape(height, width)
            dst.write(data, index)


def test_reproject_raster_changes_crs(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "reprojected.tif"
    _create_raster(source)

    result = reproject_raster(source, output, target_crs="EPSG:4326")

    assert result["crs"] == "EPSG:4326"
    with rasterio.open(output) as raster:
        assert raster.crs.to_string() == "EPSG:4326"
        assert raster.count == 1


def test_align_raster_to_reference_matches_reference_grid(tmp_path):
    source = tmp_path / "source.tif"
    reference = tmp_path / "reference.tif"
    output = tmp_path / "aligned.tif"
    _create_raster(source, width=10, height=8, resolution=20, count=2)
    _create_raster(reference, width=12, height=11, resolution=10, count=1)

    result = align_raster_to_reference(source, reference, output)

    with rasterio.open(reference) as ref, rasterio.open(output) as aligned:
        assert aligned.width == ref.width
        assert aligned.height == ref.height
        assert aligned.crs == ref.crs
        assert aligned.transform == ref.transform
        assert aligned.count == 2
    assert result["width"] == 12
    assert result["height"] == 11


def test_normalize_raster_writes_float_values_in_unit_range(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "normalized.tif"
    _create_raster(source, width=5, height=5)

    result = normalize_raster(source, output, lower_percentile=0, upper_percentile=100)

    with rasterio.open(output) as raster:
        data = raster.read(1)
        assert raster.dtypes[0] == "float32"
        assert np.nanmin(data) == 0.0
        assert np.nanmax(data) == 1.0
    assert result["range"] == [0.0, 1.0]


def test_prepare_raster_executes_requested_operations(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "prepared.tif"
    _create_raster(source, width=10, height=10, resolution=20)

    result = prepare_raster(
        source,
        output,
        operations=["resampling", "normalization"],
        target_resolution=(10, 10),
    )

    assert output.exists()
    assert result["operations"] == ["resampling", "normalization"]
    assert len(result["steps"]) == 2
    with rasterio.open(output) as raster:
        assert raster.dtypes[0] == "float32"
        assert raster.width == 20
        assert raster.height == 20
