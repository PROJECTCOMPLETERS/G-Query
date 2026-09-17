from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntityResult:
    """
    Represents an extracted entity from a user query.
    """

    name: str
    value: str


@dataclass(frozen=True)
class SlotResult:
    """
    Represents a task-specific slot extracted from
    a user query.
    """

    name: str
    value: str


@dataclass(frozen=True)
class ExtractionResult:
    """
    Result produced by the entity/slot extractor.
    """

    entities: tuple[EntityResult, ...] = field(
        default_factory=tuple
    )

    slots: tuple[SlotResult, ...] = field(
        default_factory=tuple
    )