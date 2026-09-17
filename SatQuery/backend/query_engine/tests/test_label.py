from query_engine.intent.labels import (
    Intent,
    SATELLITE_INTENTS,
    CONVERSATIONAL_INTENTS,
    GENERAL_INTENTS,
)


def test_intent_count():
    assert len(Intent) == 15


def test_conversational_intents():
    expected = {
        Intent.GREETING,
        Intent.FAREWELL,
        Intent.THANKS,
        Intent.ACKNOWLEDGEMENT,
        Intent.CAPABILITY_QUESTION,
    }

    assert CONVERSATIONAL_INTENTS == expected


def test_general_intents():
    expected = {
        Intent.GENERAL_QUESTION,
        Intent.DEFINITION,
        Intent.EXPLANATION,
    }

    assert GENERAL_INTENTS == expected


def test_satellite_intents():
    expected = {
        Intent.OBJECT_DETECTION,
        Intent.OBJECT_COUNTING,
        Intent.CHANGE_DETECTION,
        Intent.IMAGE_UNDERSTANDING,
        Intent.SEGMENTATION,
        Intent.LOCALIZATION,
        Intent.COMPARISON,
    }

    assert SATELLITE_INTENTS == expected


def test_every_intent_belongs_to_one_category():
    all_intents = (
        CONVERSATIONAL_INTENTS
        | GENERAL_INTENTS
        | SATELLITE_INTENTS
    )

    assert all_intents == set(Intent)


def test_no_intent_belongs_to_multiple_categories():
    groups = [
        CONVERSATIONAL_INTENTS,
        GENERAL_INTENTS,
        SATELLITE_INTENTS,
    ]

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            assert groups[i].isdisjoint(groups[j])