from typing import Any

from pymongo.collection import Collection

from app.schemas.dataset import DatasetCreate


class DatasetRepository:
    """Repository for dataset documents in MongoDB."""

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, dataset: DatasetCreate) -> str:
        """Create a dataset document and return its MongoDB document ID."""
        result = self.collection.insert_one(dataset.model_dump())
        return str(result.inserted_id)

    def get_by_dataset_id(self, dataset_id: str) -> dict[str, Any] | None:
        """Find a dataset using its SatQuery dataset ID."""
        return self.collection.find_one(
            {"dataset_id": dataset_id},
            {"_id": 0},
        )

    def update(
        self,
        dataset_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """Update fields of an existing dataset."""
        result = self.collection.update_one(
            {"dataset_id": dataset_id},
            {"$set": updates},
        )

        return result.modified_count > 0