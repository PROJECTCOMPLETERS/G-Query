"""Integration tests for Data Engine processing and readiness evaluation."""
import numpy as np
import rasterio
from rasterio.transform import from_origin

from data_engine.controller import process_file
from data_engine.readiness.evaluator import evaluate_data_readiness


def _create_test_raster(
    path,
    *,
    band_names,
    acquisition_datetime="2026-01-14T10:30:00",
):
    """Create a small valid GeoTIFF for integration testing."""

    width = 100
    height = 100

    # Valid UTM coordinates for EPSG:32644.
    transform = from_origin(
        200000,
        1500000,
        10,
        10,
    )

    data = np.ones(
        (height, width),
        dtype=np.uint16,
    )

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=len(band_names),
        dtype="uint16",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        for index, band_name in enumerate(band_names, start=1):
            dst.write(data, index)
            dst.set_band_description(index, band_name)

        if acquisition_datetime is not None:
            dst.update_tags(
                ACQUISITION_DATETIME=acquisition_datetime,
            )


def _requirements(
    *,
    task="object_counting",
    min_observations=1,
    modality_required=False,
    allowed_modalities=None,
    temporal_required=False,
    spatial_required=False,
):
    """Build a canonical Data Requirements payload."""

    return {
        "schema_version": "1.0",
        "request_id": "integration-test",
        "task": task,
        "inputs": {
            "min_observations": min_observations,
            "type": "image",
        },
        "modality": {
            "required": modality_required,
            "allowed": allowed_modalities or [],
        },
        "temporal": {
            "required": temporal_required,
        },
        "spatial": {
            "required": spatial_required,
        },
        "quality": {
            "valid_data": True,
            "sufficient_resolution": False,
        },
        "task_specific": {},
    }

def test_valid_optical_raster_is_processed_and_ready(tmp_path):
    """A valid optical GeoTIFF should process successfully and be ready."""

    raster_path = tmp_path / "optical.tif"

    _create_test_raster(
        raster_path,
        band_names=["B02", "B03", "B04"],
    )

    observation = process_file(raster_path)

    result = evaluate_data_readiness(
        request_id="integration-001",
        task="object_counting",
        data_requirements=_requirements(),
        observations={"observation_1": observation},
    )

    assert observation["valid"] is True
    assert observation["raster"]["modality"] == "optical"
    assert observation["raster"]["bands"] == 3
    assert observation["acquisition"]["datetime"] is not None
    assert observation["spatial"]["bounds"] is not None
    assert observation["spatial"]["map_ready"] is True

    assert result["ready"] is True
    assert result["available_observations"] == ["observation_1"]
    assert result["missing_information"] == []
    assert result["reason"] is None


def test_single_observation_is_not_ready_for_change_analysis(tmp_path):
    """Change analysis should require the configured two observations."""

    raster_path = tmp_path / "optical_single.tif"

    _create_test_raster(
        raster_path,
        band_names=["B02", "B03", "B04"],
    )

    observation = process_file(raster_path)

    result = evaluate_data_readiness(
        request_id="integration-002",
        task="change_analysis",
        data_requirements=_requirements(
    task="change_analysis",
    min_observations=2,
    temporal_required=True,
    spatial_required=True,
),
        observations={"observation_1": observation},
    )

    assert observation["valid"] is True
    assert result["ready"] is False
    assert "second_observation" in result["missing_information"]


def test_wrong_modality_is_not_ready(tmp_path):
    """A SAR observation should not satisfy an optical requirement."""

    raster_path = tmp_path / "sar.tif"

    _create_test_raster(
        raster_path,
        band_names=["VV", "VH"],
    )

    observation = process_file(raster_path)

    result = evaluate_data_readiness(
        request_id="integration-003",
        task="object_counting",
        data_requirements=_requirements(
    modality_required=True,
    allowed_modalities=["optical"],
),
        observations={"observation_1": observation},
    )

    assert observation["valid"] is True
    assert observation["raster"]["modality"] == "sar"

    assert result["ready"] is False
    assert result["missing_information"] == ["compatible_modality"]


def test_two_valid_optical_observations_are_ready(tmp_path):
    """Two valid optical observations should satisfy a two-image requirement."""

    before_path = tmp_path / "before.tif"
    after_path = tmp_path / "after.tif"

    _create_test_raster(
        before_path,
        band_names=["B02", "B03", "B04"],
        acquisition_datetime="2026-01-04T10:30:00",
    )

    _create_test_raster(
        after_path,
        band_names=["B02", "B03", "B04"],
        acquisition_datetime="2026-01-14T10:30:00",
    )

    before = process_file(before_path)
    after = process_file(after_path)

    result = evaluate_data_readiness(
        request_id="integration-004",
        task="change_analysis",
        data_requirements=_requirements(
            task="change_analysis",
            min_observations=2,
        ),
        observations={
            "before": before,
            "after": after,
        },
    )

    assert before["valid"] is True
    assert after["valid"] is True

    assert before["raster"]["modality"] == "optical"
    assert after["raster"]["modality"] == "optical"

    assert before["acquisition"]["datetime"] is not None
    assert after["acquisition"]["datetime"] is not None

    assert before["spatial"]["bounds"] is not None
    assert after["spatial"]["bounds"] is not None

    assert result["ready"] is True
    assert result["available_observations"] == ["before", "after"]
    assert result["missing_information"] == []
    assert result["reason"] is None