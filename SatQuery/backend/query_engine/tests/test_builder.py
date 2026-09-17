from __future__ import annotations

from typing import Iterable

from app.schemas.query import ObservationInput, StructuredQuery

from query_engine.context.schemas import ContextResolutionResult
from query_engine.entities.schemas import ExtractionResult
from query_engine.router.task_router import TaskRoutingResult


class StructuredQueryBuilder:
    """Builds the canonical StructuredQuery from Query Engine outputs."""

    def build(
        self,
        *,
        question: str,
        intent: str,
        extraction: ExtractionResult | None = None,
        context_resolution: ContextResolutionResult | None = None,
        routing: TaskRoutingResult | None = None,
        inputs: Iterable[ObservationInput] | None = None,
        modality: str | None = None,
        temporal_required: bool = False,
        temporal_information: dict | None = None,
        spatial_required: bool = False,
        spatial_information: dict | None = None,
        missing_information: Iterable[str] | None = None,
    ) -> StructuredQuery:

        self._validate_question(question)
        self._validate_intent(intent)

        return StructuredQuery(
            question=question,
            intent=intent,
            entities=self._build_entities(extraction),
            inputs=self._build_inputs(
                context_resolution=context_resolution,
                explicit_inputs=inputs,
            ),
            modality=modality,
            temporal={
                "required": temporal_required,
                "information": temporal_information,
            },
            spatial={
                "required": spatial_required,
                "information": spatial_information,
            },
            requested_capabilities=self._build_capabilities(routing),
            missing_information=list(missing_information or []),
        )

    @staticmethod
    def _validate_question(question: str) -> None:
        if not isinstance(question, str):
            raise TypeError("question must be a string")
        if not question.strip():
            raise ValueError("question must not be empty")

    @staticmethod
    def _validate_intent(intent: str) -> None:
        if not isinstance(intent, str):
            raise TypeError("intent must be a string")
        if not intent.strip():
            raise ValueError("intent must not be empty")

    @staticmethod
    def _build_entities(
        extraction: ExtractionResult | None,
    ) -> list[str]:
        if extraction is None:
            return []

        return [entity.value for entity in extraction.entities]

    @staticmethod
    def _build_inputs(
        *,
        context_resolution: ContextResolutionResult | None,
        explicit_inputs: Iterable[ObservationInput] | None,
    ) -> list[ObservationInput]:

        result: list[ObservationInput] = []
        seen: set[str] = set()

        for observation in explicit_inputs or []:
            if observation.input_id not in seen:
                result.append(observation)
                seen.add(observation.input_id)

        if context_resolution is not None:
            for reference in context_resolution.references:
                for observation_id in reference.observation_ids:
                    if observation_id not in seen:
                        result.append(
                            ObservationInput(
                                input_id=observation_id,
                                type="image",
                            )
                        )
                        seen.add(observation_id)

        return result

    @staticmethod
    def _build_capabilities(
        routing: TaskRoutingResult | None,
    ) -> list[str]:

        if routing is None or not routing.supported:
            return []

        if routing.task is None:
            return []

        return [routing.task.value]