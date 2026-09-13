from app.core.exceptions import SatQueryException
from app.core.recovery import RecoveryManager





def test_recovery_manager_retries_transient_error():
    manager = RecoveryManager()

    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="Model timed out",
    )

    assert manager.handle_failure(
        "req_1000", error, 0
    ) == "retry"


def test_recovery_manager_aborts_after_retry_limit():
    manager = RecoveryManager()

    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="Model timed out",
    )

    assert manager.handle_failure(
        "req_1001", error, 2
    ) == "abort"


def test_recovery_manager_handles_non_retryable_error():
    manager = RecoveryManager()

    error = SatQueryException(
        code="DATA_INVALID",
        message="Invalid raster",
    )

    assert manager.handle_failure(
        "req_1002", error, 0
    ) == "abort"


def test_recovery_manager_prevents_completed_request():
    manager = RecoveryManager()

    manager.mark_completed("req_1003")

    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="Model timed out",
    )

    assert manager.handle_failure(
        "req_1003", error, 0
    ) == "already_completed"