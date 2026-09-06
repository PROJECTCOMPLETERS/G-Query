from fastapi import APIRouter, File, UploadFile

from app.schemas.dataset import DatasetCreate
from app.schemas.upload import UploadResponse
from app.services.dataset_service import DatasetService
from app.services.upload_service import save_uploaded_file


router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    dataset_id, gridfs_file_id, size = await save_uploaded_file(file)

    dataset = DatasetCreate(
        dataset_id=dataset_id,
        filename=file.filename,
        file_type=file.content_type or "unknown",
        size=size,
        status="uploaded",
        gridfs_file_id=gridfs_file_id,
    )

    DatasetService().create_dataset(dataset)

    return UploadResponse(
        success=True,
        dataset_id=dataset_id,
        gridfs_file_id=gridfs_file_id,
        status="uploaded",
    )