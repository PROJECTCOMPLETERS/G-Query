from typing import Any

from pydantic import BaseModel, Field


class File(BaseModel):
    file_id: str
    filename: str
    media_type: str | None = None
    input_kind: str
    driver: str | None = None
    size_bytes: int | None = None
    tags: dict[str, Any] = Field(default_factory=dict)