
from app.core.exceptions import SatQueryException
from app.services.dataset_service import DatasetService
from app.storage.interfaces.file_storage import FileStorage


class FileService:
    def __init__(
        self,
        storage: FileStorage,
        dataset_service: DatasetService,
    ):
        self.storage = storage
        self.dataset_service = dataset_service

    def get_file(
        self,
        dataset_id: str,
        file_id: str,
    ):
        # Make sure the dataset exists.
        dataset = self.dataset_service.get_dataset(dataset_id)

        # Make sure the file belongs to this dataset.
        file_belongs_to_dataset = any(
            observation.file.file_id == file_id
            for observation in dataset.observations
        )

        if not file_belongs_to_dataset:
            raise SatQueryException(
                code="FILE_NOT_FOUND",
                message="File was not found.",
            )

        # Retrieve the actual file from storage.
        stored_file = self.storage.get(file_id)

        if stored_file is None:
            raise SatQueryException(
                code="FILE_NOT_FOUND",
                message="File was not found.",
            )

        return stored_file

   
    def delete_file(
    self,
    dataset_id: str,
    file_id: str,
) -> None:
    # Make sure the dataset exists.
     dataset = self.dataset_service.get_dataset(dataset_id)

    # Make sure the file belongs to this dataset.
     file_belongs_to_dataset = any(
        observation.file.file_id == file_id
        for observation in dataset.observations
    )

     if not file_belongs_to_dataset:
        raise SatQueryException(
            code="FILE_NOT_FOUND",
            message="File was not found.",
        )

    # Delete the actual file from GridFS.
     deleted = self.storage.delete(file_id)

     

     if not deleted:
        raise SatQueryException(
            code="FILE_NOT_FOUND",
            message="File was not found.",
        )

    # Remove the corresponding observation from MongoDB.
     removed = self.dataset_service.remove_observation(
        dataset_id=dataset_id,
        file_id=file_id,
    )

     

     if not removed:
        raise SatQueryException(
            code="FILE_NOT_FOUND",
            message="File was not found.",
        )
