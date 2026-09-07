"""CRS utilities for the SatQuery Data Engine."""

from typing import Any


def normalize_crs(crs: Any) -> str | None:
    """
    Normalize a CRS into a stable string representation.

    Returns:
        A normalized CRS string such as "EPSG:32644",
        or None when CRS information is unavailable.
    """

    if crs is None:
        return None

    if isinstance(crs, str):
        value = crs.strip()

        if not value:
            return None

        return value.upper()

    if hasattr(crs, "to_epsg"):
        epsg = crs.to_epsg()

        if epsg is not None:
            return f"EPSG:{epsg}"

        value = str(crs).strip()

        if value:
            return value

    raise ValueError(
        f"Unable to normalize CRS value of type "
        f"{type(crs).__name__}"
    )


def has_crs(crs: Any) -> bool:
    """Return True when usable CRS information is available."""

    return normalize_crs(crs) is not None


def validate_crs(crs: Any) -> dict[str, Any]:
    """
    Validate CRS information and return a structured result.

    Missing CRS is not treated as an invented/default CRS.
    """

    if crs is None:
        return {
            "valid": False,
            "crs": None,
            "reason": "CRS is not defined.",
        }

    try:
        normalized = normalize_crs(crs)
    except ValueError as exc:
        return {
            "valid": False,
            "crs": None,
            "reason": str(exc),
        }

    if normalized is None:
        return {
            "valid": False,
            "crs": None,
            "reason": "CRS is not defined.",
        }

    return {
        "valid": True,
        "crs": normalized,
        "reason": None,
    }