"""Tests for generic raster resampling."""

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from data_engine.preprocessing.resampling import resample_raster


def _create_test_raster(path: Path) -> None:
    transform = from_origin(
        500000,
        2000000,
        10,
        10,
    )

    data = np.arange(
        100 * 100,
        dtype=np.float32,
    ).reshape(100, 100)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=1,
        dtype="float32",
        crs="EPSG:32644",
        transform=transform,
    ) as dataset:
        dataset.write(data, 1)


def test_resample_raster_changes_resolution_and_dimensions(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "resampled.tif"

    _create_test_raster(source)

    result = resample_raster(
        source,
        output,
        target_resolution=(20.0, 20.0),
    )

    assert output.exists()
    assert result["width"] == 50
    assert result["height"] == 50
    assert result["bands"] == 1
    assert result["crs"] == "EPSG:32644"

    assert result["resolution"] == [20.0, 20.0]


def test_resample_raster_preserves_bounds(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "resampled.tif"

    _create_test_raster(source)

    with rasterio.open(source) as dataset:
        original_bounds = dataset.bounds

    resample_raster(
        source,
        output,
        target_resolution=(20.0, 20.0),
    )

    with rasterio.open(output) as dataset:
        assert dataset.bounds == original_bounds


def test_resample_raster_preserves_band_count_and_dtype(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "resampled.tif"

    _create_test_raster(source)

    resample_raster(
        source,
        output,
        target_resolution=(20.0, 20.0),
    )

    with rasterio.open(output) as dataset:
        assert dataset.count == 1
        assert dataset.dtypes == ("float32",)


def test_resample_raster_rejects_invalid_resolution(tmp_path):
    source = tmp_path / "source.tif"
    output = tmp_path / "resampled.tif"

    _create_test_raster(source)

    try:
        resample_raster(
            source,
            output,
            target_resolution=(0.0, 20.0),
        )
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid resolution.")