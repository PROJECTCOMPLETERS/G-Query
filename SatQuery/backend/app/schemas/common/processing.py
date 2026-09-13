from enum import Enum

from pydantic import BaseModel


class ProcessingStatus(str, Enum):
    UPLOADING = "uploading"


class Processing(BaseModel):
    status: ProcessingStatus