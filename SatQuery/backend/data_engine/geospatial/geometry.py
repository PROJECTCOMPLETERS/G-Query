"""Raster grid geometry utilities for the SatQuery Data Engine."""

from typing import Any

from affine import Affine


def extract_resolution(transform: Any) -> tuple[float, float]:
    """
    Extract pixel resolution from a raster affine transform.

    Returns:
        A tuple of (x_resolution, y_resolution).

    Raises:
        ValueError: If the transform is invalid.
    """

    try:
        affine = Affine(*transform) if not isinstance(transform, Affine) else transform

        x_resolution = abs(float(affine.a))
        y_resolution = abs(float(affine.e))

    except Exception as exc:
        raise ValueError(
            f"Unable to extract raster resolution: {exc}"
        ) from exc

    if x_resolution == 0 or y_resolution == 0:
        raise ValueError("Raster resolution cannot be zero.")

    return x_resolution, y_resolution


def transform_to_dict(transform: Any) -> dict[str, float]:
    """
    Convert a raster affine transform into a standardized dictionary.

    Returns:
        The six affine transformation coefficients.
    """

    try:
        affine = Affine(*transform) if not isinstance(transform, Affine) else transform

        return {
            "a": float(affine.a),
            "b": float(affine.b),
            "c": float(affine.c),
            "d": float(affine.d),
            "e": float(affine.e),
            "f": float(affine.f),
        }

    except Exception as exc:
        raise ValueError(
            f"Unable to serialize raster transform: {exc}"
        ) from exc


def validate_resolution(
    resolution: Any,
) -> dict[str, Any]:
    """
    Validate raster pixel resolution.

    Returns:
        A structured validation result.
    """

    if resolution is None:
        return {
            "valid": False,
            "resolution": None,
            "reason": "Raster resolution is not defined.",
        }

    try:
        if len(resolution) != 2:
            raise ValueError(
                "Raster resolution must contain exactly two values."
            )

        x_resolution = float(resolution[0])
        y_resolution = float(resolution[1])

        if x_resolution <= 0 or y_resolution <= 0:
            raise ValueError(
                "Raster resolution values must be greater than zero."
            )

    except (TypeError, ValueError) as exc:
        return {
            "valid": False,
            "resolution": None,
            "reason": str(exc),
        }

    return {
        "valid": True,
        "resolution": [x_resolution, y_resolution],
        "reason": None,
    }