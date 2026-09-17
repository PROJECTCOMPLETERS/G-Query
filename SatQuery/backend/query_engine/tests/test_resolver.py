import pytest

from query_engine.context.resolver import ContextResolver
from query_engine.context.schemas import (
    ConversationContext,
    ObservationContext,
)


@pytest.fixture
def resolver():
    return ContextResolver()


@pytest.fixture
def context():
    return ConversationContext(
        observations=(
            ObservationContext(
                observation_id="obs_001",
                modality="optical",
                name="image_1",
            ),
            ObservationContext(
                observation_id="obs_002",
                modality="sar",
                name="image_2",
            ),
            ObservationContext(
                observation_id="obs_003",
                modality="optical",
                name="image_3",
            ),
        )
    )


def test_resolve_current_image(
    resolver,
    context,
):

    result = resolver.resolve(
        "what is shown in this image",
        context,
    )

    assert len(result.references) == 1

    reference = result.references[0]

    assert reference.reference == "current_image"

    assert reference.observation_ids == (
        "obs_003",
    )


def test_resolve_previous_image(
    resolver,
    context,
):

    result = resolver.resolve(
        "use the previous image",
        context,
    )

    reference = result.references[0]

    assert reference.reference == "previous_image"

    assert reference.observation_ids == (
        "obs_002",
    )


def test_resolve_first_image(
    resolver,
    context,
):

    result = resolver.resolve(
        "use the first image",
        context,
    )

    reference = result.references[0]

    assert reference.reference == "first_image"

    assert reference.observation_ids == (
        "obs_001",
    )


def test_resolve_second_image(
    resolver,
    context,
):

    result = resolver.resolve(
        "use the second image",
        context,
    )

    reference = result.references[0]

    assert reference.reference == "second_image"

    assert reference.observation_ids == (
        "obs_002",
    )


def test_resolve_multiple_images(
    resolver,
    context,
):

    result = resolver.resolve(
        "compare these two images",
        context,
    )

    reference = result.references[0]

    assert reference.reference == "multiple_images"

    assert reference.observation_ids == (
        "obs_002",
        "obs_003",
    )


def test_no_reference(
    resolver,
    context,
):

    result = resolver.resolve(
        "count buildings",
        context,
    )

    assert result.references == ()


def test_missing_current_image(
    resolver,
):

    context = ConversationContext()

    result = resolver.resolve(
        "describe this image",
        context,
    )

    assert result.references == ()


def test_missing_previous_image(
    resolver,
):

    context = ConversationContext(
        observations=(
            ObservationContext(
                observation_id="obs_001",
            ),
        )
    )

    result = resolver.resolve(
        "use the previous image",
        context,
    )

    assert result.references == ()


def test_empty_text_fails(
    resolver,
    context,
):

    with pytest.raises(ValueError):
        resolver.resolve(
            "",
            context,
        )


def test_non_string_fails(
    resolver,
    context,
):

    with pytest.raises(TypeError):
        resolver.resolve(
            None,
            context,
        )


def test_invalid_context_fails(
    resolver,
):

    with pytest.raises(TypeError):
        resolver.resolve(
            "describe this image",
            None,
        )