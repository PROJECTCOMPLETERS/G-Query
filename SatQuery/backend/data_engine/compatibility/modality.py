"""Modality and raster compatibility checks for satellite observations."""

from __future__ import annotations

from typing import Any


SUPPORTED_MODALITIES = {"optical", "sar", "multispectral"}


def _extract_raster(observation: dict[str, Any]) -> dict[str, Any]:
    """Extract raster metadata from an observation result."""

    raster = observation.get("raster", observation)

    if not isinstance(raster, dict):
        return {}

    return raster


def _normalise_modality(value: Any) -> str | None:
    """Normalize a modality value for comparison."""

    if value is None:
        return None

    normalized = str(value).strip().lower()

    if not normalized:
        return None

    return normalized


def _validate_raster_structure(
    raster: dict[str, Any],
) -> dict[str, Any]:
    """Check whether basic raster structure is usable."""

    width = raster.get("width")
    height = raster.get("height")
    band_count = raster.get("bands")
    dtype = raster.get("band_details")

    dimensions_valid = (
        isinstance(width, int)
        and width > 0
        and isinstance(height, int)
        and height > 0
    )

    bands_valid = (
        isinstance(band_count, int)
        and band_count > 0
    )

    dtype_information_available = (
        isinstance(dtype, list)
        and len(dtype) == band_count
        and all(
            isinstance(band, dict)
            and band.get("dtype") is not None
            for band in dtype
        )
    )

    return {
        "dimensions": dimensions_valid,
        "bands": bands_valid,
        "dtype_information": dtype_information_available,
        "valid": (
            dimensions_valid
            and bands_valid
            and dtype_information_available
        ),
    }


def _check_required_modalities(
    modalities: list[str | None],
    required: Any,
) -> tuple[bool, str | None]:
    """
    Check observed modalities against a task requirement.

    Supported requirement forms:

    - "compatible": all observations must have the same known modality.
    - "optical": all observations must be optical.
    - "sar": all observations must be SAR.
    - ["optical", "sar"]&#58; the observations must collectively contain
      the required optical/SAR pair.
    """

    normalized = [
        modality
        for modality in modalities
        if modality is not None
    ]

    if len(normalized) != len(modalities):
        return False, "Modality information is missing for one or more observations."

    if any(modality not in SUPPORTED_MODALITIES for modality in normalized):
        return False, "One or more observations have an unsupported modality."

    if required == "compatible":
        if len(set(normalized)) == 1:
            return True, None

        return (
            False,
            "Observations have incompatible modalities.",
        )

    if isinstance(required, str):
        required = required.strip().lower()

        if required not in SUPPORTED_MODALITIES:
            return False, f"Unsupported modality requirement: {required}"

        if all(modality == required for modality in normalized):
            return True, None

        return (
            False,
            f"All observations must use modality '{required}'.",
        )

    if isinstance(required, (list, tuple, set)):
        required_modalities = {
            str(value).strip().lower()
            for value in required
        }

        if not required_modalities:
            return False, "No modality requirement was provided."

        if not required_modalities.issubset(SUPPORTED_MODALITIES):
            return False, "Modality requirement contains unsupported values."

        if required_modalities.issubset(set(normalized)):
            return True, None

        return (
            False,
            "Observed modalities do not satisfy the required modality combination.",
        )

    return False, "Invalid modality requirement."


def check_modality_compatibility(
    first: dict[str, Any],
    second: dict[str, Any] | None = None,
    required: Any = "compatible",
) -> dict[str, Any]:
    """
    Check modality compatibility and basic raster usability.

    This function checks:
    - modality availability
    - modality requirements
    - basic raster dimensions
    - band count
    - band dtype metadata

    It does not perform reprojection, resampling, registration,
    normalization, or model-specific preprocessing.
    """

    observations = [first]

    if second is not None:
        observations.append(second)

    rasters = [
        _extract_raster(observation)
        for observation in observations
    ]

    modalities = [
        _normalise_modality(raster.get("modality"))
        for raster in rasters
    ]

    modality_compatible, modality_reason = _check_required_modalities(
        modalities,
        required,
    )

    raster_checks = [
        _validate_raster_structure(raster)
        for raster in rasters
    ]

    raster_valid = all(
        check["valid"]
        for check in raster_checks
    )

    reasons = []

    if modality_reason is not None:
        reasons.append(modality_reason)

    if not raster_valid:
        reasons.append(
            "One or more observations have invalid or incomplete raster structure."
        )

    compatible = modality_compatible and raster_valid

    return {
        "compatible": compatible,
        "observations": len(observations),
        "modalities": modalities,
        "checks": {
            "modality": modality_compatible,
            "raster_structure": raster_valid,
        },
        "raster_checks": raster_checks,
        "missing_information": [
            "modality"
            for modality in modalities
            if modality is None
        ],
        "reasons": reasons,
    }