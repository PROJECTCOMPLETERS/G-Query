from typing import Any

from pydantic import BaseModel


class BoundingBox(BaseModel):
    west: float
    south: float
    east: float
    north: float


class Spatial(BaseModel):
    crs_status: str
    source_crs: str | None = None

    native_bounds: BoundingBox | None = None
    wgs84_bounds: BoundingBox | None = None

    footprint_geojson: dict[str, Any] | None = None
    centroid_wgs84: list[float] | None = None

    map_ready: bool
    map_unavailable_reason: str | None = None

    transform: dict[str, float] | None = None