import re

from query_engine.context.schemas import (
    ContextResolutionResult,
    ConversationContext,
    ResolvedReference,
)


class ContextResolver:
    """
    Resolves natural-language references such as:

        this image
        that image
        previous image
        first image
        second image
        these two images

    against the observations available in the conversation.
    """

    def resolve(
        self,
        text: str,
        context: ConversationContext,
    ) -> ContextResolutionResult:

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        if not text.strip():
            raise ValueError(
                "text cannot be empty"
            )

        if not isinstance(
            context,
            ConversationContext,
        ):
            raise TypeError(
                "context must be ConversationContext"
            )

        normalized = self._normalize(text)

        references = []

        self._resolve_current_image(
            normalized,
            context,
            references,
        )

        self._resolve_previous_image(
            normalized,
            context,
            references,
        )

        self._resolve_first_image(
            normalized,
            context,
            references,
        )

        self._resolve_second_image(
            normalized,
            context,
            references,
        )

        self._resolve_multiple_images(
            normalized,
            context,
            references,
        )

        return ContextResolutionResult(
            references=tuple(references)
        )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize(text: str) -> str:

        text = text.strip().lower()

        return re.sub(
            r"\s+",
            " ",
            text,
        )

    # ========================================================
    # CURRENT IMAGE
    # ========================================================

    def _resolve_current_image(
        self,
        text: str,
        context: ConversationContext,
        references: list[ResolvedReference],
    ) -> None:

        phrases = {
            "this image",
            "the image",
            "current image",
        }

        if not any(
            phrase in text
            for phrase in phrases
        ):
            return

        if not context.observations:
            return

        observation = context.observations[-1]

        references.append(
            ResolvedReference(
                reference="current_image",
                observation_ids=(
                    observation.observation_id,
                ),
            )
        )

    # ========================================================
    # PREVIOUS IMAGE
    # ========================================================

    def _resolve_previous_image(
        self,
        text: str,
        context: ConversationContext,
        references: list[ResolvedReference],
    ) -> None:

        phrases = {
            "previous image",
            "previous images",
            "last image",
        }

        if not any(
            phrase in text
            for phrase in phrases
        ):
            return

        if len(context.observations) < 2:
            return

        observation = context.observations[-2]

        references.append(
            ResolvedReference(
                reference="previous_image",
                observation_ids=(
                    observation.observation_id,
                ),
            )
        )

    # ========================================================
    # FIRST IMAGE
    # ========================================================

    def _resolve_first_image(
        self,
        text: str,
        context: ConversationContext,
        references: list[ResolvedReference],
    ) -> None:

        if "first image" not in text:
            return

        if not context.observations:
            return

        observation = context.observations[0]

        references.append(
            ResolvedReference(
                reference="first_image",
                observation_ids=(
                    observation.observation_id,
                ),
            )
        )

    # ========================================================
    # SECOND IMAGE
    # ========================================================

    def _resolve_second_image(
        self,
        text: str,
        context: ConversationContext,
        references: list[ResolvedReference],
    ) -> None:

        if "second image" not in text:
            return

        if len(context.observations) < 2:
            return

        observation = context.observations[1]

        references.append(
            ResolvedReference(
                reference="second_image",
                observation_ids=(
                    observation.observation_id,
                ),
            )
        )

    # ========================================================
    # MULTIPLE IMAGES
    # ========================================================

    def _resolve_multiple_images(
        self,
        text: str,
        context: ConversationContext,
        references: list[ResolvedReference],
    ) -> None:

        phrases = {
            "these images",
            "these two images",
            "two images",
            "both images",
        }

        if not any(
            phrase in text
            for phrase in phrases
        ):
            return

        if len(context.observations) < 2:
            return

        observations = context.observations[-2:]

        references.append(
            ResolvedReference(
                reference="multiple_images",
                observation_ids=tuple(
                    observation.observation_id
                    for observation in observations
                ),
            )
        )