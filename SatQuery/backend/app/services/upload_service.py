from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import SatQueryException


UPLOAD_DIR = Path("storage/uploads")

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
}

CHUNK_SIZE = 1024 * 1024  # 1 MB


def generate_dataset_id() -> str:
    """Generate a unique dataset ID."""
    return f"sat_{uuid4().hex[:8]}"


async def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """Validate and stream an uploaded file to disk."""

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

    max_size = settings.max_upload_size_mb * 1024 * 1024

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    dataset_id = generate_dataset_id()
    saved_filename = f"{dataset_id}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    total_size = 0

    try:
        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise SatQueryException(
                        message=(
                            f"File size exceeds the "
                            f"{settings.max_upload_size_mb} MB limit."
                        ),
                        code="FILE_TOO_LARGE",
                        status_code=413,
                    )

                destination.write(chunk)

    except SatQueryException:
        if file_path.exists():
            file_path.unlink()
        raise

    return dataset_id, str(file_path)