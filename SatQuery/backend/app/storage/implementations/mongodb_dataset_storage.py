
from bson import ObjectId

from app.core.exceptions import SatQueryException
from app.schemas.common.dataset import DatasetCreate, DatasetType
from app.schemas.common.observation import Observation
from app.schemas.common.processing import Processing, ProcessingStatus
from app.schemas.dataset import DatasetListResponse, DatasetResponse
from app.storage.interfaces.dataset_storage import DatasetStorage
from app.storage.mongodb import database


class MongoDBDatasetStorage(DatasetStorage):

    def create(
        self,
        dataset: DatasetCreate,
    ) -> DatasetResponse:

        document = {
            "name": dataset.name,
            "dataset_type": dataset.dataset_type.value,
            "processing": {
                "status": ProcessingStatus.UPLOADING.value,
            },
            "observations": [],
        }

        result = database.datasets.insert_one(document)

        return DatasetResponse(
            dataset_id=str(result.inserted_id),
            name=dataset.name,
            dataset_type=dataset.dataset_type,
            processing=Processing(
                status=ProcessingStatus.UPLOADING,
            ),
            observations=[],
        )

    def get(
        self,
        dataset_id: str,
    ) -> DatasetResponse | None:

        try:
            object_id = ObjectId(dataset_id)
        except Exception:
            raise SatQueryException(
                code="INVALID_DATASET_ID",
                message="Invalid dataset ID.",
            )

        document = database.datasets.find_one(
            {"_id": object_id}
        )

        if document is None:
            return None

        observations = [
            Observation(**observation)
            for observation in document.get(
                "observations",
                [],
            )
        ]

        return DatasetResponse(
            dataset_id=str(document["_id"]),
            name=document["name"],
            dataset_type=DatasetType(
                document["dataset_type"]
            ),
            processing=Processing(
                status=ProcessingStatus(
                    document["processing"]["status"]
                )
            ),
            observations=observations,
        )

    def list(
        self,
        page: int,
        page_size: int,
    ) -> DatasetListResponse:

        total = database.datasets.count_documents({})

        cursor = (
            database.datasets
            .find({})
            .skip((page - 1) * page_size)
            .limit(page_size)
        )

        items = []

        for document in cursor:
            observations = [
                Observation(**observation)
                for observation in document.get(
                    "observations",
                    [],
                )
            ]

            items.append(
                DatasetResponse(
                    dataset_id=str(document["_id"]),
                    name=document["name"],
                    dataset_type=DatasetType(
                        document["dataset_type"]
                    ),
                    processing=Processing(
                        status=ProcessingStatus(
                            document["processing"]["status"]
                        )
                    ),
                    observations=observations,
                )
            )

        return DatasetListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def delete(
        self,
        dataset_id: str,
    ) -> bool:

        try:
            object_id = ObjectId(dataset_id)
        except Exception:
            raise SatQueryException(
                code="INVALID_DATASET_ID",
                message="Invalid dataset ID.",
            )

        result = database.datasets.delete_one(
            {"_id": object_id}
        )

        return result.deleted_count == 1

    def add_observation(
        self,
        dataset_id: str,
        observation: Observation,
    ) -> bool:

        try:
            object_id = ObjectId(dataset_id)
        except Exception:
            raise SatQueryException(
                code="INVALID_DATASET_ID",
                message="Invalid dataset ID.",
            )

        result = database.datasets.update_one(
            {"_id": object_id},
            {
                "$push": {
                    "observations": observation.model_dump(),
                }
            },
        )

        return result.modified_count == 1

    def remove_observation(
    self,
    dataset_id: str,
    file_id: str,
) -> bool:
     try:
        object_id = ObjectId(dataset_id)
     except Exception:
        raise SatQueryException(
            code="INVALID_DATASET_ID",
            message="Invalid dataset ID.",
        )

     result = database.datasets.update_one(
        {"_id": object_id},
        {
            "$pull": {
                "observations": {
                    "file.file_id": file_id,
                }
            }
        },
    )

     return result.modified_count == 1
