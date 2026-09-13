from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_data_engine_client
from app.core.request import generate_request_id
from app.schemas.query import QueryAcceptedResponse, QueryRequest
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/query", tags=["query"])


def get_orchestrator() -> Orchestrator:
    data_engine = get_data_engine_client()

    return Orchestrator(
        data_engine=data_engine,
    )


@router.post(
    "",
    response_model=QueryAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_query(
    request: QueryRequest,
    orchestration: Orchestrator = Depends(get_orchestrator),
) -> QueryAcceptedResponse:
    request_id = generate_request_id()

    result = orchestration.start_query(
        request_id=request_id,
        question=request.question,
        inputs=request.inputs,
        modality=request.modality,
    )

    return QueryAcceptedResponse(
        request_id=request_id,
        status=result.status.value,
    )