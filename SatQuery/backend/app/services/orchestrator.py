from dataclasses import dataclass
from typing import Protocol

from app.core.lifecycle import RequestStatus
from app.schemas.data_engine import (
    DataReadiness,
    DataRequirements,
)
from app.schemas.query import (
    ClarificationResponse,
    ObservationInput,
    StructuredQuery,
)
from app.schemas.task import ExecutionPlan
from app.services.execution_context import ExecutionContext
from app.services.query_service import QueryService
from app.services.task_engine import (
    TaskEngine,
    UnsupportedTaskError,
)


class DataEngineClient(Protocol):
    """
    Interface for Rubin's Data Engine.

    The actual Data Engine implementation can be connected
    later without changing the Orchestrator contract.
    """

    def check_readiness(
        self,
        requirements: DataRequirements,
        observations: list[ObservationInput],
    ) -> DataReadiness:
        ...


@dataclass
class OrchestrationResult:
    """
    Result produced by the orchestration layer.
    """

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

    Satellite-analysis flow:

        Request
          ↓
        QueryService
          ↓
        Query Engine
          ↓
        StructuredQuery
          ↓
        Task Engine
          ↓
        Data Requirements
          ↓
        Data Engine
          ↓
        ExecutionPlan

    Conversational/general flow:

        Request
          ↓
        QueryService
          ↓
        Query Engine
          ↓
        StructuredQuery
          ↓
        Response layer

    The Orchestrator does not perform model inference.
    """

    def __init__(
        self,
        query_service: QueryService | None = None,
        task_engine: TaskEngine | None = None,
        data_engine: DataEngineClient | None = None,
    ) -> None:

        self.query_service = (
            query_service
            or QueryService()
        )

        self.task_engine = (
            task_engine
            or TaskEngine()
        )

        self.data_engine = data_engine

        self._contexts: dict[
            str,
            ExecutionContext,
        ] = {}

    # ------------------------------------------------------------------
    # Query classification
    # ------------------------------------------------------------------

    @staticmethod
    def _is_task_query(
        structured_query: StructuredQuery,
    ) -> bool:
        """
        Determine whether the StructuredQuery represents
        a satellite-analysis task.

        Query Engine places the requested task inside
        `requested_capabilities`.
        """

        return bool(
            structured_query.requested_capabilities
        )

    # ------------------------------------------------------------------
    # Start Query
    # ------------------------------------------------------------------

    def start_query(
        self,
        request_id: str,
        question: str,
        inputs: list[ObservationInput] | None = None,
        modality: str | None = None,
    ) -> OrchestrationResult:
        """
        Start processing a user query.

        Phase 2 satellite flow:

            RECEIVED
              ↓
            VALIDATING
              ↓
            TASK_IDENTIFIED
              ↓
            REQUIREMENTS_CHECKED
              ↓
            NEEDS_CLARIFICATION
              OR
            WAITING_FOR_DATA

        Conversational/general queries do not enter TaskEngine.
        """

        observations = inputs or []

        # ---------------------------------------------------------
        # 1. Create request lifecycle
        # ---------------------------------------------------------

        self.query_service.create_request(
            request_id
        )

        # ---------------------------------------------------------
        # 2. Create execution context
        # ---------------------------------------------------------

        context = ExecutionContext(
            request_id=request_id
        )

        self._contexts[
            request_id
        ] = context

        # ---------------------------------------------------------
        # 3. Query Understanding
        # ---------------------------------------------------------

        structured_query = (
            self.query_service.process_query(
                request_id=request_id,
                question=question,
                inputs=observations,
                modality=modality,
            )
        )

        context.set_query(
            structured_query
        )

        # ---------------------------------------------------------
        # 4. Check Query Type
        # ---------------------------------------------------------
        #
        # Conversational/general queries such as:
        #
        #   "hello"
        #   "thanks"
        #   "what can you do?"
        #   "what is SAR?"
        #
        # must NOT be sent to TaskEngine.
        #
        # Only satellite-analysis queries continue into
        # task identification and data requirements.
        # ---------------------------------------------------------

        if not self._is_task_query(
            structured_query
        ):
            return OrchestrationResult(
                request_id=request_id,
                status=RequestStatus.TASK_IDENTIFIED,
                structured_query=structured_query,
            )

        # ---------------------------------------------------------
        # 5. Build Data Requirements
        # ---------------------------------------------------------

        try:
            data_requirements = (
                self.task_engine.build_data_requirements(
                    structured_query
                )
            )

        except UnsupportedTaskError:

            self.query_service.update_status(
                request_id,
                RequestStatus.UNSUPPORTED,
            )

            return OrchestrationResult(
                request_id=request_id,
                status=RequestStatus.UNSUPPORTED,
                structured_query=structured_query,
            )

        context.set_data_requirements(
            data_requirements
        )

        self.query_service.update_status(
            request_id,
            RequestStatus.REQUIREMENTS_CHECKED,
        )

        # ---------------------------------------------------------
        # 6. Check whether user information is missing
        # ---------------------------------------------------------

        clarification = (
            self.task_engine.check_requirements(
                structured_query
            )
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

        # ---------------------------------------------------------
        # 7. Wait for Data Engine
        # ---------------------------------------------------------

        self.query_service.update_status(
            request_id,
            RequestStatus.WAITING_FOR_DATA,
        )

        return OrchestrationResult(
            request_id=request_id,
            status=RequestStatus.WAITING_FOR_DATA,
            structured_query=structured_query,
            data_requirements=data_requirements,
        )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def get_context(
        self,
        request_id: str,
    ) -> ExecutionContext:
        """
        Retrieve execution context for a request.
        """

        context = self._contexts.get(
            request_id
        )

        if context is None:
            raise KeyError(
                f"Execution context not found: {request_id}"
            )

        return context

    # ------------------------------------------------------------------
    # Continue With Data Readiness
    # ------------------------------------------------------------------

    def continue_with_data_readiness(
        self,
        request_id: str,
        readiness: DataReadiness,
    ) -> OrchestrationResult:
        """
        Continue orchestration after the Data Engine
        reports whether the required data is ready.

        Phase 2 ends at EXECUTION_PLANNED.
        """

        context = self.get_context(
            request_id
        )

        if (
            context.data_requirements is None
            or context.query is None
        ):
            raise ValueError(
                "Execution context is incomplete."
            )

        context.set_data_readiness(
            readiness
        )

        # ---------------------------------------------------------
        # Data is not ready
        # ---------------------------------------------------------

        if not readiness.ready:

            self.query_service.update_status(
                request_id,
                RequestStatus.NOT_READY,
            )

            return OrchestrationResult(
                request_id=request_id,
                status=RequestStatus.NOT_READY,
                structured_query=context.query,
                data_requirements=(
                    context.data_requirements
                ),
                data_readiness=readiness,
            )

        # ---------------------------------------------------------
        # Data is ready
        # ---------------------------------------------------------

        execution_plan = (
            self.task_engine.build_execution_plan(
                context.query,
                readiness,
            )
        )

        context.set_execution_plan(
            execution_plan
        )

        # ---------------------------------------------------------
        # READY
        # ---------------------------------------------------------

        self.query_service.update_status(
            request_id,
            RequestStatus.READY,
        )

        # ---------------------------------------------------------
        # EXECUTION_PLANNED
        #
        # Phase 2 stops here.
        # ---------------------------------------------------------

        self.query_service.update_status(
            request_id,
            RequestStatus.EXECUTION_PLANNED,
        )

        return OrchestrationResult(
            request_id=request_id,
            status=RequestStatus.EXECUTION_PLANNED,
            structured_query=context.query,
            data_requirements=(
                context.data_requirements
            ),
            data_readiness=readiness,
            execution_plan=execution_plan,
        )