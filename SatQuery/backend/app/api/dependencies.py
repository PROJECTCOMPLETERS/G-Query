
from fastapi import Depends

from app.services.dataset_service import DatasetService
from app.services.file_service import FileService
from app.services.upload_service import UploadService
from app.storage.implementations.gridfs_file_storage import (
    GridFSFileStorage,
)


def get_dataset_service() -> DatasetService:
    from app.storage.implementations.mongodb_dataset_storage import (
        MongoDBDatasetStorage,
    )

    storage = MongoDBDatasetStorage()
    file_storage = GridFSFileStorage()

    return DatasetService(
        storage=storage,
        file_storage=file_storage,
    )


def get_upload_service(
    dataset_service: DatasetService = Depends(
        get_dataset_service
    ),
) -> UploadService:
    file_storage = GridFSFileStorage()

    return UploadService(
        file_storage=file_storage,
        dataset_service=dataset_service,
    )


def get_file_service(
    dataset_service: DatasetService = Depends(
        get_dataset_service
    ),
) -> FileService:
    file_storage = GridFSFileStorage()

    return FileService(
        storage=file_storage,
        dataset_service=dataset_service,
    )
