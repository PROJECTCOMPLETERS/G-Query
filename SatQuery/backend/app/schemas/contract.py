from pydantic import BaseModel, Field


class ContractBase(BaseModel):
    schema_version: str = Field(default="1.0")
    request_id: str