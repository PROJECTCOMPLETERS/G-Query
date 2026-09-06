from fastapi import APIRouter, File, UploadFile

from app.schemas.upload import UploadResponse
from app.services.upload_service import save_uploaded_file


router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    dataset_id, _ = await save_uploaded_file(file)

    return UploadResponse(
        success=True,
        dataset_id=dataset_id,
        status="uploaded",
    )