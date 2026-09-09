
import os
import tempfile
from pathlib import Path
from typing import BinaryIO

from data_engine import (
    detect_file_type,
    validate_file,
    extract_metadata,
)
from data_engine.exceptions import DataEngineError

from app.core.exceptions import SatQueryException
from app.services.dataset_service import DatasetService
from app.services.metadata_mapper import metadata_to_observation
from app.storage.interfaces.file_storage import FileStorage


class UploadService:
    def __init__(
        self,
        file_storage: FileStorage,
        dataset_service: DatasetService,
    ):
        self.file_storage = file_storage
        self.dataset_service = dataset_service

    def save_file(
        self,
        dataset_id: str,
        file: BinaryIO,
        filename: str,
        content_type: str | None = None,
    ) -> str:
        # Make sure the dataset exists before processing the file.
        self.dataset_service.get_dataset(dataset_id)

        extension = Path(filename).suffix.lower()

        # API-level supported file check.
        if extension not in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
            raise SatQueryException(
                code="UNSUPPORTED_FILE_TYPE",
                message="Unsupported file type.",
            )

        # Copy the uploaded file to a temporary file.
        # The Data Engine works with file paths.
        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            file.seek(0)

            while chunk := file.read(1024 * 1024):
                temp_file.write(chunk)

        try:
            # Data Engine validation and metadata extraction.
            detect_file_type(temp_path)
            validate_file(temp_path)
            metadata = extract_metadata(temp_path)

            size_bytes = temp_path.stat().st_size

        except DataEngineError as exc:
            raise SatQueryException(
                code="INVALID_RASTER",
                message="The uploaded file is not a valid supported raster.",
                details=str(exc),
            ) from exc

        finally:
            # The temporary file is no longer needed.
            if temp_path.exists():
                os.remove(temp_path)

        # Reset the uploaded file before storing it in GridFS.
        file.seek(0)

        # Store the actual file through the Storage Abstraction.
        file_id = self.file_storage.save(
            file=file,
            filename=filename,
            content_type=content_type,
        )

        # Convert Data Engine metadata into the common Observation schema.
        observation = metadata_to_observation(
            metadata=metadata,
            file_id=file_id,
            filename=filename,
            media_type=content_type,
            size_bytes=size_bytes,
        )

        # Store the observation reference inside the dataset.
        self.dataset_service.add_observation(
            dataset_id=dataset_id,
            observation=observation,
        )

        return file_id

