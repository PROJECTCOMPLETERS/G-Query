from enum import Enum
from typing import Any

from pydantic import BaseModel

from typing import Literal

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




PHASE2_ERROR_CODES = {
    "QUERY_INVALID",
    "QUERY_AMBIGUOUS",
    "STRUCTURED_QUERY_INVALID",
    "TASK_UNSUPPORTED",
    "TASK_INVALID",
    "TASK_REQUIREMENTS_INVALID",
    "DATA_MISSING",
    "DATA_INVALID",
    "DATA_INCOMPATIBLE",
    "DATA_INSUFFICIENT",
    "DATA_QUALITY_INSUFFICIENT",
    "MODEL_UNAVAILABLE",
    "MODEL_INPUT_INVALID",
    "MODEL_INFERENCE_FAILED",
    "MODEL_TIMEOUT",
    "PREPROCESSING_FAILED",
    "POSTPROCESSING_FAILED",
    "PIPELINE_FAILED",
    "RESPONSE_GENERATION_FAILED",
    "SYSTEM_ERROR",
    "TIMEOUT",
}


class Phase2Error(BaseModel):
    code: str
    message: str
    stage: str
    recoverable: bool


class Phase2ErrorResponse(BaseModel):
    status: Literal["failed"] = "failed"
    error: Phase2Error