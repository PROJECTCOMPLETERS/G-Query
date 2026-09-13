"""Tests for the generic Data Engine -> Model Engine handoff contract."""

import pytest

from data_engine.model_input import build_model_input


def _observation():
    return {
        "valid": True,
        "raster": {
            "modality": "multispectral",
            "width": 120,
            "height": 120,
            "bands": 6,
        },
        "spatial": {"bounds": {"west": 80, "south": 13, "east": 80.1, "north": 13.1}},
        "acquisition": {"datetime": "2026-01-14T10:00:00"},
        "band_validation": {"valid": True},
    }


def test_build_model_input_contains_prepared_raster_and_metadata(tmp_path):
    prepared = tmp_path / "prepared.tif"
    prepared.write_bytes(b"placeholder")

    result = build_model_input(
        observation_id="obs_001",
        observation=_observation(),
        prepared_path=prepared,
        preprocessing=["reprojection", "normalization"],
    )

    assert result["schema_version"] == "1.0"
    assert result["observation_id"] == "obs_001"
    assert result["input"]["type"] == "prepared_raster"
    assert result["input"]["path"] == str(prepared)
    assert result["input"]["tensor"] is None
    assert result["metadata"]["raster"]["modality"] == "multispectral"
    assert result["preprocessing"] == ["reprojection", "normalization"]


def test_tensor_can_be_supplied_by_later_model_pipeline():
    tensor = [[1, 2], [3, 4]]
    result = build_model_input(
        observation_id="obs_002",
        observation=_observation(),
        tensor=tensor,
    )

    assert result["input"]["type"] == "tensor"
    assert result["input"]["tensor"] == tensor


def test_invalid_observation_cannot_be_handed_off():
    observation = _observation()
    observation["valid"] = False

    with pytest.raises(ValueError, match="valid Data Engine observations"):
        build_model_input(
            observation_id="obs_003",
            observation=observation,
            tensor=[1],
        )
