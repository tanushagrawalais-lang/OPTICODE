"""Language detection subsystem for OptiCode Analyzer.

Provides conservative language detection, alias normalization, and ambiguity resolution.
"""

from typing import Optional
from opticode.detector.aliases import (
    CANONICAL_ALIASES,
    get_supported_aliases,
    normalize_alias,
    resolve_declared_language,
)
from opticode.detector.detector import LanguageDetector
from opticode.models.detection import LanguageDetectionResult

_default_detector: Optional[LanguageDetector] = None


def get_default_language_detector() -> LanguageDetector:
    """Returns the shared default LanguageDetector instance."""
    global _default_detector
    if _default_detector is None:
        _default_detector = LanguageDetector()
    return _default_detector


def detect(
    source_code: str,
    declared_language: Optional[str] = None,
) -> LanguageDetectionResult:
    """Convenience function to detect language using the default detector."""
    return get_default_language_detector().detect(source_code, declared_language)


__all__ = [
    "LanguageDetector",
    "LanguageDetectionResult",
    "CANONICAL_ALIASES",
    "get_supported_aliases",
    "normalize_alias",
    "resolve_declared_language",
    "get_default_language_detector",
    "detect",
]
