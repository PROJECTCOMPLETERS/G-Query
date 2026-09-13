from enum import Enum


class RecoveryAction(str, Enum):
    RECOVER = "recover"
    RETRY = "retry"
    CLARIFY = "clarify"
    WAIT = "wait"
    FALLBACK = "fallback"
    ABORT = "abort"


TRANSIENT_ERROR_CODES = {
    "MODEL_INFERENCE_FAILED",
    "MODEL_TIMEOUT",
    "TIMEOUT",
    "SYSTEM_ERROR",
}


NON_RETRYABLE_ERROR_CODES = {
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
    "PREPROCESSING_FAILED",
    "POSTPROCESSING_FAILED",
    "RESPONSE_GENERATION_FAILED",
}


class SatQueryException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details=None,
    ):
        self.code = code
        self.message = message
        self.details = details

        super().__init__(message)

    @property
    def is_retryable(self) -> bool:
        return self.code in TRANSIENT_ERROR_CODES

    @property
    def default_recovery(self) -> RecoveryAction:
        if self.is_retryable:
            return RecoveryAction.RETRY

        if self.code == "DATA_MISSING":
            return RecoveryAction.WAIT

        if self.code == "QUERY_AMBIGUOUS":
            return RecoveryAction.CLARIFY

        if self.code == "TASK_UNSUPPORTED":
            return RecoveryAction.ABORT

        return RecoveryAction.ABORT