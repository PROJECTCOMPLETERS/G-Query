from enum import Enum

from pydantic import BaseModel, Field


class DatasetType(str, Enum):
    SINGLE = "single"
    TEMPORAL = "temporal"
    MULTIMODAL = "multimodal"


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dataset_type: DatasetType