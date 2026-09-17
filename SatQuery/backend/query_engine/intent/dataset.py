import json
from pathlib import Path

from query_engine.intent.labels import Intent


DATA_FILE = Path(__file__).parent / "data" / "intents.json"


def load_intent_dataset() -> dict[str, list[str]]:
    """
    Load the intent dataset from intents.json.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def validate_intent_dataset(
    dataset: dict,
) -> None:
    """
    Validate multilingual intent dataset.
    """

    valid_intents = {
        intent.value
        for intent in Intent
    }

    dataset_intents = set(dataset.keys())

    missing_intents = (
        valid_intents - dataset_intents
    )

    if missing_intents:
        raise ValueError(
            f"Missing intents: {sorted(missing_intents)}"
        )

    unknown_intents = (
        dataset_intents - valid_intents
    )

    if unknown_intents:
        raise ValueError(
            f"Unknown intents: {sorted(unknown_intents)}"
        )

    for intent, language_groups in dataset.items():

        if not isinstance(language_groups, dict):
            raise TypeError(
                f"'{intent}' must contain language groups"
            )

        required_languages = {
            "en",
            "ta",
            "ta_latn",
            "mixed",
        }

        missing_languages = (
            required_languages
            - set(language_groups.keys())
        )

        if missing_languages:
            raise ValueError(
                f"'{intent}' missing languages: "
                f"{sorted(missing_languages)}"
            )

        for language, examples in language_groups.items():

            if not isinstance(examples, list):
                raise TypeError(
                    f"Examples for "
                    f"'{intent}/{language}' "
                    "must be a list"
                )

            if not examples:
                raise ValueError(
                    f"'{intent}/{language}' "
                    "has no examples"
                )

            for example in examples:

                if not isinstance(example, str):
                    raise TypeError(
                        f"Example for "
                        f"'{intent}/{language}' "
                        "must be a string"
                    )

                if not example.strip():
                    raise ValueError(
                        f"'{intent}/{language}' "
                        "contains empty example"
                    )

def load_and_validate_dataset() -> dict[str, list[str]]:
    """
    Load and validate the complete intent dataset.
    """

    dataset = load_intent_dataset()

    validate_intent_dataset(dataset)

    return dataset