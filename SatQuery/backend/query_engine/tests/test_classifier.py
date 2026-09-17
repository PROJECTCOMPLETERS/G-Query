import pytest

from query_engine.intent.classifier import IntentClassifier
from query_engine.intent.labels import (
    Intent,
    SATELLITE_INTENTS,
    CONVERSATIONAL_INTENTS,
    GENERAL_INTENTS,
)
from query_engine.intent.preprocessor import build_training_examples


@pytest.fixture(scope="module")
def classifier():
    """
    Train the classifier once for the entire test module.
    """
    model = IntentClassifier()
    model.train(epochs=100)
    return model


@pytest.fixture(scope="module")
def training_examples():
    """
    Load the complete multilingual training dataset.
    """
    return build_training_examples()


# ============================================================
# CLASSIFIER STRUCTURE
# ============================================================


def test_classifier_has_all_intents(classifier):
    assert len(classifier.intent_to_index) == len(Intent)

    for intent in Intent:
        assert intent in classifier.intent_to_index


def test_classifier_index_mapping_is_unique(classifier):
    indices = list(classifier.intent_to_index.values())

    assert len(indices) == len(set(indices))


def test_classifier_covers_all_intent_categories(classifier):
    mapped_intents = set(classifier.intent_to_index.keys())

    assert CONVERSATIONAL_INTENTS.issubset(mapped_intents)
    assert GENERAL_INTENTS.issubset(mapped_intents)
    assert SATELLITE_INTENTS.issubset(mapped_intents)


