from typing import Any

from pydantic import BaseModel, Field


class RasterInfo(BaseModel):
    width: int
    height: int
    bands: int
    band_details: list[dict[str, Any]] = Field(default_factory=list)
    resolution: list[float] = Field(default_factory=list)
    crs: str | None = None
    modality: str | None = None


class BandValidation(BaseModel):
    valid: bool
    band_count: int
    same_dtype: bool
    same_dimensions: bool
    dtypes: list[str] = Field(default_factory=list)
    dimensions: dict[str, int] = Field(default_factory=dict)


class SpatialInfo(BaseModel):
    bounds: dict[str, Any] = Field(default_factory=dict)
    centroid_wgs84: list[float] = Field(default_factory=list)
    map_ready: bool


class AcquisitionInfo(BaseModel):
    datetime: str | None = None


class DataEngineResult(BaseModel):
    valid: bool
    raster: RasterInfo
    band_validation: BandValidation
    spatial: SpatialInfo
    acquisition: AcquisitionInfo