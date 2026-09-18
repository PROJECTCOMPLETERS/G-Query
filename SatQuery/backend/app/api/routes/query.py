from fastapi import APIRouter, Depends, status

from app.core.request import generate_request_id
from app.schemas.data_engine import DataReadiness
from app.schemas.query import (
    QueryAcceptedResponse,
    QueryRequest,
)
from app.services.orchestrator import Orchestrator


router = APIRouter(
    prefix="/query",
    tags=["query"],
)


orchestrator = Orchestrator()


def get_orchestrator() -> Orchestrator:
    return orchestrator


# ============================================================
# CREATE QUERY
# ============================================================


@router.post(
    "",
    response_model=QueryAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_query(
    request: QueryRequest,
    orchestration: Orchestrator = Depends(
        get_orchestrator
    ),
) -> QueryAcceptedResponse:

    request_id = generate_request_id()

    result = orchestration.start_query(
        request_id=request_id,
        question=request.question,
        inputs=request.inputs,
        modality=request.modality,
    )
    print(result)
    return QueryAcceptedResponse(
    request_id=request_id,
    status=result.status.value,
    structured_query=result.structured_query,
    execution_plan=result.execution_plan,
)


# ============================================================
# DATA READINESS
# ============================================================


@router.post(
    "/{request_id}/readiness",
    response_model=QueryAcceptedResponse,
    status_code=status.HTTP_200_OK,
)
def update_data_readiness(
    request_id: str,
    readiness: DataReadiness,
    orchestration: Orchestrator = Depends(
        get_orchestrator
    ),
) -> QueryAcceptedResponse:

    result = (
        orchestration.continue_with_data_readiness(
            request_id=request_id,
            readiness=readiness,
        )
    )

    return QueryAcceptedResponse(
    request_id=request_id,
    status=result.status.value,
    structured_query=result.structured_query,
    execution_plan=result.execution_plan,
)