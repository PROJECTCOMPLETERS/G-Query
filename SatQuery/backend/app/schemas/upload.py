from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    dataset_id: str
    status: str