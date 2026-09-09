
from pydantic import BaseModel, Field

from app.schemas.common.dataset import DatasetType
from app.schemas.common.observation import Observation
from app.schemas.common.pagination import Pagination
from app.schemas.common.processing import Processing


class DatasetResponse(BaseModel):
    dataset_id: str
    name: str
    dataset_type: DatasetType
    processing: Processing
    observations: list[Observation] = Field(
        default_factory=list
    )


class DatasetListResponse(Pagination):
    items: list[DatasetResponse]
