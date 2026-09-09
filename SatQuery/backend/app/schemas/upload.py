from pydantic import BaseModel


class UploadResponse(BaseModel):
    dataset_id: str
    file_id: str
    status: str