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