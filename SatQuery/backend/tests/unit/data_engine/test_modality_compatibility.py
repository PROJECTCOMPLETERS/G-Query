"""Tests for modality and raster compatibility."""

from data_engine.compatibility.modality import (
    check_modality_compatibility,
)


def _observation(
    modality="optical",
    width=100,
    height=100,
    bands=3,
):
    """Build a minimal valid observation."""

    return {
        "raster": {
            "modality": modality,
            "width": width,
            "height": height,
            "bands": bands,
            "band_details": [
                {"dtype": "uint16"}
                for _ in range(bands)
            ],
        }
    }


def test_same_optical_modality_is_compatible():
    """Two optical observations should satisfy compatible modality."""

    first = _observation("optical")
    second = _observation("optical")

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is True
    assert result["checks"]["modality"] is True
    assert result["checks"]["raster_structure"] is True
    assert result["modalities"] == ["optical", "optical"]


def test_same_sar_modality_is_compatible():
    """Two SAR observations should satisfy compatible modality."""

    first = _observation("sar", bands=2)
    second = _observation("sar", bands=2)

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is True
    assert result["modalities"] == ["sar", "sar"]


def test_mixed_modalities_are_not_compatible_by_default():
    """Optical and SAR should not satisfy a generic compatible requirement."""

    first = _observation("optical")
    second = _observation("sar", bands=2)

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is False
    assert result["checks"]["modality"] is False


def test_optical_sar_requirement_accepts_mixed_pair():
    """An explicit optical+SAR requirement should accept the mixed pair."""

    first = _observation("optical")
    second = _observation("sar", bands=2)

    result = check_modality_compatibility(
        first,
        second,
        required=["optical", "sar"],
    )

    assert result["compatible"] is True
    assert result["checks"]["modality"] is True


def test_optical_requirement_rejects_sar():
    """An optical-only requirement should reject SAR."""

    first = _observation("optical")
    second = _observation("sar", bands=2)

    result = check_modality_compatibility(
        first,
        second,
        required="optical",
    )

    assert result["compatible"] is False


def test_missing_modality_is_not_confirmed():
    """Missing modality metadata should prevent compatibility confirmation."""

    first = _observation(None)
    second = _observation("optical")

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is False
    assert "modality" in result["missing_information"]


def test_invalid_raster_dimensions_are_rejected():
    """Invalid raster dimensions should make the observation unusable."""

    first = _observation("optical", width=0)
    second = _observation("optical")

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is False
    assert result["checks"]["raster_structure"] is False


def test_missing_band_metadata_is_rejected():
    """Incomplete band metadata should be reported."""

    first = _observation("optical")
    first["raster"]["band_details"] = []

    second = _observation("optical")

    result = check_modality_compatibility(
        first,
        second,
        required="compatible",
    )

    assert result["compatible"] is False
    assert result["checks"]["raster_structure"] is False