import re

from query_engine.entities.schemas import (
    EntityResult,
    ExtractionResult,
    SlotResult,
)


class EntityExtractor:
    """
    Deterministic entity and slot extractor.

    This is the initial Phase 2 implementation.

    It extracts explicit entities and references from
    the user's query without performing task classification.
    """

    OBJECT_TERMS = {
        "building": "building",
        "buildings": "building",
        "road": "road",
        "roads": "road",
        "vehicle": "vehicle",
        "vehicles": "vehicle",
        "ship": "ship",
        "ships": "ship",
        "water": "water",
        "tree": "tree",
        "trees": "tree",
    }

    INPUT_REFERENCES = {
        "this image": "current_image",
        "the image": "current_image",
        "that image": "referenced_image",
        "these images": "multiple_images",
        "two images": "multiple_images",
        "first image": "first_image",
        "second image": "second_image",
        "previous image": "previous_image",
        "previous images": "previous_images",
    }

    TEMPORAL_TERMS = {
        "before": "before",
        "after": "after",
        "earlier": "earlier",
        "later": "later",
        "over time": "over_time",
        "previous": "previous",
        "current": "current",
    }

    def extract(
        self,
        text: str,
    ) -> ExtractionResult:

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        if not text.strip():
            raise ValueError(
                "text cannot be empty"
            )

        normalized = self._normalize(text)

        entities = []
        slots = []

        self._extract_objects(
            normalized,
            entities,
        )

        self._extract_input_references(
            normalized,
            slots,
        )

        self._extract_temporal_references(
            normalized,
            slots,
        )

        return ExtractionResult(
            entities=tuple(entities),
            slots=tuple(slots),
        )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize(text: str) -> str:

        text = text.strip().lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    # ========================================================
    # OBJECT EXTRACTION
    # ========================================================

    def _extract_objects(
        self,
        text: str,
        entities: list[EntityResult],
    ) -> None:

        for phrase, normalized_value in (
            self.OBJECT_TERMS.items()
        ):

            if self._contains_word(
                text,
                phrase,
            ):
                entity = EntityResult(
                    name="object",
                    value=normalized_value,
                )

                if entity not in entities:
                    entities.append(entity)

    # ========================================================
    # INPUT REFERENCE EXTRACTION
    # ========================================================

    def _extract_input_references(
        self,
        text: str,
        slots: list[SlotResult],
    ) -> None:

        for phrase, value in (
            self.INPUT_REFERENCES.items()
        ):

            if phrase in text:

                slot = SlotResult(
                    name="input_reference",
                    value=value,
                )

                if slot not in slots:
                    slots.append(slot)

    # ========================================================
    # TEMPORAL EXTRACTION
    # ========================================================

    def _extract_temporal_references(
        self,
        text: str,
        slots: list[SlotResult],
    ) -> None:

        for phrase, value in (
            self.TEMPORAL_TERMS.items()
        ):

            if self._contains_phrase(
                text,
                phrase,
            ):

                slot = SlotResult(
                    name="temporal_reference",
                    value=value,
                )

                if slot not in slots:
                    slots.append(slot)

    # ========================================================
    # WORD MATCHING
    # ========================================================

    @staticmethod
    def _contains_word(
        text: str,
        word: str,
    ) -> bool:

        return bool(
            re.search(
                rf"(?<!\w){re.escape(word)}(?!\w)",
                text,
            )
        )

    @staticmethod
    def _contains_phrase(
        text: str,
        phrase: str,
    ) -> bool:

        return phrase in text