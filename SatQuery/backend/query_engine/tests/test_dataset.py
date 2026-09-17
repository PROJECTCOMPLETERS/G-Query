import pytest

from query_engine.intent.dataset import (
    load_intent_dataset,
    load_and_validate_dataset,
    validate_intent_dataset,
)
from query_engine.intent.labels import Intent


REQUIRED_LANGUAGES = {
    "en",
    "ta",
    "ta_latn",
    "mixed",
}


def test_dataset_loads():
    dataset = load_intent_dataset()

    assert isinstance(dataset, dict)
    assert dataset


def test_all_intents_are_present():
    dataset = load_intent_dataset()

    expected_intents = {
        intent.value
        for intent in Intent
    }

    assert set(dataset.keys()) == expected_intents


def test_every_intent_has_all_languages():
    dataset = load_intent_dataset()

    for intent, languages in dataset.items():

        assert isinstance(languages, dict)

        assert set(languages.keys()) == REQUIRED_LANGUAGES


def test_every_language_has_examples():
    dataset = load_intent_dataset()

    for intent, languages in dataset.items():

        for language, examples in languages.items():

            assert isinstance(examples, list)
            assert len(examples) > 0


def test_examples_are_strings():
    dataset = load_intent_dataset()

    for languages in dataset.values():

        for examples in languages.values():

            for example in examples:

                assert isinstance(example, str)
                assert example.strip()


def test_dataset_validation():
    dataset = load_and_validate_dataset()

    assert dataset


def test_unknown_intent_is_rejected():
    dataset = load_intent_dataset()

    dataset["unknown_intent"] = {
        "en": ["some example"],
        "ta": ["சில உதாரணம்"],
        "ta_latn": ["sila udharanam"],
        "mixed": ["some example சில"],
    }

    with pytest.raises(ValueError, match="Unknown intents"):
        validate_intent_dataset(dataset)


def test_missing_intent_is_rejected():
    dataset = load_intent_dataset()

    dataset.pop("greeting")

    with pytest.raises(ValueError, match="Missing intents"):
        validate_intent_dataset(dataset)


def test_missing_language_is_rejected():
    dataset = load_intent_dataset()

    dataset["greeting"].pop("ta")

    with pytest.raises(ValueError, match="missing languages"):
        validate_intent_dataset(dataset)


def test_empty_language_examples_are_rejected():
    dataset = load_intent_dataset()

    dataset["greeting"]["ta"] = []

    with pytest.raises(
        ValueError,
        match="has no examples",
    ):
        validate_intent_dataset(dataset)


def test_non_list_examples_are_rejected():
    dataset = load_intent_dataset()

    dataset["greeting"]["ta"] = "வணக்கம்"

    with pytest.raises(
        TypeError,
        match="must be a list",
    ):
        validate_intent_dataset(dataset)


def test_non_string_example_is_rejected():
    dataset = load_intent_dataset()

    dataset["greeting"]["ta"].append(123)

    with pytest.raises(
        TypeError,
        match="must be a string",
    ):
        validate_intent_dataset(dataset)


def test_empty_example_is_rejected():
    dataset = load_intent_dataset()

    dataset["greeting"]["ta"].append("   ")

    with pytest.raises(
        ValueError,
        match="contains empty example",
    ):
        validate_intent_dataset(dataset)


def test_language_distribution():
    dataset = load_intent_dataset()

    counts = {
        language: 0
        for language in REQUIRED_LANGUAGES
    }

    for languages in dataset.values():

        for language, examples in languages.items():

            counts[language] += len(examples)

    for language, count in counts.items():
        assert count > 0


def test_all_intents_have_examples_in_all_languages():
    dataset = load_intent_dataset()

    for intent in Intent:

        languages = dataset[intent.value]

        for language in REQUIRED_LANGUAGES:

            assert len(
                languages[language]
            ) > 0


def test_dataset_contains_tanglish_examples():
    dataset = load_intent_dataset()

    tanglish_examples = []

    for languages in dataset.values():
        tanglish_examples.extend(
            languages["ta_latn"]
        )

    assert tanglish_examples


def test_dataset_contains_mixed_examples():
    dataset = load_intent_dataset()

    mixed_examples = []

    for languages in dataset.values():
        mixed_examples.extend(
            languages["mixed"]
        )

    assert mixed_examples