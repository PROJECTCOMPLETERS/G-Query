from dataclasses import dataclass
from typing import Any

from app.schemas.data_engine import DataReadiness, DataRequirements
from app.schemas.query import StructuredQuery
from app.schemas.task import ExecutionPlan


@dataclass
class ExecutionContext:
    request_id: str

    query: StructuredQuery | None = None
    data_requirements: DataRequirements | None = None
    data_readiness: DataReadiness | None = None
    execution_plan: ExecutionPlan | None = None

    session_id: str | None = None
    task: str | None = None
    model_requirements: dict[str, Any] | None = None

    def set_query(self, query: StructuredQuery) -> None:
        self.query = query
        self.task = query.intent

    def set_data_requirements(
        self,
        requirements: DataRequirements,
    ) -> None:
        self.data_requirements = requirements
        self.task = requirements.task

    def set_data_readiness(
        self,
        readiness: DataReadiness,
    ) -> None:
        self.data_readiness = readiness

    def set_execution_plan(
        self,
        plan: ExecutionPlan,
    ) -> None:
        self.execution_plan = plan
        self.model_requirements = (
            plan.model_requirements.model_dump()
        )