# ============================================================
# ENGLISH PREDICTIONS
# ============================================================


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "how many buildings are there",
            Intent.OBJECT_COUNTING,
        ),
        (
            "detect buildings in this image",
            Intent.OBJECT_DETECTION,
        ),
        (
            "what changed between these images",
            Intent.CHANGE_DETECTION,
        ),
        (
            "what is shown in this image",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "segment the buildings",
            Intent.SEGMENTATION,
        ),
        (
            "locate the road",
            Intent.LOCALIZATION,
        ),
        (
            "compare these two images",
            Intent.COMPARISON,
        ),
        (
            "hello",
            Intent.GREETING,
        ),
        (
            "goodbye",
            Intent.FAREWELL,
        ),
        (
            "thank you",
            Intent.THANKS,
        ),
        (
            "okay",
            Intent.ACKNOWLEDGEMENT,
        ),
        (
            "what can you do",
            Intent.CAPABILITY_QUESTION,
        ),
        (
            "what is SAR",
            Intent.DEFINITION,
        ),
        (
            "how does satellite imaging work",
            Intent.EXPLANATION,
        ),
        (
            "what is satellite imagery",
            Intent.GENERAL_QUESTION,
        ),
    ],
)
def test_english_predictions(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


# ============================================================
# TAMIL PREDICTIONS
# ============================================================


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "வணக்கம்",
            Intent.GREETING,
        ),
        (
            "பிரியாவிடை",
            Intent.FAREWELL,
        ),
        (
            "நன்றி",
            Intent.THANKS,
        ),
        (
            "சரி",
            Intent.ACKNOWLEDGEMENT,
        ),
        (
            "எத்தனை கட்டிடங்கள் உள்ளன",
            Intent.OBJECT_COUNTING,
        ),
        (
            "இந்த படத்தில் என்ன இருக்கிறது",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "இந்த இரண்டு படங்களுக்கு இடையில் என்ன மாற்றம் ஏற்பட்டுள்ளது",
            Intent.CHANGE_DETECTION,
        ),
    ],
)
def test_tamil_predictions(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


# ============================================================
# TANGLISH PREDICTIONS
# ============================================================


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "vanakkam",
            Intent.GREETING,
        ),
        (
            "bye",
            Intent.FAREWELL,
        ),
        (
            "nandri",
            Intent.THANKS,
        ),
        (
            "seri",
            Intent.ACKNOWLEDGEMENT,
        ),
        (
            "ethana buildings irukku",
            Intent.OBJECT_COUNTING,
        ),
        (
            "indha image la enna irukku",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "indha rendu images ku naduvula enna change aachu",
            Intent.CHANGE_DETECTION,
        ),
        (
            "buildings ah segment pannu",
            Intent.SEGMENTATION,
        ),
    ],
)
def test_tanglish_predictions(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


# ============================================================
# MIXED LANGUAGE PREDICTIONS
# ============================================================


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "வணக்கம் satquery",
            Intent.GREETING,
        ),
        (
            "சரி bye",
            Intent.FAREWELL,
        ),
        (
            "ரொம்ப thanks",
            Intent.THANKS,
        ),
        (
            "சரி got it",
            Intent.ACKNOWLEDGEMENT,
        ),
        (
            "இந்த image la ethana buildings irukku",
            Intent.OBJECT_COUNTING,
        ),
        (
            "இந்த image la buildings detect pannu",
            Intent.OBJECT_DETECTION,
        ),
        (
            "இந்த image la enna irukku",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "இந்த இரண்டு images la என்ன change ஆச்சு",
            Intent.CHANGE_DETECTION,
        ),
        (
            "இந்த image ல buildings ah segment பண்ணு",
            Intent.SEGMENTATION,
        ),
        (
            "இந்த இரண்டு images ah compare பண்ணு",
            Intent.COMPARISON,
        ),
    ],
)
def test_mixed_language_predictions(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


# ============================================================
# PROBABILITY TESTS
# ============================================================


def test_classification_probabilities_sum_to_one(classifier):
    result = classifier.classify(
        "how many buildings are there"
    )

    total = sum(result.probabilities.values())

    assert total == pytest.approx(
        1.0,
        abs=1e-5,
    )


def test_classification_confidence_is_valid(classifier):
    result = classifier.classify(
        "how many buildings are there"
    )

    assert 0.0 <= result.confidence <= 1.0


def test_probability_keys_match_intents(classifier):
    result = classifier.classify(
        "detect buildings"
    )

    assert set(result.probabilities.keys()) == set(Intent)


# ============================================================
# EVALUATION
# ============================================================


def test_evaluation_returns_valid_accuracy(
    classifier,
    training_examples,
):
    accuracy = classifier.evaluate(
        training_examples
    )

    assert 0.0 <= accuracy <= 1.0


# ============================================================
# LANGUAGE SUPPORT
# ============================================================


def test_classifier_handles_english(classifier):
    examples = [
        "hello",
        "how many buildings are there",
        "compare these images",
        "detect roads",
        "what is SAR",
    ]

    for text in examples:
        result = classifier.classify(text)

        assert isinstance(result.intent, Intent)
        assert 0.0 <= result.confidence <= 1.0


def test_classifier_handles_tamil(classifier):
    examples = [
        "வணக்கம்",
        "எத்தனை கட்டிடங்கள் உள்ளன",
        "இந்த படத்தில் என்ன இருக்கிறது",
    ]

    for text in examples:
        result = classifier.classify(text)

        assert isinstance(result.intent, Intent)
        assert 0.0 <= result.confidence <= 1.0


def test_classifier_handles_tanglish(classifier):
    examples = [
        "vanakkam",
        "ethana buildings irukku",
        "indha image la enna irukku",
    ]

    for text in examples:
        result = classifier.classify(text)

        assert isinstance(result.intent, Intent)
        assert 0.0 <= result.confidence <= 1.0


def test_classifier_handles_mixed_language(classifier):
    examples = [
        "இந்த image la ethana buildings irukku",
        "இந்த image ah compare pannu",
        "indha image la road detect pannu",
    ]

    for text in examples:
        result = classifier.classify(text)

        assert isinstance(result.intent, Intent)
        assert 0.0 <= result.confidence <= 1.0


# ============================================================
# HARD SEMANTIC BOUNDARIES
# ============================================================


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "what is shown in this image",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "what can you see in this image",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "describe this image",
            Intent.IMAGE_UNDERSTANDING,
        ),
        (
            "what changed between these images",
            Intent.CHANGE_DETECTION,
        ),
        (
            "has this area changed over time",
            Intent.CHANGE_DETECTION,
        ),
    ],
)
def test_image_understanding_vs_change_detection(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "detect buildings",
            Intent.OBJECT_DETECTION,
        ),
        (
            "find buildings in this image",
            Intent.OBJECT_DETECTION,
        ),
        (
            "segment the buildings",
            Intent.SEGMENTATION,
        ),
        (
            "create a segmentation mask for buildings",
            Intent.SEGMENTATION,
        ),
    ],
)
def test_detection_vs_segmentation(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "hello",
            Intent.GREETING,
        ),
        (
            "hi",
            Intent.GREETING,
        ),
        (
            "goodbye",
            Intent.FAREWELL,
        ),
        (
            "bye",
            Intent.FAREWELL,
        ),
        (
            "see you later",
            Intent.FAREWELL,
        ),
    ],
)
def test_greeting_vs_farewell(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        (
            "what is SAR",
            Intent.DEFINITION,
        ),
        (
            "what is satellite imagery",
            Intent.GENERAL_QUESTION,
        ),
        (
            "how does SAR work",
            Intent.EXPLANATION,
        ),
        (
            "how does satellite imaging work",
            Intent.EXPLANATION,
        ),
        (
            "explain remote sensing",
            Intent.EXPLANATION,
        ),
    ],
)
def test_general_question_vs_definition_vs_explanation(
    classifier,
    text,
    expected_intent,
):
    result = classifier.classify(text)

    assert result.intent == expected_intent


# ============================================================
# DATASET COVERAGE
# ============================================================


def test_training_examples_are_multilingual(
    training_examples,
):
    languages = {
        example.language
        for example in training_examples
    }

    assert "en" in languages
    assert "ta" in languages
    assert "ta_latn" in languages
    assert "mixed" in languages


def test_every_intent_has_training_examples(
    training_examples,
):
    intents = {
        example.intent
        for example in training_examples
    }

    expected = {
        intent.value
        for intent in Intent
    }

    assert intents == expected


def test_every_intent_has_all_languages(
    training_examples,
):
    coverage = {
        intent.value: set()
        for intent in Intent
    }

    for example in training_examples:
        coverage[example.intent].add(
            example.language
        )

    required_languages = {
        "en",
        "ta",
        "ta_latn",
        "mixed",
    }

    for intent in Intent:
        assert (
            coverage[intent.value]
            == required_languages
        )