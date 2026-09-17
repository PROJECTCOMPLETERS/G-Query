from app.core.lifecycle import RequestLifecycle, RequestStatus
from app.schemas.query import (
    ObservationInput,
    StructuredQuery,
)

from query_engine.pipeline import QueryEngine


class QueryService:
    """
    Service responsible for request lifecycle management and
    Query Engine integration.

    Query understanding is delegated to the canonical
    query_engine.pipeline.QueryEngine.

    This service owns:
    - request creation
    - request lifecycle
    - StructuredQuery storage
    - status management
    - input normalization
    """

    def __init__(
        self,
        query_engine: QueryEngine | None = None,
    ) -> None:
        self._requests: dict[str, RequestLifecycle] = {}
        self._structured_queries: dict[str, StructuredQuery] = {}

        self._query_engine = (
            query_engine
            or QueryEngine()
        )

    def create_request(
        self,
        request_id: str,
    ) -> RequestLifecycle:
        if not isinstance(request_id, str):
            raise TypeError(
                "request_id must be a string"
            )

        if not request_id.strip():
            raise ValueError(
                "request_id cannot be empty"
            )

        if request_id in self._requests:
            raise ValueError(
                f"Request already exists: {request_id}"
            )

        lifecycle = RequestLifecycle(
            request_id=request_id
        )

        self._requests[request_id] = lifecycle

        return lifecycle

    def process_query(
        self,
        request_id: str,
        question: str,
        inputs: list[ObservationInput] | None = None,
        modality: str | None = None,
    ) -> StructuredQuery:

        lifecycle = self.get_request(
            request_id
        )

        lifecycle.transition_to(
            RequestStatus.VALIDATING
        )

        normalized_inputs = self._normalize_inputs(
            inputs
        )

        result = self._query_engine.process(
            question,
            request_id=request_id,
            inputs=normalized_inputs,
            modality=modality,
        )

        structured_query = result.structured_query

        self._structured_queries[
            request_id
        ] = structured_query

        lifecycle.transition_to(
            RequestStatus.TASK_IDENTIFIED
        )

        return structured_query

    @staticmethod
    def _normalize_inputs(
        inputs: list[ObservationInput] | None,
    ) -> list[ObservationInput]:
        """
        Normalize incoming observation dictionaries/Pydantic
        objects into ObservationInput contracts.

        This keeps the Query Engine independent of the transport
        representation used by FastAPI/tests.
        """

        if inputs is None:
            return []

        normalized: list[ObservationInput] = []

        for item in inputs:
            if isinstance(item, ObservationInput):
                normalized.append(item)
                continue

            if isinstance(item, dict):
                normalized.append(
                    ObservationInput.model_validate(item)
                )
                continue

            raise TypeError(
                "inputs must contain ObservationInput objects "
                "or dictionaries"
            )

        return normalized

    def get_request(
        self,
        request_id: str,
    ) -> RequestLifecycle:

        lifecycle = self._requests.get(
            request_id
        )

        if lifecycle is None:
            raise KeyError(
                f"Request not found: {request_id}"
            )

        return lifecycle

    def get_status(
        self,
        request_id: str,
    ) -> RequestStatus:

        return self.get_request(
            request_id
        ).status

    def get_history(
        self,
        request_id: str,
    ):
        return self.get_request(
            request_id
        ).get_history()

    def get_structured_query(
        self,
        request_id: str,
    ) -> StructuredQuery:

        query = self._structured_queries.get(
            request_id
        )

        if query is None:
            raise KeyError(
                f"Structured query not found: {request_id}"
            )

        return query

    def update_status(
        self,
        request_id: str,
        status: RequestStatus,
    ) -> RequestStatus:

        lifecycle = self.get_request(
            request_id
        )

        return lifecycle.transition_to(
            status
        )

    def delete_request(
        self,
        request_id: str,
    ) -> None:

        self._requests.pop(
            request_id,
            None,
        )

        self._structured_queries.pop(
            request_id,
            None,
        )