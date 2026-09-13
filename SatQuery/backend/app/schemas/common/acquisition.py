from datetime import datetime as DateTime

from pydantic import BaseModel


class Acquisition(BaseModel):
    datetime: DateTime | None = None