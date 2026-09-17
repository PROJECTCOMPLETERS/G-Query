import random
from dataclasses import dataclass

from query_engine.intent.preprocessor import (
    TrainingExample,
    build_training_examples,
)


@dataclass(frozen=True)
class DatasetSplit:
    train: list[TrainingExample]
    validation: list[TrainingExample]
    test: list[TrainingExample]


def split_dataset(
    examples: list[TrainingExample],
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    seed: int = 42,
) -> DatasetSplit:
    """
    Split examples into train, validation and test sets.

    The split is performed independently for each intent so that
    every intent is represented in all three datasets.
    """

    if not examples:
        raise ValueError("Dataset cannot be empty")

    if train_ratio <= 0:
        raise ValueError("train_ratio must be greater than zero")

    if validation_ratio < 0:
        raise ValueError("validation_ratio cannot be negative")

    if train_ratio + validation_ratio >= 1:
        raise ValueError(
            "train_ratio + validation_ratio must be less than 1"
        )

    grouped: dict[str, list[TrainingExample]] = {}

    for example in examples:
        grouped.setdefault(example.intent, []).append(example)

    rng = random.Random(seed)

    train: list[TrainingExample] = []
    validation: list[TrainingExample] = []
    test: list[TrainingExample] = []

    for intent_examples in grouped.values():

        shuffled = intent_examples.copy()
        rng.shuffle(shuffled)

        total = len(shuffled)

        train_end = max(1, int(total * train_ratio))

        remaining = total - train_end

        validation_count = 0

        if remaining >= 2:
            validation_count = max(
                1,
                int(total * validation_ratio),
            )

        validation_end = train_end + validation_count

        train.extend(shuffled[:train_end])
        validation.extend(shuffled[train_end:validation_end])
        test.extend(shuffled[validation_end:])

    return DatasetSplit(
        train=train,
        validation=validation,
        test=test,
    )


def create_dataset_split() -> DatasetSplit:
    """
    Build and split the current intent dataset.
    """

    examples = build_training_examples()

    return split_dataset(examples)