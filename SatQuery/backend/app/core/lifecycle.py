from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RequestStatus(str, Enum):
    RECEIVED = "received"
    VALIDATING = "validating"
    TASK_IDENTIFIED = "task_identified"
    REQUIREMENTS_CHECKED = "requirements_checked"
    WAITING_FOR_DATA = "waiting_for_data"
    READY = "ready"
    EXECUTION_PLANNED = "execution_planned"
    EXECUTING = "executing"
    COMPLETED = "completed"

    NEEDS_CLARIFICATION = "needs_clarification"
    NOT_READY = "not_ready"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class InvalidTransitionError(Exception):
    pass


ALLOWED_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.RECEIVED: {
        RequestStatus.VALIDATING,
        RequestStatus.FAILED,
    },
    RequestStatus.VALIDATING: {
        RequestStatus.TASK_IDENTIFIED,
        RequestStatus.NEEDS_CLARIFICATION,
        RequestStatus.FAILED,
    },
    RequestStatus.TASK_IDENTIFIED: {
        RequestStatus.REQUIREMENTS_CHECKED,
        RequestStatus.UNSUPPORTED,
        RequestStatus.FAILED,
    },
    RequestStatus.REQUIREMENTS_CHECKED: {
        RequestStatus.WAITING_FOR_DATA,
        RequestStatus.READY,
        RequestStatus.NEEDS_CLARIFICATION,
        RequestStatus.FAILED,
    },
    RequestStatus.WAITING_FOR_DATA: {
        RequestStatus.READY,
        RequestStatus.NOT_READY,
        RequestStatus.FAILED,
    },
    RequestStatus.READY: {
        RequestStatus.EXECUTION_PLANNED,
        RequestStatus.FAILED,
    },
    RequestStatus.EXECUTION_PLANNED: {
        RequestStatus.EXECUTING,
        RequestStatus.FAILED,
    },
    RequestStatus.EXECUTING: {
        RequestStatus.COMPLETED,
        RequestStatus.FAILED,
    },

    # Terminal states
    RequestStatus.COMPLETED: set(),
    RequestStatus.NEEDS_CLARIFICATION: set(),
    RequestStatus.NOT_READY: set(),
    RequestStatus.UNSUPPORTED: set(),
    RequestStatus.FAILED: set(),
}


@dataclass(frozen=True)
class LifecycleEvent:
    from_status: RequestStatus | None
    to_status: RequestStatus
    timestamp: datetime


@dataclass
class RequestLifecycle:
    request_id: str
    status: RequestStatus = RequestStatus.RECEIVED
    history: list[LifecycleEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.history.append(
            LifecycleEvent(
                from_status=None,
                to_status=self.status,
                timestamp=datetime.now(timezone.utc),
            )
        )

    def transition_to(self, new_status: RequestStatus) -> RequestStatus:
        allowed = ALLOWED_TRANSITIONS.get(self.status, set())

        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Invalid transition: "
                f"{self.status.value} -> {new_status.value}"
            )

        previous_status = self.status
        self.status = new_status

        self.history.append(
            LifecycleEvent(
                from_status=previous_status,
                to_status=new_status,
                timestamp=datetime.now(timezone.utc),
            )
        )

        return self.status

    def get_history(self) -> list[LifecycleEvent]:
        return list(self.history)

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            RequestStatus.COMPLETED,
            RequestStatus.NEEDS_CLARIFICATION,
            RequestStatus.NOT_READY,
            RequestStatus.UNSUPPORTED,
            RequestStatus.FAILED,
        }
    
