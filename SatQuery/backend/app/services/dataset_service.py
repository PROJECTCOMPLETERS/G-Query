
from app.core.exceptions import SatQueryException
from app.schemas.common.dataset import DatasetCreate
from app.schemas.common.observation import Observation
from app.schemas.dataset import DatasetListResponse, DatasetResponse
from app.storage.interfaces.dataset_storage import DatasetStorage
from app.storage.interfaces.file_storage import FileStorage


class DatasetService:

    def __init__(
        self,
        storage: DatasetStorage,
        file_storage: FileStorage,
    ):
        self.storage = storage
        self.file_storage = file_storage

    def create_dataset(
        self,
        dataset: DatasetCreate,
    ) -> DatasetResponse:
        return self.storage.create(dataset)

    def get_dataset(
        self,
        dataset_id: str,
    ) -> DatasetResponse:
        dataset = self.storage.get(dataset_id)

        if dataset is None:
            raise SatQueryException(
                code="DATASET_NOT_FOUND",
                message="Dataset was not found.",
            )

        return dataset

    def list_datasets(
        self,
        page: int,
        page_size: int,
    ) -> DatasetListResponse:
        return self.storage.list(
            page=page,
            page_size=page_size,
        )

    def delete_dataset(
    self,
    dataset_id: str,
) -> None:
     dataset = self.get_dataset(dataset_id)

     for observation in dataset.observations:
        self.file_storage.delete(
            observation.file.file_id
        )

     deleted = self.storage.delete(dataset_id)

     if not deleted:
        raise SatQueryException(
            code="DATASET_NOT_FOUND",
            message="Dataset was not found.",
        )

    def add_observation(
        self,
        dataset_id: str,
        observation: Observation,
    ) -> None:
        added = self.storage.add_observation(
            dataset_id=dataset_id,
            observation=observation,
        )

        if not added:
            raise SatQueryException(
                code="DATASET_NOT_FOUND",
                message="Dataset was not found.",
            )

    def remove_observation(
        self,
        dataset_id: str,
        file_id: str,
    ) -> bool:
        removed = self.storage.remove_observation(
            dataset_id=dataset_id,
            file_id=file_id,
        )

        if not removed:
            raise SatQueryException(
                code="FILE_NOT_FOUND",
                message="File was not found.",
            )

        return removed
