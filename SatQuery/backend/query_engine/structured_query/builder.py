from __future__ import annotations

from typing import Iterable

from app.schemas.query import ObservationInput, StructuredQuery
from query_engine.context.schemas import ContextResolutionResult
from query_engine.entities.schemas import ExtractionResult
from query_engine.router.task_router import TaskRoutingResult


class StructuredQueryBuilder:
    """
    Builds the canonical StructuredQuery contract from the outputs
    of the Query Engine pipeline.

    Request ID is supplied by the request lifecycle/API layer.
    The Query Engine does not generate request IDs.
    """

    def build(
        self,
        *,
        request_id: str,
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
        """
        Build a StructuredQuery.

        Parameters
        ----------
        request_id:
            Unique request identifier supplied by the API/request
            lifecycle layer.

        question:
            Original user question.

        intent:
            Classified intent.

        extraction:
            Entity and slot extraction result.

        context_resolution:
            Resolved references to observations from conversation context.

        routing:
            Task routing result.

        inputs:
            Explicit observation inputs supplied with the request.

        modality:
            Requested or known modality.

        temporal_required:
            Whether temporal information is required.

        temporal_information:
            Extracted/resolved temporal information.

        spatial_required:
            Whether spatial information is required.

        spatial_information:
            Extracted/resolved spatial information.

        missing_information:
            Information still required to execute the query.
        """

        if not isinstance(request_id, str):
            raise TypeError("request_id must be a string")

        if not request_id.strip():
            raise ValueError("request_id cannot be empty")

        if not isinstance(question, str):
            raise TypeError("question must be a string")

        if not question.strip():
            raise ValueError("question cannot be empty")

        if not isinstance(intent, str):
            raise TypeError("intent must be a string")

        if not intent.strip():
            raise ValueError("intent cannot be empty")

        entities = self._build_entities(extraction)

        resolved_inputs = self._build_inputs(
            inputs=inputs,
            context_resolution=context_resolution,
        )

        requested_capabilities = self._build_capabilities(routing)

        missing = self._build_missing_information(
            missing_information
        )

        return StructuredQuery(
            request_id=request_id,
            question=question,
            intent=intent,
            entities=entities,
            inputs=resolved_inputs,
            modality=modality,
            temporal={
                "required": temporal_required,
                "information": temporal_information,
            },
            spatial={
                "required": spatial_required,
                "information": spatial_information,
            },
            requested_capabilities=requested_capabilities,
            missing_information=missing,
        )

    @staticmethod
    def _build_entities(
        extraction: ExtractionResult | None,
    ) -> list[str]:
        """
        Convert extracted entities into the canonical list of
        entity values expected by StructuredQuery.
        """

        if extraction is None:
            return []

        return [
            entity.value
            for entity in extraction.entities
        ]

    @staticmethod
    def _build_inputs(
        *,
        inputs: Iterable[ObservationInput] | None,
        context_resolution: ContextResolutionResult | None,
    ) -> list[ObservationInput]:
        """
        Merge explicitly supplied inputs with observation IDs resolved
        from conversation context.

        Duplicate observation IDs are removed while preserving order.
        """

        resolved_inputs: list[ObservationInput] = []
        seen_ids: set[str] = set()

        if inputs is not None:
            for observation in inputs:
                if not isinstance(observation, ObservationInput):
                    raise TypeError(
                        "inputs must contain ObservationInput objects"
                    )

                if observation.input_id not in seen_ids:
                    resolved_inputs.append(observation)
                    seen_ids.add(observation.input_id)

        if context_resolution is not None:
            for reference in context_resolution.references:
                for observation_id in reference.observation_ids:
                    if observation_id in seen_ids:
                        continue

                    resolved_inputs.append(
                        ObservationInput(
                            input_id=observation_id,
                            type="image",
                        )
                    )

                    seen_ids.add(observation_id)

        return resolved_inputs

    @staticmethod
    def _build_capabilities(
        routing: TaskRoutingResult | None,
    ) -> list[str]:
        """
        Convert a supported task routing result into the
        requested_capabilities field.
        """

        if routing is None:
            return []

        if not routing.supported:
            return []

        if routing.task is None:
            return []

        return [routing.task.value]

    @staticmethod
    def _build_missing_information(
        missing_information: Iterable[str] | None,
    ) -> list[str]:
        """
        Normalize missing information while preserving order
        and removing duplicates.
        """

        if missing_information is None:
            return []

        result: list[str] = []
        seen: set[str] = set()

        for item in missing_information:
            if not isinstance(item, str):
                raise TypeError(
                    "missing_information must contain strings"
                )

            value = item.strip()

            if not value:
                continue

            if value in seen:
                continue

            result.append(value)
            seen.add(value)

        return result