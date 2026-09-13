from app.core.exceptions import SatQueryException
from app.core.recovery import IdempotencyGuard, RetryPolicy
from app.core.exceptions import (
    SatQueryException,
    to_phase2_error_response,
)


def test_retry_policy_allows_transient_error():
    policy = RetryPolicy(max_retries=2)

    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="timeout",
    )

    assert policy.should_retry(error, 0) is True
    assert policy.should_retry(error, 1) is True
    assert policy.should_retry(error, 2) is False


def test_retry_policy_rejects_non_transient_error():
    policy = RetryPolicy(max_retries=2)

    error = SatQueryException(
        code="DATA_INVALID",
        message="invalid raster",
    )

    assert policy.should_retry(error, 0) is False


def test_idempotency_guard():
    guard = IdempotencyGuard()

    assert guard.is_completed("req_900") is False

    guard.mark_completed("req_900")

    assert guard.is_completed("req_900") is True


def test_same_request_is_not_repeated_after_completion():
    guard = IdempotencyGuard()

    guard.mark_completed("req_901")

    assert guard.is_completed("req_901") is True



def test_exception_to_phase2_error_response():
    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="Model timed out",
    )

    response = to_phase2_error_response(error)

    assert response.status == "failed"
    assert response.error.code == "MODEL_TIMEOUT"
    assert response.error.stage == "orchestration"
    assert response.error.recoverable is True