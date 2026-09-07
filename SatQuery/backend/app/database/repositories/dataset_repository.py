from typing import Any

from pymongo.collection import Collection


class DatasetRepository:
    """Repository for dataset documents in MongoDB."""

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, document: dict[str, Any]) -> str:
        """Insert a dataset document and return its SatQuery dataset ID."""
        self.collection.insert_one(document)
        return document["dataset_id"]

    def get_by_dataset_id(
        self,
        dataset_id: str,
    ) -> dict[str, Any] | None:
        """Find a dataset using its SatQuery dataset ID."""
        return self.collection.find_one(
            {"dataset_id": dataset_id},
            {"_id": 0},
        )

    def list_datasets(
        self,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return paginated datasets and total count."""
        cursor = (
            self.collection
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        items = list(cursor)
        total = self.collection.count_documents({})

        return items, total

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

        return result.matched_count > 0

    def delete(self, dataset_id: str) -> bool:
        """Delete a dataset document."""
        result = self.collection.delete_one(
            {"dataset_id": dataset_id}
        )

        return result.deleted_count > 0

    def add_file(
        self,
        dataset_id: str,
        file_document: dict[str, Any],
    ) -> bool:
        """Append a file reference to a dataset."""
        result = self.collection.update_one(
            {"dataset_id": dataset_id},
            {
                "$push": {
                    "files": file_document
                },
                "$set": {
                    "processing.updated_at": file_document.get(
                        "updated_at"
                    )
                },
            },
        )

        return result.matched_count > 0

    def remove_file(
        self,
        dataset_id: str,
        file_id: str,
    ) -> bool:
        """Remove a file reference from a dataset."""
        result = self.collection.update_one(
            {"dataset_id": dataset_id},
            {
                "$pull": {
                    "files": {
                        "file_id": file_id
                    }
                },
            },
        )

        return result.matched_count > 0