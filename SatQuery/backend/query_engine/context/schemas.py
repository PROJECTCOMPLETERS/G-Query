from dataclasses import dataclass, field


@dataclass(frozen=True)
class ObservationContext:
    """
    Represents an observation available in the conversation.
    """

    observation_id: str
    modality: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class ConversationContext:
    """
    State available to the Query Engine while resolving
    references in the current user query.
    """

    observations: tuple[ObservationContext, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class ResolvedReference:
    """
    A resolved reference from the user's query.
    """

    reference: str
    observation_ids: tuple[str, ...]


@dataclass(frozen=True)
class ContextResolutionResult:
    """
    Result of resolving references against conversation context.
    """

    references: tuple[ResolvedReference, ...] = field(
        default_factory=tuple
    )