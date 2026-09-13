import re

from app.schemas.query import (
    ObservationInput,
    StructuredQuery,
)


class QueryEngine:
    """
    Baseline Query Engine.

    Converts a natural-language question into a StructuredQuery.
    This implementation uses deterministic rules so it has no external
    LLM dependency. A future LLM-backed implementation can replace the
    interpretation logic without changing the StructuredQuery contract.
    """

    def build_structured_query(
        self,
        request_id: str,
        question: str,
        inputs: list[ObservationInput] | None = None,
        modality: str | None = None,
    ) -> StructuredQuery:
        normalized = question.strip().lower()

        intent = self._detect_intent(normalized)
        entities = self._extract_entities(normalized)
        capabilities = self._detect_capabilities(normalized)

        return StructuredQuery(
            request_id=request_id,
            question=question,
            intent=intent,
            entities=entities,
            inputs=inputs or [],
            modality=modality,
            requested_capabilities=capabilities,
        )

    def _detect_intent(self, question: str) -> str:
        if any(
            phrase in question
            for phrase in [
                "how many",
                "count",
                "number of",
            ]
        ):
            return "object_counting"

        if any(
            phrase in question
            for phrase in [
                "change",
                "changed",
                "before and after",
                "compare",
                "difference",
            ]
        ):
            return "change_detection"

        if any(
            phrase in question
            for phrase in [
                "what is",
                "describe",
                "identify",
                "explain",
            ]
        ):
            return "image_understanding"

        return "unknown"

    def _extract_entities(self, question: str) -> list[str]:
        known_entities = [
            "building",
            "buildings",
            "road",
            "roads",
            "vehicle",
            "vehicles",
            "water",
            "river",
            "crop",
            "crops",
            "flood",
            "forest",
            "ship",
            "ships",
        ]

        entities = []

        for entity in known_entities:
            if re.search(rf"\b{re.escape(entity)}\b", question):
                normalized_entity = entity.rstrip("s")
                if normalized_entity not in entities:
                    entities.append(normalized_entity)

        return entities

    def _detect_capabilities(self, question: str) -> list[str]:
        capabilities = []

        if any(
            phrase in question
            for phrase in ["how many", "count", "number of"]
        ):
            capabilities.extend(
                ["object_detection", "counting"]
            )

        if any(
            phrase in question
            for phrase in [
                "change",
                "changed",
                "compare",
                "difference",
            ]
        ):
            capabilities.append("change_detection")

        if any(
            phrase in question
            for phrase in [
                "describe",
                "identify",
                "explain",
            ]
        ):
            capabilities.append("image_understanding")

        return capabilities