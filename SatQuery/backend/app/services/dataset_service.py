from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.database.connection import get_datasets_collection
from app.database.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import DatasetCreate


class DatasetService:
    """Business logic for dataset operations."""

    def __init__(self):
        collection = get_datasets_collection()
        self.repository = DatasetRepository(collection)

    def create_dataset(self, data: DatasetCreate) -> dict[str, Any]:
        """Create a new dataset record."""
        now = datetime.now(timezone.utc)

        dataset_id = f"ds_{uuid4().hex[:8]}"

        document = {
            "dataset_id": dataset_id,
            "name": data.name,
            "dataset_type": data.dataset_type,
            "observations": [],
            "files": [],
            "processing": {
                "status": "uploading",
                "created_at": now,
                "updated_at": now,
            },
            "created_at": now,
            "updated_at": now,
        }

        self.repository.create(document)

        return document

    def get_dataset(
        self,
        dataset_id: str,
    ) -> dict[str, Any] | None:
        return self.repository.get_by_dataset_id(dataset_id)

    def list_datasets(
        self,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        skip = (page - 1) * page_size

        return self.repository.list_datasets(
            skip=skip,
            limit=page_size,
        )

    def delete_dataset(
        self,
        dataset_id: str,
    ) -> bool:
        return self.repository.delete(dataset_id)