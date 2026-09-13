
from abc import ABC, abstractmethod

from app.schemas.common.dataset import DatasetCreate
from app.schemas.common.observation import Observation
from app.schemas.dataset import DatasetListResponse, DatasetResponse


class DatasetStorage(ABC):

    @abstractmethod
    def create(
        self,
        dataset: DatasetCreate,
    ) -> DatasetResponse:
        pass

    @abstractmethod
    def get(
        self,
        dataset_id: str,
    ) -> DatasetResponse | None:
        pass

    @abstractmethod
    def list(
        self,
        page: int,
        page_size: int,
    ) -> DatasetListResponse:
        pass

    @abstractmethod
    def delete(
        self,
        dataset_id: str,
    ) -> bool:
        pass

    @abstractmethod
    def add_observation(
        self,
        dataset_id: str,
        observation: Observation,
    ) -> bool:
        pass

    @abstractmethod
    def remove_observation(
        self,
        dataset_id: str,
        file_id: str,
    ) -> bool:
        pass
