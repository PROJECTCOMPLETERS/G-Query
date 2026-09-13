from app.core.lifecycle import RequestLifecycle, RequestStatus
from app.services.query_engine import QueryEngine
from app.schemas.query import (
    ObservationInput,
    StructuredQuery,
)


class QueryService:
    def __init__(self) -> None:
        self._requests: dict[str, RequestLifecycle] = {}
        self._structured_queries: dict[str, StructuredQuery] = {}
        self._query_engine = QueryEngine()

    def create_request(self, request_id: str) -> RequestLifecycle:
        if request_id in self._requests:
            raise ValueError(f"Request already exists: {request_id}")

        lifecycle = RequestLifecycle(request_id=request_id)
        self._requests[request_id] = lifecycle

        return lifecycle

    def process_query(
        self,
        request_id: str,
        question: str,
        inputs: list[ObservationInput] | None = None,
        modality: str | None = None,
    ) -> StructuredQuery:
        lifecycle = self.get_request(request_id)

        lifecycle.transition_to(RequestStatus.VALIDATING)

        structured_query = self._query_engine.build_structured_query(
            request_id=request_id,
            question=question,
            inputs=inputs,
            modality=modality,
        )

        self._structured_queries[request_id] = structured_query

        lifecycle.transition_to(RequestStatus.TASK_IDENTIFIED)

        return structured_query

    def get_request(self, request_id: str) -> RequestLifecycle:
        lifecycle = self._requests.get(request_id)

        if lifecycle is None:
            raise KeyError(f"Request not found: {request_id}")

        return lifecycle

    def get_status(self, request_id: str) -> RequestStatus:
        return self.get_request(request_id).status

    def get_history(self, request_id: str):
        return self.get_request(request_id).get_history()

    def get_structured_query(self, request_id: str) -> StructuredQuery:
        query = self._structured_queries.get(request_id)

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
        lifecycle = self.get_request(request_id)
        return lifecycle.transition_to(status)

    def delete_request(self, request_id: str) -> None:
        self._requests.pop(request_id, None)
        self._structured_queries.pop(request_id, None)