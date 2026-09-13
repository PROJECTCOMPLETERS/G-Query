from typing import Any

from pydantic import BaseModel, Field
from app.schemas.contract import ContractBase

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

class InputRequirements(BaseModel):
    min_observations: int = 1
    type: str = "image"


class ModalityRequirements(BaseModel):
    required: bool = False
    allowed: list[str] = Field(default_factory=list)


class TemporalRequirements(BaseModel):
    required: bool = False
    information: dict[str, Any] | None = None


class SpatialRequirements(BaseModel):
    required: bool = False
    information: dict[str, Any] | None = None


class QualityRequirements(BaseModel):
    valid_data: bool = True
    sufficient_resolution: bool = False


class DataRequirements(ContractBase):
    task: str
    inputs: InputRequirements = Field(
        default_factory=InputRequirements
    )
    modality: ModalityRequirements = Field(
        default_factory=ModalityRequirements
    )
    temporal: TemporalRequirements = Field(
        default_factory=TemporalRequirements
    )
    spatial: SpatialRequirements = Field(
        default_factory=SpatialRequirements
    )
    quality: QualityRequirements = Field(
        default_factory=QualityRequirements
    )
    task_specific: dict[str, Any] = Field(
        default_factory=dict
    )
class DataReadiness(ContractBase):
    ready: bool
    available_observations: list[str] = Field(
        default_factory=list
    )
    missing_information: list[str] = Field(
        default_factory=list
    )
    reason: str | None = None