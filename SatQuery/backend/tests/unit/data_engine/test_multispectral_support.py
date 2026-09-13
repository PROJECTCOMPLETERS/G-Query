"""Tests for explicit optical, SAR, and multispectral modality handling."""

import numpy as np
import rasterio
from rasterio.transform import from_origin

from data_engine.compatibility.modality import check_modality_compatibility
from data_engine.controller import process_file


def _create_raster(path, band_names):
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=20,
        height=20,
        count=len(band_names),
        dtype="uint16",
        crs="EPSG:32644",
        transform=from_origin(200000, 1500000, 10, 10),
    ) as dst:
        data = np.ones((20, 20), dtype=np.uint16)
        for index, name in enumerate(band_names, start=1):
            dst.write(data, index)
            dst.set_band_description(index, name)


def test_sentinel_style_multiband_optical_is_multispectral(tmp_path):
    path = tmp_path / "sentinel2.tif"
    _create_raster(path, ["B02", "B03", "B04", "B08", "B11", "B12"])

    observation = process_file(path)

    assert observation["valid"] is True
    assert observation["raster"]["modality"] == "multispectral"


def test_three_band_optical_remains_optical(tmp_path):
    path = tmp_path / "rgb.tif"
    _create_raster(path, ["B02", "B03", "B04"])

    observation = process_file(path)

    assert observation["raster"]["modality"] == "optical"


def test_multispectral_requirement_is_supported():
    observation = {
        "raster": {
            "modality": "multispectral",
            "width": 20,
            "height": 20,
            "bands": 6,
            "band_details": [{"dtype": "uint16"}] * 6,
        }
    }

    result = check_modality_compatibility(
        observation,
        required="multispectral",
    )

    assert result["compatible"] is True
    assert result["modalities"] == ["multispectral"]
