from dataclasses import dataclass
from typing import Protocol

from app.core.lifecycle import RequestStatus
from app.schemas.data_engine import DataReadiness, DataRequirements
from app.schemas.query import (
    ClarificationResponse,
    ObservationInput,
    StructuredQuery,
)
from app.schemas.task import ExecutionPlan
from app.services.execution_context import ExecutionContext
from app.services.query_engine import QueryEngine
from app.services.query_service import QueryService
from app.services.task_engine import TaskEngine


class DataEngineClient(Protocol):
    """
    Interface only.

    Rubin's Data Engine will provide the actual implementation later.
    """

    def check_readiness(
        self,
        requirements: DataRequirements,
        observations: list[ObservationInput],
    ) -> DataReadiness:
        ...


@dataclass
class OrchestrationResult:
    request_id: str
    status: RequestStatus
    structured_query: StructuredQuery | None = None
    data_requirements: DataRequirements | None = None
    clarification: ClarificationResponse | None = None
    data_readiness: DataReadiness | None = None
    execution_plan: ExecutionPlan | None = None


class Orchestrator:
    """
    Coordinates the backend workflow.

    Rubin's Data Engine is accessed only through DataEngineClient.
    """

    def __init__(
        self,
        query_service: QueryService | None = None,
        query_engine: QueryEngine | None = None,
        task_engine: TaskEngine | None = None,
        data_engine: DataEngineClient | None = None,
    ) -> None:
        self.query_service = query_service or QueryService()
        self.query_engine = query_engine or QueryEngine()
        self.task_engine = task_engine or TaskEngine()
        self.data_engine = data_engine
        self._contexts: dict[str, ExecutionContext] = {}

    def start_query(
        self,
        request_id: str,
        question: str,
        inputs: list[ObservationInput] | None = None,
        modality: str | None = None,
    ) -> OrchestrationResult:
        observations = inputs or []

        self.query_service.create_request(request_id)

        context = ExecutionContext(request_id=request_id)
        self._contexts[request_id] = context

        structured_query = self.query_service.process_query(
            request_id=request_id,
            question=question,
            inputs=observations,
            modality=modality,
        )

        context.set_query(structured_query)

        # Build task requirements first.
        data_requirements = (
            self.task_engine.build_data_requirements(
                structured_query
            )
        )

        context.set_data_requirements(data_requirements)

        self.query_service.update_status(
            request_id,
            RequestStatus.REQUIREMENTS_CHECKED,
        )

        # Check for missing USER information.
        clarification = self.task_engine.check_requirements(
            structured_query
        )

        if clarification is not None:
            self.query_service.update_status(
                request_id,
                RequestStatus.NEEDS_CLARIFICATION,
            )

            return OrchestrationResult(
                request_id=request_id,
                status=RequestStatus.NEEDS_CLARIFICATION,
                structured_query=structured_query,
                data_requirements=data_requirements,
                clarification=clarification,
            )

        # Stop here until Rubin's implementation is connected.
        return OrchestrationResult(
            request_id=request_id,
            status=RequestStatus.REQUIREMENTS_CHECKED,
            structured_query=structured_query,
            data_requirements=data_requirements,
        )

    def get_context(self, request_id: str) -> ExecutionContext:
        context = self._contexts.get(request_id)

        if context is None:
            raise KeyError(
                f"Execution context not found: {request_id}"
            )

        return context
    def continue_with_data_readiness(
        self,
        request_id: str,
        readiness: DataReadiness,
    ) -> OrchestrationResult:
        context = self.get_context(request_id)

        if context.data_requirements is None or context.query is None:
            raise ValueError(
                "Execution context is incomplete."
            )

        context.set_data_readiness(readiness)

        if not readiness.ready:
            self.query_service.update_status(
                request_id,
                RequestStatus.NOT_READY,
            )

            return OrchestrationResult(
                request_id=request_id,
                status=RequestStatus.NOT_READY,
                structured_query=context.query,
                data_requirements=context.data_requirements,
                data_readiness=readiness,
            )

        execution_plan = self.task_engine.build_execution_plan(
            context.query,
            readiness,
        )

        context.set_execution_plan(execution_plan)

        self.query_service.update_status(
            request_id,
            RequestStatus.READY,
        )
        self.query_service.update_status(
            request_id,
            RequestStatus.EXECUTION_PLANNED,
        )

        return OrchestrationResult(
            request_id=request_id,
            status=RequestStatus.EXECUTION_PLANNED,
            structured_query=context.query,
            data_requirements=context.data_requirements,
            data_readiness=readiness,
            execution_plan=execution_plan,
        )