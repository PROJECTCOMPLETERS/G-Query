from __future__ import annotations

import pytest

from app.schemas.query import ObservationInput

from query_engine.context.schemas import (
    ConversationContext,
    ObservationContext,
)

from query_engine.intent.labels import Intent
from query_engine.pipeline import QueryEngine


@pytest.fixture
def engine() -> QueryEngine:
    return QueryEngine()


def test_query_engine_initializes(
    engine: QueryEngine,
) -> None:
    assert engine is not None
    assert engine.embedding_encoder is not None
    assert engine.intent_classifier is not None
    assert engine.entity_extractor is not None
    assert engine.context_resolver is not None
    assert engine.task_router is not None
    assert engine.structured_query_builder is not None


def test_object_counting(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "how many buildings are there?",
        request_id="test-counting-001",
    )

    assert (
        result.classification.intent
        == Intent.OBJECT_COUNTING
    )

    assert (
        result.routing.task is not None
    )

    assert result.routing.supported is True

    assert (
        result.structured_query.request_id
        == "test-counting-001"
    )

    assert (
        result.structured_query.intent
        == Intent.OBJECT_COUNTING.value
    )


def test_image_understanding(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "what is shown in this image?",
        request_id="test-understanding-001",
        inputs=[
            ObservationInput(
                input_id="image-001",
                type="image",
            )
        ],
    )

    assert (
        result.classification.intent
        == Intent.IMAGE_UNDERSTANDING
    )

    assert result.routing.supported is True

    assert (
        result.structured_query.request_id
        == "test-understanding-001"
    )

    assert (
        "image-001"
        in [
            item.input_id
            for item in result.structured_query.inputs
        ]
    )


def test_change_detection(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "what changed between these two images?",
        request_id="test-change-001",
        context=ConversationContext(
            observations=(
                ObservationContext(
                    observation_id="image-001",
                ),
                ObservationContext(
                    observation_id="image-002",
                ),
            )
        ),
    )

    assert (
        result.classification.intent
        == Intent.CHANGE_DETECTION
    )

    assert result.routing.supported is True

    assert (
        result.structured_query.request_id
        == "test-change-001"
    )

    input_ids = [
        item.input_id
        for item in result.structured_query.inputs
    ]

    assert "image-001" in input_ids
    assert "image-002" in input_ids


def test_segmentation(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "segment the buildings",
        request_id="test-segmentation-001",
    )

    assert (
        result.classification.intent
        == Intent.SEGMENTATION
    )

    assert result.routing.supported is True

    assert (
        result.structured_query.request_id
        == "test-segmentation-001"
    )


def test_greeting(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "hello",
        request_id="test-greeting-001",
    )

    assert (
        result.classification.intent
        == Intent.GREETING
    )

    assert result.routing.supported is False

    assert result.routing.task is None

    assert (
        result.structured_query.request_id
        == "test-greeting-001"
    )

    assert (
        result.structured_query.requested_capabilities
        == []
    )


def test_empty_question_rejected(
    engine: QueryEngine,
) -> None:
    with pytest.raises(ValueError):
        engine.process(
            "",
            request_id="test-empty-001",
        )


def test_non_string_question_rejected(
    engine: QueryEngine,
) -> None:
    with pytest.raises(TypeError):
        engine.process(
            123,
            request_id="test-invalid-001",
        )


def test_empty_request_id_rejected(
    engine: QueryEngine,
) -> None:
    with pytest.raises(ValueError):
        engine.process(
            "hello",
            request_id="",
        )


def test_non_string_request_id_rejected(
    engine: QueryEngine,
) -> None:
    with pytest.raises(TypeError):
        engine.process(
            "hello",
            request_id=123,
        )


def test_explicit_input_is_preserved(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "describe this image",
        request_id="test-input-001",
        inputs=[
            ObservationInput(
                input_id="image-123",
                type="image",
            )
        ],
    )

    input_ids = [
        item.input_id
        for item in result.structured_query.inputs
    ]

    assert "image-123" in input_ids


def test_context_reference_is_resolved(
    engine: QueryEngine,
) -> None:
    result = engine.process(
        "describe this image",
        request_id="test-context-001",
        context=ConversationContext(
            observations=(
                ObservationContext(
                    observation_id="image-001",
                ),
            )
        ),
    )

    input_ids = [
        item.input_id
        for item in result.structured_query.inputs
    ]

    assert "image-001" in input_ids


def test_request_id_is_propagated(
    engine: QueryEngine,
) -> None:
    request_id = "request-abc-123"

    result = engine.process(
        "how many buildings are there?",
        request_id=request_id,
    )

    assert result.structured_query.request_id == request_id