from app.schemas.query import (
    ClarificationResponse,
    StructuredQuery,
)
from app.schemas.data_engine import (
    DataReadiness,
    DataRequirements,
)
from app.schemas.task import ExecutionPlan
from app.schemas.result import AnalysisResult
from app.schemas.common.error import (
    Phase2Error,
    Phase2ErrorResponse,
)
from app.core.lifecycle import (
    InvalidTransitionError,
    RequestLifecycle,
    RequestStatus,
)
from app.core.exceptions import (
    RecoveryAction,
    SatQueryException,
)
from app.services.query_service import QueryService

def test_structured_query():
    query = StructuredQuery(
        request_id="req_001",
        question="How many buildings are in this image?",
        intent="object_counting",
        entities=["building"],
        inputs=[{"input_id": "obs_001", "type": "image"}],
        modality="optical",
        requested_capabilities=["object_detection", "counting"],
    )

    assert query.schema_version == "1.0"
    assert query.request_id == "req_001"
    assert query.intent == "object_counting"
    assert query.inputs[0].input_id == "obs_001"


def test_data_requirements():
    requirements = DataRequirements(
        request_id="req_002",
        task="object_counting",
        inputs={
            "min_observations": 1,
            "type": "image",
        },
        modality={
            "required": True,
            "allowed": ["optical"],
        },
    )

    assert requirements.schema_version == "1.0"
    assert requirements.task == "object_counting"
    assert requirements.inputs.min_observations == 1
    assert requirements.modality.allowed == ["optical"]


def test_data_readiness_ready():
    readiness = DataReadiness(
        request_id="req_003",
        ready=True,
        available_observations=["obs_001"],
    )

    assert readiness.ready is True
    assert readiness.available_observations == ["obs_001"]


def test_data_readiness_not_ready():
    readiness = DataReadiness(
        request_id="req_004",
        ready=False,
        available_observations=["obs_001"],
        missing_information=["second observation required"],
        reason="Comparison requires two observations",
    )

    assert readiness.ready is False
    assert "second observation required" in readiness.missing_information
    assert readiness.reason == "Comparison requires two observations"


def test_execution_plan():
    plan = ExecutionPlan(
        request_id="req_005",
        task="object_counting",
        input_observations=["obs_001"],
        required_modalities=["optical"],
        preprocessing=["normalize", "resize"],
        model_requirements={
            "capabilities": [
                "object_detection",
                "counting",
            ]
        },
        expected_output={
            "type": "count",
            "spatial_output": True,
        },
    )

    assert plan.schema_version == "1.0"
    assert plan.task == "object_counting"
    assert plan.input_observations == ["obs_001"]
    assert "object_detection" in plan.model_requirements.capabilities


def test_analysis_result():
    result = AnalysisResult(
        request_id="req_006",
        status="completed",
        task="object_counting",
        result={
            "type": "count",
            "target": "building",
            "count": 42,
        },
        spatial_output={
            "type": "polygons",
            "features": [],
        },
    )

    assert result.status == "completed"
    assert result.task == "object_counting"
    assert result.result["count"] == 42


def test_clarification_response():
    response = ClarificationResponse(
        request_id="req_007",
        missing_information=["second observation required"],
        question="Please provide the second satellite image.",
    )

    assert response.status == "needs_clarification"
    assert response.request_id == "req_007"
    assert len(response.missing_information) == 1


def test_phase2_error_response():
    error = Phase2ErrorResponse(
        error=Phase2Error(
            code="DATA_INCOMPATIBLE",
            message="Image modality is not supported for this task.",
            stage="data_validation",
            recoverable=False,
        )
    )

    assert error.status == "failed"
    assert error.error.code == "DATA_INCOMPATIBLE"
    assert error.error.stage == "data_validation"
    assert error.error.recoverable is False
def test_request_lifecycle_happy_path():
    lifecycle = RequestLifecycle("req_100")

    lifecycle.transition_to(RequestStatus.VALIDATING)
    lifecycle.transition_to(RequestStatus.TASK_IDENTIFIED)
    lifecycle.transition_to(RequestStatus.REQUIREMENTS_CHECKED)
    lifecycle.transition_to(RequestStatus.WAITING_FOR_DATA)
    lifecycle.transition_to(RequestStatus.READY)
    lifecycle.transition_to(RequestStatus.EXECUTION_PLANNED)
    lifecycle.transition_to(RequestStatus.EXECUTING)
    lifecycle.transition_to(RequestStatus.COMPLETED)

    assert lifecycle.status == RequestStatus.COMPLETED


def test_request_lifecycle_clarification_branch():
    lifecycle = RequestLifecycle("req_101")

    lifecycle.transition_to(RequestStatus.VALIDATING)
    lifecycle.transition_to(RequestStatus.NEEDS_CLARIFICATION)

    assert lifecycle.status == RequestStatus.NEEDS_CLARIFICATION


