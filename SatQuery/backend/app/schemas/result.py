from typing import Any

from pydantic import BaseModel, Field

from app.schemas.contract import ContractBase


class AnalysisResult(ContractBase):
    status: str
    task: str

    result: dict[str, Any] = Field(
        default_factory=dict
    )

    spatial_output: dict[str, Any] | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )