from typing import Any

from app.database.connection import get_datasets_collection
from app.database.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import DatasetCreate


class DatasetService:
    """Business logic for dataset operations."""

    def __init__(self):
        collection = get_datasets_collection()
        self.repository = DatasetRepository(collection)

    def create_dataset(self, dataset: DatasetCreate) -> str:
        """Create and persist a dataset."""
        return self.repository.create(dataset)

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        """Retrieve a dataset by its SatQuery dataset ID."""
        return self.repository.get_by_dataset_id(dataset_id)

    def update_dataset(
        self,
        dataset_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """Update an existing dataset."""
        return self.repository.update(dataset_id, updates)