import pytest

from query_engine.intent.preprocessor import (
    TrainingExample,
    normalize_text,
    build_training_examples,
)


def test_normalize_lowercase():
    assert normalize_text("Hello WORLD") == "hello world"


def test_normalize_whitespace():
    assert normalize_text(
        "  how   many   buildings   are   there  "
    ) == "how many buildings are there"


def test_normalize_preserves_meaningful_punctuation():
    assert normalize_text(
        "What is SAR?"
    ) == "what is sar?"


def test_normalize_requires_string():
    with pytest.raises(TypeError):
        normalize_text(123)


def test_training_examples_are_created():
    examples = build_training_examples()

    assert examples
    assert all(
        isinstance(example, TrainingExample)
        for example in examples
    )


def test_training_examples_have_text_and_intent():
    examples = build_training_examples()

    for example in examples:
        assert example.text
        assert example.intent


def test_training_examples_are_normalized():
    examples = build_training_examples()

    for example in examples:
        assert example.text == example.text.strip()
        assert example.text == example.text.lower()


def test_expected_example_exists():
    examples = build_training_examples()

    assert TrainingExample(
        text="how many buildings are there",
        intent="object_counting",
        language="en",
    ) in examples