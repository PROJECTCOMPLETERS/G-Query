from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    dataset_id: str
    gridfs_file_id: str
    status: str