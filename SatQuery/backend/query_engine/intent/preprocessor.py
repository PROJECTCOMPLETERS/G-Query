import re
from dataclasses import dataclass

from query_engine.intent.dataset import load_and_validate_dataset


@dataclass(frozen=True)
class TrainingExample:
    text: str
    intent: str
    language: str

def normalize_text(text: str) -> str:
    """
    Normalize user text before classification.

    Steps:
    1. Convert to lowercase
    2. Remove extra whitespace
    3. Normalize punctuation spacing
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip().lower()

    # Collapse multiple whitespace characters.
    text = re.sub(r"\s+", " ", text)

    return text


def build_training_examples() -> list[TrainingExample]:
    """
    Convert the multilingual intent dataset into
    a flat list of training examples.
    """

    dataset = load_and_validate_dataset()

    examples: list[TrainingExample] = []

    for intent, language_groups in dataset.items():

        for language, texts in language_groups.items():

            for text in texts:

                normalized = normalize_text(text)

                examples.append(
                    TrainingExample(
                        text=normalized,
                        intent=intent,
                        language=language,
                    )
                )

    return examples
    """
    Convert the intent dataset into a flat list of training examples.
    """

    dataset = load_and_validate_dataset()

    examples: list[TrainingExample] = []

    for intent, texts in dataset.items():
        for text in texts:
            normalized = normalize_text(text)

            examples.append(
                TrainingExample(
                    text=normalized,
                    intent=intent,
                )
            )

    return examples