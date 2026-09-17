import pytest

from query_engine.intent.preprocessor import TrainingExample
from query_engine.intent.splitter import split_dataset


def make_examples():
    return [
        TrainingExample(
            text=f"example {i}",
            intent=intent,
            language="en",
        )
        for intent in [
            "greeting",
            "object_counting",
            "change_detection",
        ]
        for i in range(10)
    ]


def test_split_dataset():
    examples = make_examples()

    result = split_dataset(examples)

    assert result.train
    assert result.validation
    assert result.test


def test_all_examples_are_preserved():
    examples = make_examples()

    result = split_dataset(examples)

    combined = (
        result.train
        + result.validation
        + result.test
    )

    assert len(combined) == len(examples)
    assert set(combined) == set(examples)


def test_each_intent_exists_in_train():
    examples = make_examples()

    result = split_dataset(examples)

    intents = {
        example.intent
        for example in result.train
    }

    assert intents == {
        "greeting",
        "object_counting",
        "change_detection",
    }


def test_each_intent_exists_in_validation():
    examples = make_examples()

    result = split_dataset(examples)

    intents = {
        example.intent
        for example in result.validation
    }

    assert intents == {
        "greeting",
        "object_counting",
        "change_detection",
    }


def test_each_intent_exists_in_test():
    examples = make_examples()

    result = split_dataset(examples)

    intents = {
        example.intent
        for example in result.test
    }

    assert intents == {
        "greeting",
        "object_counting",
        "change_detection",
    }


def test_split_is_reproducible():
    examples = make_examples()

    first = split_dataset(examples, seed=42)
    second = split_dataset(examples, seed=42)

    assert first == second


def test_empty_dataset_rejected():
    with pytest.raises(ValueError):
        split_dataset([])


def test_invalid_ratio_rejected():
    examples = make_examples()

    with pytest.raises(ValueError):
        split_dataset(
            examples,
            train_ratio=0.8,
            validation_ratio=0.3,
        )