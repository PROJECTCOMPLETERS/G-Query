from dataclasses import dataclass

from app.core.lifecycle import RequestStatus
from app.schemas.data_engine import (
    DataRequirements,
    InputRequirements,
    ModalityRequirements,
    QualityRequirements,
    SpatialRequirements,
    TemporalRequirements,
)
from app.schemas.query import StructuredQuery
from app.schemas.query import ClarificationResponse
from app.schemas.data_engine import DataReadiness
from app.schemas.task import ExecutionPlan, ModelRequirements


@dataclass(frozen=True)
class TaskDefinition:
    task: str
    required_capabilities: list[str]
    min_observations: int
    allowed_modalities: list[str]
    sufficient_resolution_required: bool = False
    temporal_required: bool = False
    spatial_required: bool = False


TASK_DEFINITIONS: dict[str, TaskDefinition] = {
    "object_counting": TaskDefinition(
        task="object_counting",
        required_capabilities=[
            "object_detection",
            "counting",
        ],
        min_observations=1,
        allowed_modalities=["optical", "sar"],
        sufficient_resolution_required=True,
    ),
    "change_detection": TaskDefinition(
        task="change_detection",
        required_capabilities=["change_detection"],
        min_observations=2,
        allowed_modalities=["optical", "sar"],
        temporal_required=True,
        spatial_required=True,
    ),
    "image_understanding": TaskDefinition(
        task="image_understanding",
        required_capabilities=["image_understanding"],
        min_observations=1,
        allowed_modalities=["optical", "sar"],
    ),
}


class UnsupportedTaskError(Exception):
    pass


class InvalidTaskError(Exception):
    pass


class TaskEngine:
    """
    Determines what needs to happen for a StructuredQuery.

    The Task Engine does not execute ML and does not select a
    concrete model implementation.
    """

    def identify_task(self, query: StructuredQuery) -> TaskDefinition:
        if not query.intent:
            raise InvalidTaskError("Structured query has no intent.")

        task_definition = TASK_DEFINITIONS.get(query.intent)

        if task_definition is None:
            raise UnsupportedTaskError(
                f"Unsupported task intent: {query.intent}"
            )

        return task_definition

    def build_data_requirements(
        self,
        query: StructuredQuery,
    ) -> DataRequirements:
        task_definition = self.identify_task(query)

        allowed_modalities = task_definition.allowed_modalities

        # If the Query Engine already identified a modality,
        # preserve it in the requirements.
        if query.modality:
            allowed_modalities = [query.modality]

        return DataRequirements(
            request_id=query.request_id,
            task=task_definition.task,
            inputs=InputRequirements(
                min_observations=task_definition.min_observations,
                type="image",
            ),
            modality=ModalityRequirements(
                required=bool(query.modality),
                allowed=allowed_modalities,
            ),
            temporal=TemporalRequirements(
                required=task_definition.temporal_required,
                information=query.temporal.information,
            ),
            spatial=SpatialRequirements(
                required=task_definition.spatial_required,
                information=query.spatial.information,
            ),
            quality=QualityRequirements(
                valid_data=True,
                sufficient_resolution=(
                    task_definition.sufficient_resolution_required
                ),
            ),
            task_specific={
                "entities": query.entities,
                "requested_capabilities": (
                    task_definition.required_capabilities
                ),
            },
        )
    def check_requirements(
        self,
        query: StructuredQuery,
    ) -> ClarificationResponse | None:
        task_definition = self.identify_task(query)

        missing_information: list[str] = []

        if len(query.inputs) < task_definition.min_observations:
            missing_information.append(
                f"At least {task_definition.min_observations} "
                f"observation(s) required."
            )

        if task_definition.temporal_required:
            if query.temporal.information is None:
                missing_information.append(
                "Temporal information is required."
                )

        if task_definition.spatial_required:
            if query.spatial.information is None:
                missing_information.append(
                "Spatial information is required."
            )

        if missing_information:
            return ClarificationResponse(
                request_id=query.request_id,
                missing_information=missing_information,
                question=self._build_clarification_question(
                    missing_information
                ),
            )

        return None

    def _build_clarification_question(
        self,
        missing_information: list[str],
    ) -> str:
        if len(missing_information) == 1:
            return (
                f"Please provide the missing information: "
                f"{missing_information[0]}"
            )

        return (
            "Please provide the following missing information: "
            + "; ".join(missing_information)
        )
    def build_execution_plan(
        self,
        query: StructuredQuery,
        readiness: DataReadiness,
    ) -> ExecutionPlan:
        if not readiness.ready:
            raise ValueError(
                "Cannot build execution plan when data is not ready."
            )

        task_definition = self.identify_task(query)

        return ExecutionPlan(
            request_id=query.request_id,
            task=task_definition.task,
            input_observations=readiness.available_observations,
           required_modalities=([query.modality]if query.modality else task_definition.allowed_modalities),
            temporal_requirements={
                "required": task_definition.temporal_required,
                "information": query.temporal.information,
            },
            spatial_requirements={
                "required": task_definition.spatial_required,
                "information": query.spatial.information,
            },
            preprocessing=[],
            model_requirements=ModelRequirements(
                capabilities=task_definition.required_capabilities
            ),
            expected_output={
                "task": task_definition.task,
                "spatial_output": task_definition.spatial_required,
            },
        )