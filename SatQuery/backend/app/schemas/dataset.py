from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Dataset(BaseModel):
    """Stable SatQuery representation of a dataset."""

    dataset_id: str
    filename: str
    file_type: str
    size: int = Field(ge=0)
    status: str
    gridfs_file_id: str

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime


class DatasetCreate(BaseModel):
    """Data required when creating a dataset."""

    dataset_id: str
    filename: str
    file_type: str
    size: int = Field(ge=0)
    status: str = "uploaded"
    gridfs_file_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)