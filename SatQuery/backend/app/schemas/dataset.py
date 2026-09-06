from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    """
    Flexible metadata produced by the satellite data engine.

    Extra fields are allowed so the schema does not depend
    on a specific data-engine implementation.
    """

    model_config = {
        "extra": "allow",
    }


class Dataset(BaseModel):
    """
    Stable SatQuery representation of a dataset.
    """

    dataset_id: str
    filename: str
    file_type: str
    size: int = Field(ge=0)
    status: str
    storage_path: str

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime


class DatasetCreate(BaseModel):
    """
    Data required when creating a dataset record.
    """

    dataset_id: str
    filename: str
    file_type: str
    size: int = Field(ge=0)
    status: str = "uploaded"
    storage_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)