from fastapi import APIRouter, Depends, status

from app.core.request import generate_request_id
from app.schemas.query import QueryAcceptedResponse, QueryRequest
from app.services.query_service import QueryService

router = APIRouter(prefix="/query", tags=["query"])

query_service = QueryService()


def get_query_service() -> QueryService:
    return query_service


@router.post(
    "",
    response_model=QueryAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_query(
    request: QueryRequest,
    query_service: QueryService = Depends(get_query_service),
) -> QueryAcceptedResponse:
    request_id = generate_request_id()

    query_service.create_request(request_id)

    query_service.process_query(
        request_id=request_id,
        question=request.question,
        inputs=request.inputs,
        modality=request.modality,
    )

    return QueryAcceptedResponse(
        request_id=request_id,
        status=query_service.get_status(request_id).value,
    )