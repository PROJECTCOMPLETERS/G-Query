from pydantic import BaseModel


class Source(BaseModel):
    kind: str
    locator: str
    display_name: str
    media_type: str | None = None