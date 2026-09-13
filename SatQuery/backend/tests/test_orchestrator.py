from dataclasses import dataclass

from app.core.lifecycle import RequestStatus
from app.schemas.data_engine import DataReadiness, DataRequirements
from app.schemas.query import ObservationInput
from app.services.orchestrator import Orchestrator


@dataclass
class FakeDataEngineClient:
    readiness: DataReadiness

    def check_readiness(
        self,
        request_id: str,
        task: str,
        requirements: DataRequirements,
        observations: list[ObservationInput],
    ) -> DataReadiness:
        assert request_id == self.readiness.request_id
        return self.readiness


def test_orchestrator_normal_flow():
    data_engine = FakeDataEngineClient(
        readiness=DataReadiness(
            request_id="req_800",
            ready=True,
            available_observations=["obs_001"],
        )
    )

    orchestrator = Orchestrator(
        data_engine=data_engine,
    )

    result = orchestrator.start_query(
        request_id="req_800",
        question="How many buildings are in this image?",
        inputs=[
            {
                "input_id": "obs_001",
                "type": "image",
            }
        ],
        modality="optical",
    )

    assert result.status == RequestStatus.WAITING_FOR_DATA
    assert result.structured_query is not None
    assert result.data_requirements is not None
    assert result.data_requirements.task == "object_counting"


def test_orchestrator_clarification_flow():
    orchestrator = Orchestrator()

    result = orchestrator.start_query(
        request_id="req_801",
        question="How many buildings are in this image?",
        inputs=[],
        modality="optical",
    )

    assert result.status == RequestStatus.NEEDS_CLARIFICATION
    assert result.clarification is not None
    assert result.structured_query is not None


def test_orchestrator_ready_flow():
    data_engine = FakeDataEngineClient(
        readiness=DataReadiness(
            request_id="req_802",
            ready=True,
            available_observations=["obs_001"],
        )
    )

    orchestrator = Orchestrator(
        data_engine=data_engine,
    )

    orchestrator.start_query(
        request_id="req_802",
        question="How many buildings are in this image?",
        inputs=[
            {
                "input_id": "obs_001",
                "type": "image",
            }
        ],
        modality="optical",
    )

    result = orchestrator.continue_with_data_readiness(
        "req_802",
    )

    assert result.status == RequestStatus.EXECUTION_PLANNED
    assert result.execution_plan is not None
    assert result.execution_plan.task == "object_counting"
    assert result.data_readiness is not None
    assert result.data_readiness.ready is True


def test_orchestrator_not_ready_flow():
    data_engine = FakeDataEngineClient(
        readiness=DataReadiness(
            request_id="req_803",
            ready=False,
            available_observations=["obs_001"],
            reason="Insufficient resolution",
        )
    )

    orchestrator = Orchestrator(
        data_engine=data_engine,
    )

    orchestrator.start_query(
        request_id="req_803",
        question="How many buildings are in this image?",
        inputs=[
            {
                "input_id": "obs_001",
                "type": "image",
            }
        ],
        modality="optical",
    )

    result = orchestrator.continue_with_data_readiness(
        "req_803",
    )

    assert result.status == RequestStatus.NOT_READY
    assert result.data_readiness is not None
    assert result.data_readiness.ready is False


def test_orchestrator_context_contains_plan_after_ready():
    data_engine = FakeDataEngineClient(
        readiness=DataReadiness(
            request_id="req_804",
            ready=True,
            available_observations=["obs_001"],
        )
    )

    orchestrator = Orchestrator(
        data_engine=data_engine,
    )

    orchestrator.start_query(
        request_id="req_804",
        question="How many buildings are in this image?",
        inputs=[
            {
                "input_id": "obs_001",
                "type": "image",
            }
        ],
        modality="optical",
    )

    orchestrator.continue_with_data_readiness(
        "req_804",
    )

    context = orchestrator.get_context("req_804")

    assert context.request_id == "req_804"
    assert context.query is not None
    assert context.data_requirements is not None
    assert context.data_readiness is not None
    assert context.execution_plan is not None