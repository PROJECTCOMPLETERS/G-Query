from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageResult:
    primary_language: str
    languages: frozenset[str]
    script: str
    is_mixed: bool
    is_transliterated: bool
    confidence: float