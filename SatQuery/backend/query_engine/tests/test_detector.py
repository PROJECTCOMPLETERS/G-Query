import pytest

from query_engine.language.detector import detect_language
from query_engine.language.schemas import LanguageResult


def test_english():
    result = detect_language(
        "How many buildings are there?"
    )

    assert isinstance(result, LanguageResult)
    assert result.primary_language == "en"
    assert result.languages == frozenset({"en"})
    assert result.script == "latin"
    assert result.is_mixed is False
    assert result.is_transliterated is False


def test_tamil_script():
    result = detect_language(
        "இந்த படத்தில் எத்தனை கட்டிடங்கள் உள்ளன?"
    )

    assert result.primary_language == "ta"
    assert result.languages == frozenset({"ta"})
    assert result.script == "tamil"
    assert result.is_mixed is False
    assert result.is_transliterated is False


def test_tanglish():
    result = detect_language(
        "indha image la ethana buildings irukku?"
    )

    assert result.primary_language == "ta"
    assert "ta" in result.languages
    assert result.is_transliterated is True


def test_tamil_english_mixed():
    result = detect_language(
        "இந்த image ல எத்தனை buildings இருக்கு?"
    )

    assert result.primary_language == "ta"
    assert result.languages == frozenset({"ta", "en"})
    assert result.script == "mixed"
    assert result.is_mixed is True
    assert result.is_transliterated is False


def test_tanglish_with_english():
    result = detect_language(
        "indha image la how many buildings irukku?"
    )

    assert result.primary_language == "ta"
    assert result.languages == frozenset({"ta", "en"})
    assert result.is_mixed is True
    assert result.is_transliterated is True


def test_hindi():
    result = detect_language(
        "इस तस्वीर में कितनी इमारतें हैं?"
    )

    assert result.primary_language == "hi"
    assert result.languages == frozenset({"hi"})


def test_telugu():
    result = detect_language(
        "ఈ చిత్రంలో ఎన్ని భవనాలు ఉన్నాయి?"
    )

    assert result.primary_language == "te"
    assert result.languages == frozenset({"te"})


def test_kannada():
    result = detect_language(
        "ಈ ಚಿತ್ರದಲ್ಲಿ ಎಷ್ಟು ಕಟ್ಟಡಗಳಿವೆ?"
    )

    assert result.primary_language == "kn"
    assert result.languages == frozenset({"kn"})


def test_malayalam():
    result = detect_language(
        "ഈ ചിത്രത്തിൽ എത്ര കെട്ടിടങ്ങളുണ്ട്?"
    )

    assert result.primary_language == "ml"
    assert result.languages == frozenset({"ml"})


def test_empty_text():
    result = detect_language("")

    assert result.primary_language == "unknown"
    assert result.languages == frozenset()
    assert result.confidence == 0.0


def test_symbols_only():
    result = detect_language("123 !!! ???")

    assert result.primary_language == "unknown"
    assert result.languages == frozenset()


def test_non_string():
    with pytest.raises(TypeError):
        detect_language(123)