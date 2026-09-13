"""Evaluate whether available observations satisfy Data Requirements."""

from __future__ import annotations

from typing import Any


def _normalise_modality(value: Any) -> str | None:
    """Normalise a modality value."""
    if value is None:
        return None

    value = str(value).strip().lower()

    return value or None


def _extract_observation_modality(
    observation: dict[str, Any],
) -> str | None:
    """Extract modality from an inspected observation."""
    raster = observation.get("raster", observation)

    if not isinstance(raster, dict):
        return None

    return _normalise_modality(raster.get("modality"))


def _extract_observation_datetime(
    observation: dict[str, Any],
) -> str | None:
    """Extract acquisition datetime from an inspected observation."""
    acquisition = observation.get("acquisition", {})

    if not isinstance(acquisition, dict):
        return None

    value = acquisition.get("datetime")

    if value is None:
        return None

    return str(value).strip() or None


def _check_modality_requirements(
    observations: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check whether observations satisfy modality requirements."""

    if not requirements.get("required", False):
        return True, None

    allowed = requirements.get("allowed", [])

    if not allowed:
        return False, "Required modality information is missing."

    modalities = [
        _extract_observation_modality(observation)
        for observation in observations
    ]

    if any(modality is None for modality in modalities):
        return False, "Modality information is missing for one or more observations."

    normalised_allowed = {
        _normalise_modality(modality)
        for modality in allowed
    }

    if "compatible" in normalised_allowed:
        if len(set(modalities)) == 1:
            return True, None

    explicit_modalities = {
        modality
        for modality in normalised_allowed
        if modality != "compatible"
    }

    if explicit_modalities and set(modalities).issubset(explicit_modalities):
        return True, None

    return (
        False,
        "Available observations do not satisfy the required modality.",
    )


def _check_temporal_requirements(
    observations: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check whether required temporal information is available."""

    if not requirements.get("required", False):
        return True, None

    missing = [
        index + 1
        for index, observation in enumerate(observations)
        if _extract_observation_datetime(observation) is None
    ]

    if missing:
        return (
            False,
            "Acquisition datetime is missing for one or more observations.",
        )

    return True, None


def _check_spatial_requirements(
    observations: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check whether required spatial information is available."""

    if not requirements.get("required", False):
        return True, None

    for observation in observations:
        spatial = observation.get("spatial")

        if not isinstance(spatial, dict):
            return False, "Spatial information is missing for one or more observations."

        if not spatial.get("bounds"):
            return False, "Spatial bounds are missing for one or more observations."

    return True, None


def _check_quality_requirements(
    observations: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check basic data quality requirements."""

    if requirements.get("valid_data", True):
        invalid = [
            observation
            for observation in observations
            if observation.get("valid") is not True
        ]

        if invalid:
            return False, "One or more observations failed Data Engine validation."

    return True, None


def evaluate_data_readiness(
    *,
    request_id: str,
    task: str,
    data_requirements: dict[str, Any],
    observations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Evaluate whether available observations satisfy Data Requirements.

    Args:
        request_id:
            Request identifier from the canonical contract.

        task:
            Task identifier from the Task Engine.

        data_requirements:
            Canonical Data Requirements payload.

        observations:
            Mapping of observation ID to inspected Data Engine results.

    Returns:
        Canonical Data Readiness payload.
    """

    available_observation_ids = list(observations.keys())

    inputs = data_requirements.get("inputs", {})
    min_observations = int(inputs.get("min_observations", 1))

    missing_information: list[str] = []
    reasons: list[str] = []

    # 1. Observation count.
    if len(available_observation_ids) < min_observations:
        missing_count = min_observations - len(available_observation_ids)

        if missing_count == 1:
            missing_information.append("second_observation")
        else:
            missing_information.append(
                f"{missing_count}_additional_observations"
            )

        reasons.append(
            f"{task} requires at least {min_observations} observations."
        )

    # Only evaluate requirements against available observations.
    available_observations = list(observations.values())

    if available_observations:
        # 2. Modality.
        modality_ok, modality_reason = _check_modality_requirements(
            available_observations,
            data_requirements.get("modality", {}),
        )

        if not modality_ok:
            missing_information.append("compatible_modality")
            if modality_reason:
                reasons.append(modality_reason)

        # 3. Temporal information.
        temporal_ok, temporal_reason = _check_temporal_requirements(
            available_observations,
            data_requirements.get("temporal", {}),
        )

        if not temporal_ok:
            missing_information.append("acquisition_datetime")
            if temporal_reason:
                reasons.append(temporal_reason)

        # 4. Spatial information.
        spatial_ok, spatial_reason = _check_spatial_requirements(
            available_observations,
            data_requirements.get("spatial", {}),
        )

        if not spatial_ok:
            missing_information.append("spatial_information")
            if spatial_reason:
                reasons.append(spatial_reason)

        # 5. Quality.
        quality_ok, quality_reason = _check_quality_requirements(
            available_observations,
            data_requirements.get("quality", {}),
        )

        if not quality_ok:
            missing_information.append("valid_data")
            if quality_reason:
                reasons.append(quality_reason)

    # Remove duplicate information/reasons while preserving order.
    missing_information = list(dict.fromkeys(missing_information))
    reasons = list(dict.fromkeys(reasons))

    ready = not missing_information

    return {
        "schema_version": "1.0",
        "request_id": request_id,
        "ready": ready,
        "available_observations": available_observation_ids,
        "missing_information": missing_information,
        "reason": "; ".join(reasons) if reasons else None,
    }