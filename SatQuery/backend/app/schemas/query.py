from typing import Any

from pydantic import BaseModel, Field

from app.schemas.contract import ContractBase


class ObservationInput(BaseModel):
    input_id: str
    type: str = "image"


class TemporalInfo(BaseModel):
    required: bool = False
    information: dict[str, Any] | None = None


class SpatialInfo(BaseModel):
    required: bool = False
    information: dict[str, Any] | None = None


class StructuredQuery(ContractBase):
    question: str
    intent: str

    entities: list[str] = Field(default_factory=list)

    inputs: list[ObservationInput] = Field(
        default_factory=list
    )

    modality: str | None = None

    temporal: TemporalInfo = Field(
        default_factory=TemporalInfo
    )

    spatial: SpatialInfo = Field(
        default_factory=SpatialInfo
    )

    requested_capabilities: list[str] = Field(
        default_factory=list
    )

    missing_information: list[str] = Field(
        default_factory=list
    )
class ClarificationResponse(ContractBase):
    status: str = "needs_clarification"
    missing_information: list[str] = Field(
        default_factory=list
    )
    question: str
class QueryRequest(BaseModel):
    question: str
    inputs: list[ObservationInput] = Field(default_factory=list)
    modality: str | None = None
class QueryAcceptedResponse(ContractBase):
    request_id: str
    status: str = "received"
    structured_query: StructuredQuery | None = None