"""Coordinate transformation utilities for the SatQuery Data Engine."""

from typing import Any

from pyproj import CRS, Transformer


def transform_coordinate(
    x: float,
    y: float,
    source_crs: Any,
    target_crs: Any,
) -> tuple[float, float]:
    """
    Transform a single coordinate from one CRS to another.

    Args:
        x: X coordinate, typically longitude or easting.
        y: Y coordinate, typically latitude or northing.
        source_crs: Source coordinate reference system.
        target_crs: Target coordinate reference system.

    Returns:
        A tuple containing the transformed (x, y) coordinate.

    Raises:
        ValueError: If either CRS is invalid or the coordinate
            transformation cannot be performed.
    """

    try:
        source = CRS.from_user_input(source_crs)
        target = CRS.from_user_input(target_crs)

        transformer = Transformer.from_crs(
            source,
            target,
            always_xy=True,
        )

        transformed_x, transformed_y = transformer.transform(x, y)

        return float(transformed_x), float(transformed_y)

    except Exception as exc:
        raise ValueError(
            f"Unable to transform coordinate from "
            f"{source_crs} to {target_crs}: {exc}"
        ) from exc