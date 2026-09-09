from enum import Enum
from typing import Any

from pydantic import BaseModel


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_DATASET_ID = "INVALID_DATASET_ID"
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    INVALID_RASTER = "INVALID_RASTER"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    STORAGE_ERROR = "STORAGE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail