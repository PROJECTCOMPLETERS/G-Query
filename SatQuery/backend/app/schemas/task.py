from typing import Any

from pydantic import BaseModel, Field

from app.schemas.contract import ContractBase


class ModelRequirements(BaseModel):
    capabilities: list[str] = Field(default_factory=list)


class ExecutionPlan(ContractBase):
    task: str

    input_observations: list[str] = Field(
        default_factory=list
    )

    required_modalities: list[str] = Field(
        default_factory=list
    )

    temporal_requirements: dict[str, Any] = Field(
        default_factory=dict
    )

    spatial_requirements: dict[str, Any] = Field(
        default_factory=dict
    )

    preprocessing: list[str] = Field(
        default_factory=list
    )

    model_requirements: ModelRequirements = Field(
        default_factory=ModelRequirements
    )

    expected_output: dict[str, Any] = Field(
        default_factory=dict
    )