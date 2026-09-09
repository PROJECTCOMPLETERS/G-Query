from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_dataset_service
from app.schemas.common.dataset import DatasetCreate
from app.schemas.dataset import DatasetListResponse, DatasetResponse
from app.services.dataset_service import DatasetService
from app.schemas.common.error import ErrorResponse

router = APIRouter()


@router.post(
    "/datasets",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    dataset: DatasetCreate,
    dataset_service: DatasetService = Depends(get_dataset_service),
):
    return dataset_service.create_dataset(dataset)


@router.get(
    "/datasets",
    response_model=DatasetListResponse,
)
def list_datasets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    dataset_service: DatasetService = Depends(get_dataset_service),
):
    return dataset_service.list_datasets(
        page=page,
        page_size=page_size,
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_dataset(
    dataset_id: str,
    dataset_service: DatasetService = Depends(get_dataset_service),
):
    return dataset_service.get_dataset(dataset_id)


@router.delete(
    "/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def delete_dataset(
    dataset_id: str,
    dataset_service: DatasetService = Depends(get_dataset_service),
):
    dataset_service.delete_dataset(dataset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