def test_request_lifecycle_rejects_invalid_transition():
    lifecycle = RequestLifecycle("req_102")

    try:
        lifecycle.transition_to(RequestStatus.COMPLETED)
        assert False, "Expected InvalidTransitionError"
    except InvalidTransitionError:
        pass


def test_terminal_state_cannot_transition():
    lifecycle = RequestLifecycle(
        "req_103",
        status=RequestStatus.COMPLETED,
    )

    try:
        lifecycle.transition_to(RequestStatus.RECEIVED)
        assert False, "Expected InvalidTransitionError"
    except InvalidTransitionError:
        pass
def test_retryable_error():
    error = SatQueryException(
        code="MODEL_TIMEOUT",
        message="Model timed out",
    )

    assert error.is_retryable is True
    assert error.default_recovery == RecoveryAction.RETRY


def test_ambiguous_query_requires_clarification():
    error = SatQueryException(
        code="QUERY_AMBIGUOUS",
        message="Target is unclear",
    )

    assert error.is_retryable is False
    assert error.default_recovery == RecoveryAction.CLARIFY


def test_missing_data_requires_wait():
    error = SatQueryException(
        code="DATA_MISSING",
        message="Required observation unavailable",
    )

    assert error.is_retryable is False
    assert error.default_recovery == RecoveryAction.WAIT


def test_unsupported_task_aborts():
    error = SatQueryException(
        code="TASK_UNSUPPORTED",
        message="Requested task is unsupported",
    )

    assert error.is_retryable is False
    assert error.default_recovery == RecoveryAction.ABORT


def test_invalid_input_is_not_retryable():
    error = SatQueryException(
        code="QUERY_INVALID",
        message="Invalid query",
    )

    assert error.is_retryable is False
    assert error.default_recovery == RecoveryAction.ABORT
def test_request_lifecycle_records_history():
    lifecycle = RequestLifecycle("req_104")

    lifecycle.transition_to(RequestStatus.VALIDATING)
    lifecycle.transition_to(RequestStatus.TASK_IDENTIFIED)

    history = lifecycle.get_history()

    assert len(history) == 3
    assert history[0].from_status is None
    assert history[0].to_status == RequestStatus.RECEIVED
    assert history[1].from_status == RequestStatus.RECEIVED
    assert history[1].to_status == RequestStatus.VALIDATING
    assert history[2].from_status == RequestStatus.VALIDATING
    assert history[2].to_status == RequestStatus.TASK_IDENTIFIED


def test_request_lifecycle_records_timestamps():
    lifecycle = RequestLifecycle("req_105")

    lifecycle.transition_to(RequestStatus.VALIDATING)

    history = lifecycle.get_history()

    assert history[0].timestamp is not None
    assert history[1].timestamp is not None


def test_completed_request_is_terminal():
    lifecycle = RequestLifecycle("req_106")

    lifecycle.transition_to(RequestStatus.VALIDATING)
    lifecycle.transition_to(RequestStatus.TASK_IDENTIFIED)
    lifecycle.transition_to(RequestStatus.REQUIREMENTS_CHECKED)
    lifecycle.transition_to(RequestStatus.READY)
    lifecycle.transition_to(RequestStatus.EXECUTION_PLANNED)
    lifecycle.transition_to(RequestStatus.EXECUTING)
    lifecycle.transition_to(RequestStatus.COMPLETED)

    assert lifecycle.is_terminal is True


def test_active_request_is_not_terminal():
    lifecycle = RequestLifecycle("req_107")

    lifecycle.transition_to(RequestStatus.VALIDATING)

    assert lifecycle.is_terminal is False
def test_query_service_create_request():
    service = QueryService()

    lifecycle = service.create_request("req_200")

    assert lifecycle.request_id == "req_200"
    assert lifecycle.status == RequestStatus.RECEIVED


def test_query_service_rejects_duplicate_request():
    service = QueryService()

    service.create_request("req_201")

    try:
        service.create_request("req_201")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_query_service_get_request():
    service = QueryService()

    created = service.create_request("req_202")
    fetched = service.get_request("req_202")

    assert fetched is created
    assert fetched.request_id == "req_202"


def test_query_service_update_status():
    service = QueryService()

    service.create_request("req_203")
    new_status = service.update_status(
        "req_203",
        RequestStatus.VALIDATING,
    )

    assert new_status == RequestStatus.VALIDATING
    assert service.get_status("req_203") == RequestStatus.VALIDATING


def test_query_service_get_history():
    service = QueryService()

    service.create_request("req_204")
    service.update_status(
        "req_204",
        RequestStatus.VALIDATING,
    )

    history = service.get_history("req_204")

    assert len(history) == 2
    assert history[0].to_status == RequestStatus.RECEIVED
    assert history[1].to_status == RequestStatus.VALIDATING


def test_query_service_unknown_request():
    service = QueryService()

    try:
        service.get_request("req_205")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_query_service_delete_request():
    service = QueryService()

    service.create_request("req_206")
    service.delete_request("req_206")

    try:
        service.get_request("req_206")
        assert False, "Expected KeyError"
    except KeyError:
        pass