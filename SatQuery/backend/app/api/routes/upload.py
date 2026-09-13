
from collections.abc import Iterator

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.api.dependencies import (
    get_file_service,
    get_upload_service,
)
from app.schemas.common.error import ErrorResponse
from app.schemas.upload import UploadResponse
from app.services.file_service import FileService
from app.services.upload_service import UploadService


router = APIRouter()


@router.post(
    "/datasets/{dataset_id}/files",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Upload a dataset file",
    description=(
        "Upload a JPG, JPEG, PNG, TIF, or TIFF file "
        "to a dataset."
    ),
)
def upload_file(
    dataset_id: str,
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(
        get_upload_service
    ),
):
    file_id = upload_service.save_file(
        dataset_id=dataset_id,
        file=file.file,
        filename=file.filename,
        content_type=file.content_type,
    )

    return UploadResponse(
        dataset_id=dataset_id,
        file_id=file_id,
        status="uploaded",
    )


def stream_gridfs_file(
    stored_file,
    chunk_size: int = 1024 * 1024,
) -> Iterator[bytes]:
    while True:
        chunk = stored_file.read(chunk_size)

        if not chunk:
            break

        yield chunk


@router.get(
    "/datasets/{dataset_id}/files/{file_id}",
    responses={
        404: {"model": ErrorResponse},
    },
    summary="Retrieve a dataset file",
    description="Stream a stored dataset file.",
)
def get_file(
    dataset_id: str,
    file_id: str,
    file_service: FileService = Depends(
        get_file_service
    ),
):
    stored_file = file_service.get_file(
        dataset_id=dataset_id,
        file_id=file_id,
    )

    content_type = (
    (stored_file.metadata or {}).get("content_type")
    or "application/octet-stream"
)

    return StreamingResponse(
        stream_gridfs_file(stored_file),
        media_type=content_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{stored_file.filename}"'
            )
        },
    )


@router.delete(
    "/datasets/{dataset_id}/files/{file_id}",
    status_code=204,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Delete a dataset file",
    description=(
        "Delete a file from the dataset and "
        "remove its observation reference."
    ),
)
def delete_file(
    dataset_id: str,
    file_id: str,
    file_service: FileService = Depends(
        get_file_service
    ),
):
    file_service.delete_file(
        dataset_id=dataset_id,
        file_id=file_id,
    )
