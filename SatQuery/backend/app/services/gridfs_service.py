from bson import ObjectId
from gridfs import GridFSBucket
from pymongo.database import Database


class GridFSService:
    """Handles file storage inside MongoDB GridFS."""

    def __init__(self, database: Database):
        self.bucket = GridFSBucket(database)

    def create_upload_stream(
        self,
        filename: str,
        content_type: str | None = None,
    ):
        """Create a GridFS upload stream."""

        metadata = {}

        if content_type:
            metadata["content_type"] = content_type

        return self.bucket.open_upload_stream(
            filename,
            metadata=metadata,
        )

    def get_file(self, file_id: str) -> bytes:
        """Retrieve a file from GridFS."""
        return self.bucket.open_download_stream(
            ObjectId(file_id)
        ).read()

    def delete_file(self, file_id: str) -> None:
        """Delete a file from GridFS."""
        self.bucket.delete(ObjectId(file_id))