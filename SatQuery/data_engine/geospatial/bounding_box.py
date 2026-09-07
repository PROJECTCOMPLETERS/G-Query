"""Geographic bounding-box utilities for the SatQuery Data Engine."""

from typing import Any


def create_bounding_box(
    west: float,
    south: float,
    east: float,
    north: float,
) -> dict[str, float]:
    """
    Create a standardized geographic bounding box.

    Coordinates are expected in the order:
        west, south, east, north

    Returns:
        A dictionary containing the four bounding-box coordinates.

    Raises:
        ValueError: If the bounds are geographically invalid.
    """

    west = float(west)
    south = float(south)
    east = float(east)
    north = float(north)

    if west > east:
        raise ValueError("West bound cannot be greater than east bound.")

    if south > north:
        raise ValueError("South bound cannot be greater than north bound.")

    if not -180 <= west <= 180:
        raise ValueError("West longitude must be between -180 and 180.")

    if not -180 <= east <= 180:
        raise ValueError("East longitude must be between -180 and 180.")

    if not -90 <= south <= 90:
        raise ValueError("South latitude must be between -90 and 90.")

    if not -90 <= north <= 90:
        raise ValueError("North latitude must be between -90 and 90.")

    return {
        "west": west,
        "south": south,
        "east": east,
        "north": north,
    }


def validate_bounding_box(bounds: Any) -> dict[str, Any]:
    """
    Validate a geographic bounding box.

    Returns:
        A structured validation result.
    """

    if bounds is None:
        return {
            "valid": False,
            "bounds": None,
            "reason": "Bounding box is not defined.",
        }

    if not isinstance(bounds, dict):
        return {
            "valid": False,
            "bounds": None,
            "reason": "Bounding box must be a dictionary.",
        }

    required_keys = {"west", "south", "east", "north"}

    if not required_keys.issubset(bounds):
        return {
            "valid": False,
            "bounds": None,
            "reason": "Bounding box is missing one or more required coordinates.",
        }

    try:
        normalized = create_bounding_box(
            bounds["west"],
            bounds["south"],
            bounds["east"],
            bounds["north"],
        )
    except (TypeError, ValueError) as exc:
        return {
            "valid": False,
            "bounds": None,
            "reason": str(exc),
        }

    return {
        "valid": True,
        "bounds": normalized,
        "reason": None,
    }