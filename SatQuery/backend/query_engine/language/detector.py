import re
import unicodedata

from query_engine.language.schemas import LanguageResult


TAMIL_WORDS = {
    "naan",
    "nee",
    "neenga",
    "enna",
    "ennanga",
    "ethana",
    "evlo",
    "irukku",
    "iruku",
    "iruka",
    "pannu",
    "pannunga",
    "pannunga",
    "intha",
    "indha",
    "andha",
    "image",
    "la",
    "ulla",
    "compare",
    "pannu",
    "pannunga",
}

SCRIPT_LANGUAGE_MAP = {
    "tamil": "ta",
    "devanagari": "hi",
    "telugu": "te",
    "kannada": "kn",
    "malayalam": "ml",
}


def _get_script(character: str) -> str | None:
    """
    Determine the Unicode script of a character.
    """

    if not character.isalpha():
        return None

    name = unicodedata.name(character, "")

    for script in SCRIPT_LANGUAGE_MAP:
        if script.upper() in name:
            return script

    if "LATIN" in name:
        return "latin"

    return None


def _count_scripts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}

    for character in text:
        script = _get_script(character)

        if script:
            counts[script] = counts.get(script, 0) + 1

    return counts


def _latin_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def _detect_tanglish(tokens: list[str]) -> bool:
    """
    Detect likely Tamil written using Latin characters.
    """

    tamil_matches = set(tokens).intersection(TAMIL_WORDS)

    return len(tamil_matches) >= 2


def _detect_english_tokens(tokens: list[str]) -> bool:
    """
    Determine whether ordinary English words are present.

    This is intentionally conservative. Semantic language
    identification will later be handled by the multilingual
    embedding layer.
    """

    english_words = {
        "hello",
        "hi",
        "hey",
        "what",
        "how",
        "many",
        "is",
        "are",
        "the",
        "this",
        "that",
        "image",
        "images",
        "building",
        "buildings",
        "road",
        "roads",
        "vehicle",
        "vehicles",
        "ship",
        "ships",
        "compare",
        "these",
        "two",
        "detect",
        "find",
        "show",
        "me",
        "can",
        "you",
        "please",
        "change",
        "changes",
    }

    return bool(set(tokens).intersection(english_words))


def detect_language(text: str) -> LanguageResult:
    """
    Detect language characteristics.

    Supports:
    - English
    - Tamil
    - Tanglish
    - Tamil + English
    - Other supported Indian scripts
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return LanguageResult(
            primary_language="unknown",
            languages=frozenset(),
            script="unknown",
            is_mixed=False,
            is_transliterated=False,
            confidence=0.0,
        )

    scripts = _count_scripts(text)

    tokens = _latin_tokens(text)

    if not scripts and not tokens:
        return LanguageResult(
            primary_language="unknown",
            languages=frozenset(),
            script="unknown",
            is_mixed=False,
            is_transliterated=False,
            confidence=0.0,
        )

    languages: set[str] = set()

    # Native-script languages.
    for script in scripts:
        language = SCRIPT_LANGUAGE_MAP.get(script)

        if language:
            languages.add(language)

    tanglish = False

    if "latin" in scripts:
        tanglish = _detect_tanglish(tokens)

        if tanglish:
            languages.add("ta")

        if _detect_english_tokens(tokens):
            languages.add("en")

        # Pure Latin input with no Tanglish signal.
        if not tanglish and "en" not in languages:
            languages.add("en")

    # Determine whether multiple languages are present.
    is_mixed = len(languages) > 1

    # Primary language.
    if tanglish:
        primary_language = "ta"

    elif len(languages) == 1:
        primary_language = next(iter(languages))

    elif "ta" in languages:
        primary_language = "ta"

    else:
        primary_language = "unknown"

    # Script classification.
    script_names = set(scripts)

    if len(script_names) == 1:
        script = next(iter(script_names))
    elif len(script_names) > 1:
        script = "mixed"
    elif tanglish:
        script = "latin"
    else:
        script = "unknown"

    # Confidence.
    if is_mixed:
        confidence = 0.75
    elif tanglish:
        confidence = 0.80
    elif primary_language != "unknown":
        confidence = 1.0
    else:
        confidence = 0.0

    return LanguageResult(
        primary_language=primary_language,
        languages=frozenset(languages),
        script=script,
        is_mixed=is_mixed,
        is_transliterated=tanglish,
        confidence=confidence,
    )