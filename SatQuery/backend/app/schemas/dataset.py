from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


DatasetType = Literal["single", "temporal", "multimodal"]


class ProcessingStatus(BaseModel):
    status: str = "uploading"
    created_at: datetime
    updated_at: datetime


class DatasetFile(BaseModel):
    file_id: str
    gridfs_id: str
    filename: str
    content_type: str
    size_bytes: int = Field(ge=0)
    processing: str = "pending"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Dataset(BaseModel):
    dataset_id: str
    name: str
    dataset_type: DatasetType

    observations: list[dict[str, Any]] = Field(default_factory=list)
    files: list[DatasetFile] = Field(default_factory=list)

    processing: ProcessingStatus

    created_at: datetime
    updated_at: datetime


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dataset_type: DatasetType


def utc_now() -> datetime:
    return datetime.now(timezone.utc)