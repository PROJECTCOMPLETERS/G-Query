import pytest

from query_engine.intent.labels import Intent
from query_engine.router.task_router import (
    TaskRouter,
    TaskType,
)


@pytest.fixture
def router():
    return TaskRouter()


# ============================================================
# SATELLITE TASK ROUTING
# ============================================================


def test_object_detection(
    router,
):

    result = router.route(
        Intent.OBJECT_DETECTION
    )

    assert result.supported is True

    assert result.task == (
        TaskType.OBJECT_DETECTION
    )


def test_object_counting(
    router,
):

    result = router.route(
        Intent.OBJECT_COUNTING
    )

    assert result.supported is True

    assert result.task == (
        TaskType.OBJECT_COUNTING
    )


def test_change_detection(
    router,
):

    result = router.route(
        Intent.CHANGE_DETECTION
    )

    assert result.supported is True

    assert result.task == (
        TaskType.CHANGE_DETECTION
    )


def test_image_understanding(
    router,
):

    result = router.route(
        Intent.IMAGE_UNDERSTANDING
    )

    assert result.supported is True

    assert result.task == (
        TaskType.IMAGE_UNDERSTANDING
    )


def test_segmentation(
    router,
):

    result = router.route(
        Intent.SEGMENTATION
    )

    assert result.supported is True

    assert result.task == (
        TaskType.SEGMENTATION
    )


def test_localization(
    router,
):

    result = router.route(
        Intent.LOCALIZATION
    )

    assert result.supported is True

    assert result.task == (
        TaskType.LOCALIZATION
    )


def test_comparison(
    router,
):

    result = router.route(
        Intent.COMPARISON
    )

    assert result.supported is True

    assert result.task == (
        TaskType.COMPARISON
    )


# ============================================================
# NON-ANALYSIS INTENTS
# ============================================================


@pytest.mark.parametrize(
    "intent",
    [
        Intent.GREETING,
        Intent.FAREWELL,
        Intent.THANKS,
        Intent.ACKNOWLEDGEMENT,
        Intent.CAPABILITY_QUESTION,
        Intent.GENERAL_QUESTION,
        Intent.DEFINITION,
        Intent.EXPLANATION,
    ],
)
def test_non_analysis_intents_are_not_tasks(
    router,
    intent,
):

    result = router.route(intent)

    assert result.supported is False

    assert result.task is None

    assert result.intent == intent

    assert result.reason is not None


# ============================================================
# RESULT CONTRACT
# ============================================================


def test_supported_result_contract(
    router,
):

    result = router.route(
        Intent.OBJECT_COUNTING
    )

    assert result.intent == (
        Intent.OBJECT_COUNTING
    )

    assert result.supported is True

    assert result.task == (
        TaskType.OBJECT_COUNTING
    )

    assert result.reason is None


def test_unsupported_result_contract(
    router,
):

    result = router.route(
        Intent.GREETING
    )

    assert result.intent == (
        Intent.GREETING
    )

    assert result.supported is False

    assert result.task is None

    assert isinstance(
        result.reason,
        str,
    )


# ============================================================
# VALIDATION
# ============================================================


def test_invalid_intent_fails(
    router,
):

    with pytest.raises(TypeError):

        router.route(
            "object_counting"
        )


def test_none_intent_fails(
    router,
):

    with pytest.raises(TypeError):

        router.route(None)