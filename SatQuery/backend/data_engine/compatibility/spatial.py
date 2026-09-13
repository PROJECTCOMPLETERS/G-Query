"""Spatial compatibility checks for satellite raster observations."""

from __future__ import annotations

from math import isclose
from typing import Any


DEFAULT_TOLERANCE = 1e-6


def _normalise_resolution(
    resolution: Any,
) -> tuple[float, float] | None:
    """Convert a resolution value into an (x, y) tuple."""
    if resolution is None:
        return None

    try:
        if len(resolution) != 2:
            return None

        x = float(resolution[0])
        y = float(resolution[1])

        if x <= 0 or y <= 0:
            return None

        return x, y
    except (TypeError, ValueError):
        return None


def _normalise_crs(crs: Any) -> str | None:
    """Normalise a CRS value for comparison."""
    if crs is None:
        return None

    value = str(crs).strip().upper()

    if not value:
        return None

    return value


def _extract_bounds(
    spatial: dict[str, Any],
) -> dict[str, float] | None:
    """Extract WGS84 bounds from spatial metadata."""
    bounds = spatial.get("bounds")

    if not isinstance(bounds, dict):
        return None

    required = ("west", "south", "east", "north")

    if not all(key in bounds for key in required):
        return None

    try:
        return {
            key: float(bounds[key])
            for key in required
        }
    except (TypeError, ValueError):
        return None


def _bounds_overlap(
    first: dict[str, float],
    second: dict[str, float],
    tolerance: float = DEFAULT_TOLERANCE,
) -> bool:
    """Return whether two bounding boxes overlap."""
    return not (
        first["east"] < second["west"] - tolerance
        or second["east"] < first["west"] - tolerance
        or first["north"] < second["south"] - tolerance
        or second["north"] < first["south"] - tolerance
    )


def _extract_transform(
    raster: dict[str, Any],
) -> dict[str, float] | None:
    """Extract affine transform coefficients."""
    transform = raster.get("transform")

    if not isinstance(transform, dict):
        return None

    required = ("a", "b", "c", "d", "e", "f")

    if not all(key in transform for key in required):
        return None

    try:
        return {
            key: float(transform[key])
            for key in required
        }
    except (TypeError, ValueError):
        return None


def _transforms_aligned(
    first: dict[str, float],
    second: dict[str, float],
    tolerance: float = DEFAULT_TOLERANCE,
) -> bool:
    """Check whether two affine transforms are equivalent."""
    return all(
        isclose(
            first[key],
            second[key],
            rel_tol=0.0,
            abs_tol=tolerance,
        )
        for key in ("a", "b", "c", "d", "e", "f")
    )


def check_spatial_compatibility(
    first: dict[str, Any],
    second: dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, Any]:
    """
    Compare the spatial properties of two raster observations.

    Checks:
    - CRS
    - resolution
    - spatial overlap
    - grid alignment

    The result is intentionally explainable so that a later Task
    Engine can determine whether preprocessing is required.

    Args:
        first: Metadata for the first raster observation.
        second: Metadata for the second raster observation.
        tolerance: Numeric comparison tolerance.

    Returns:
        A structured compatibility result.
    """

    first_raster = first.get("raster", first)
    second_raster = second.get("raster", second)

    first_spatial = first.get("spatial", {})
    second_spatial = second.get("spatial", {})

    # ---------------------------------------------------------
    # 1. CRS
    # ---------------------------------------------------------
    first_crs = _normalise_crs(first_raster.get("crs"))
    second_crs = _normalise_crs(second_raster.get("crs"))

    crs_compatible = (
        first_crs is not None
        and second_crs is not None
        and first_crs == second_crs
    )

    # ---------------------------------------------------------
    # 2. Resolution
    # ---------------------------------------------------------
    first_resolution = _normalise_resolution(
        first_raster.get("resolution")
    )
    second_resolution = _normalise_resolution(
        second_raster.get("resolution")
    )

    resolution_compatible = (
        first_resolution is not None
        and second_resolution is not None
        and isclose(
            first_resolution[0],
            second_resolution[0],
            rel_tol=0.0,
            abs_tol=tolerance,
        )
        and isclose(
            first_resolution[1],
            second_resolution[1],
            rel_tol=0.0,
            abs_tol=tolerance,
        )
    )

    # ---------------------------------------------------------
    # 3. Spatial overlap
    # ---------------------------------------------------------
    first_bounds = _extract_bounds(first_spatial)
    second_bounds = _extract_bounds(second_spatial)

    bounds_compatible = (
        first_bounds is not None
        and second_bounds is not None
        and _bounds_overlap(
            first_bounds,
            second_bounds,
            tolerance,
        )
    )

    # ---------------------------------------------------------
    # 4. Grid alignment
    # ---------------------------------------------------------
    first_transform = _extract_transform(first_raster)
    second_transform = _extract_transform(second_raster)

    alignment_compatible = (
        first_transform is not None
        and second_transform is not None
        and _transforms_aligned(
            first_transform,
            second_transform,
            tolerance,
        )
    )

    # ---------------------------------------------------------
    # Explainability
    # ---------------------------------------------------------
    reasons: list[str] = []
    preprocessing_required: list[str] = []

    if first_crs is None or second_crs is None:
        reasons.append("CRS information is missing.")
        preprocessing_required.append("CRS definition/reprojection")
    elif not crs_compatible:
        reasons.append("CRS mismatch.")
        preprocessing_required.append("reprojection")

    if first_resolution is None or second_resolution is None:
        reasons.append("Raster resolution information is missing.")
        preprocessing_required.append("resampling")
    elif not resolution_compatible:
        reasons.append("Resolution mismatch.")
        preprocessing_required.append("resampling")

    if first_bounds is None or second_bounds is None:
        reasons.append("Spatial bounds are missing.")
    elif not bounds_compatible:
        reasons.append("Raster observations do not overlap spatially.")

    if first_transform is None or second_transform is None:
        reasons.append("Affine transform information is missing.")
        preprocessing_required.append("grid alignment")
    elif not alignment_compatible:
        reasons.append("Raster grids are not aligned.")
        preprocessing_required.append("registration/alignment")

    compatible = (
        crs_compatible
        and resolution_compatible
        and bounds_compatible
        and alignment_compatible
    )

    return {
        "compatible": compatible,
        "checks": {
            "crs": crs_compatible,
            "resolution": resolution_compatible,
            "bounds": bounds_compatible,
            "alignment": alignment_compatible,
        },
        "preprocessing_required": bool(preprocessing_required),
        "preprocessing": sorted(set(preprocessing_required)),
        "reasons": reasons,
    }