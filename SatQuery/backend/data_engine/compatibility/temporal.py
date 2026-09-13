"""Temporal compatibility checks for satellite observations."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _extract_datetime(observation: dict[str, Any]) -> str | None:
    """Extract acquisition datetime from an observation result."""

    acquisition = observation.get("acquisition", {})

    if not isinstance(acquisition, dict):
        return None

    value = acquisition.get("datetime")

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _parse_datetime(value: str) -> datetime | None:
    """Parse an ISO-8601 datetime string safely."""

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def check_temporal_compatibility(
    first: dict[str, Any],
    second: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare the temporal metadata of two observations.

    The function checks whether both observations contain valid
    acquisition timestamps and whether their chronological ordering
    can be established.

    It does not determine whether the time interval is appropriate
    for a particular task. That decision belongs to the task
    requirements supplied by the Task Engine.

    Returns:
        A structured temporal compatibility result.
    """

    first_value = _extract_datetime(first)
    second_value = _extract_datetime(second)

    if first_value is None or second_value is None:
        missing = []

        if first_value is None:
            missing.append("first_observation_datetime")

        if second_value is None:
            missing.append("second_observation_datetime")

        return {
            "compatible": False,
            "checks": {
                "first_datetime_available": first_value is not None,
                "second_datetime_available": second_value is not None,
                "valid_datetime_values": False,
                "chronological_order": None,
            },
            "missing_information": missing,
            "reason": "Acquisition datetime is missing for one or both observations.",
        }

    first_datetime = _parse_datetime(first_value)
    second_datetime = _parse_datetime(second_value)

    if first_datetime is None or second_datetime is None:
        invalid = []

        if first_datetime is None:
            invalid.append("first_observation_datetime")

        if second_datetime is None:
            invalid.append("second_observation_datetime")

        return {
            "compatible": False,
            "checks": {
                "first_datetime_available": True,
                "second_datetime_available": True,
                "valid_datetime_values": False,
                "chronological_order": None,
            },
            "missing_information": [],
            "invalid_information": invalid,
            "reason": "One or both acquisition datetime values are invalid.",
        }

    chronological_order = (
        "before"
        if first_datetime < second_datetime
        else "after"
        if first_datetime > second_datetime
        else "same"
    )

    return {
        "compatible": True,
        "checks": {
            "first_datetime_available": True,
            "second_datetime_available": True,
            "valid_datetime_values": True,
            "chronological_order": chronological_order,
        },
        "missing_information": [],
        "reason": None,
    }
