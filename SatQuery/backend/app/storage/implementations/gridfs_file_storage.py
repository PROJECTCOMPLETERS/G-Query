
from bson import ObjectId
from gridfs import GridFS
from typing import BinaryIO

from app.storage.mongodb import database
from app.storage.interfaces.file_storage import FileStorage


class GridFSFileStorage(FileStorage):

    def __init__(self):
        self.gridfs = GridFS(database)

    def save(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str | None = None,
    ) -> str:

        file_id = self.gridfs.put(
    file,
    filename=filename,
    metadata={
        "content_type": content_type,
    },
)

        return str(file_id)

    def get(self, file_id: str):
        try:
            object_id = ObjectId(file_id)
        except Exception:
            return None

        try:
            return self.gridfs.get(object_id)
        except Exception:
            return None

    def delete(self, file_id: str) -> bool:
        try:
            object_id = ObjectId(file_id)
        except Exception:
            return False

        try:
            self.gridfs.delete(object_id)
            return True
        except Exception:
            return False
