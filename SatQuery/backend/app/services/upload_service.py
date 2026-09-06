from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

import app.database.connection as db
from app.core.config import settings
from app.core.exceptions import SatQueryException
from app.services.gridfs_service import GridFSService


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
}

CHUNK_SIZE = 1024 * 1024  # 1 MB


def generate_dataset_id() -> str:
    """Generate a unique SatQuery dataset ID."""
    return f"sat_{uuid4().hex[:8]}"


async def save_uploaded_file(file: UploadFile) -> tuple[str, str, int]:
    """
    Validate and stream an uploaded file directly into GridFS.

    Returns:
        dataset_id, gridfs_file_id, total_size
    """

    if not file.filename:
        raise SatQueryException(
            message="Filename is required.",
            code="MISSING_FILENAME",
            status_code=400,
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise SatQueryException(
            message=(
                "Unsupported file format. "
                "Allowed formats: JPG, PNG and GeoTIFF."
            ),
            code="UNSUPPORTED_FORMAT",
            status_code=415,
        )

    if db.database is None:
        raise RuntimeError("MongoDB is not connected.")

    max_size = settings.max_upload_size_mb * 1024 * 1024

    dataset_id = generate_dataset_id()

    gridfs_service = GridFSService(db.database)

    upload_stream = gridfs_service.create_upload_stream(
        filename=file.filename,
        content_type=file.content_type,
    )

    total_size = 0

    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)

            if not chunk:
                break

            total_size += len(chunk)

            if total_size > max_size:
                upload_stream.abort()

                raise SatQueryException(
                    message=(
                        f"File size exceeds the "
                        f"{settings.max_upload_size_mb} MB limit."
                    ),
                    code="FILE_TOO_LARGE",
                    status_code=413,
                )

            upload_stream.write(chunk)

        upload_stream.close()

    except SatQueryException:
        raise

    except Exception as exc:
        try:
            upload_stream.abort()
        except Exception:
            pass

        raise RuntimeError(
            f"Failed to store file in GridFS: {exc}"
        ) from exc

    return dataset_id, str(upload_stream._id), total_size