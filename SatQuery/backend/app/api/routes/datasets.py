from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.dataset import Dataset, DatasetCreate
from app.services.dataset_service import DatasetService


router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["Datasets"],
)


def get_service() -> DatasetService:
    return DatasetService()


@router.post(
    "",
    response_model=Dataset,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset(payload: DatasetCreate):
    service = get_service()

    return service.create_dataset(payload)


@router.get("")
async def list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = get_service()

    items, total = service.list_datasets(
        page=page,
        page_size=page_size,
    )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get(
    "/{dataset_id}",
    response_model=Dataset,
)
async def get_dataset(dataset_id: str):
    service = get_service()

    dataset = service.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATASET_NOT_FOUND",
                    "message": "Dataset not found",
                    "details": None,
                }
            },
        )

    return dataset


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_dataset(dataset_id: str):
    service = get_service()

    deleted = service.delete_dataset(dataset_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATASET_NOT_FOUND",
                    "message": "Dataset not found",
                    "details": None,
                }
            },
        )

    return None