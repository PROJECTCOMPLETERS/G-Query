
from abc import ABC, abstractmethod
from typing import BinaryIO


class FileStorage(ABC):

    @abstractmethod
    def save(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str | None = None,
    ) -> str:
        pass

    @abstractmethod
    def get(self, file_id: str):
        pass

    @abstractmethod
    def delete(self, file_id: str) -> bool:
        pass

