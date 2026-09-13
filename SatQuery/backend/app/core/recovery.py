from dataclasses import dataclass
from dataclasses import dataclass, field

from app.core.exceptions import SatQueryException


@dataclass
class RetryPolicy:
    max_retries: int = 2

    def should_retry(
        self,
        error: SatQueryException,
        retry_count: int,
    ) -> bool:
        return (
            error.is_retryable
            and retry_count < self.max_retries
        )


class IdempotencyGuard:
    def __init__(self) -> None:
        self._completed_requests: set[str] = set()

    def is_completed(self, request_id: str) -> bool:
        return request_id in self._completed_requests

    def mark_completed(self, request_id: str) -> None:
        self._completed_requests.add(request_id)


@dataclass
class RecoveryManager:
    retry_policy: RetryPolicy = field(
        default_factory=RetryPolicy
    )
    idempotency_guard: IdempotencyGuard = field(
        default_factory=IdempotencyGuard
    )

    def handle_failure(
        self,
        request_id: str,
        error: SatQueryException,
        retry_count: int,
    ) -> str:
        if self.idempotency_guard.is_completed(request_id):
            return "already_completed"

        if self.retry_policy.should_retry(error, retry_count):
            return "retry"

        if error.is_retryable:
            return "abort"

        return error.default_recovery.value

    def mark_completed(self, request_id: str) -> None:
        self.idempotency_guard.mark_completed(request_id)