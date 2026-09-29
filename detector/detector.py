from __future__ import annotations
import re
from typing import Dict, List, Optional, Set, Tuple
from opticode.models.common import DetectionStatus, Language
from opticode.models.detection import LanguageDetectionResult
from opticode.detector.aliases import resolve_declared_language
from opticode.detector.heuristics import (
    CPP_TOKEN_PATTERNS,
    GO_PATTERNS,
    JAVA_PATTERNS,
    PYTHON_PATTERNS,
    RUST_PATTERNS,
    TS_TOKEN_PATTERNS,
    has_cpp_constructs,
    has_typescript_constructs,
    matches_any_pattern,
)
from opticode.parser import ParserEngine, get_default_parser_engine
from opticode.parser.types import ParsedSyntaxTree

JS_TS_KEYWORDS = re.compile(
    r"(\bfunction\s+\w+\s*\(|\b(let|const|var)\s+\w+|\bconsole\.(log|warn|error)\b|===|!==|=>|\b(null|undefined)\b|\bexport\s+(default\s+)?)"
)

C_SPECIFIC_MARKERS = re.compile(
    r"(#\s*(include|define|ifdef|ifndef|endif)\b|\b(printf|scanf|malloc|free|sizeof|NULL)\b|\b(struct|union)\s+\w+|\bint\s+main\s*\()"
)


class LanguageDetector:
    """Subsystem responsible for determining source code language.

    Adheres strictly to the four-state model:
    - DECLARED: Language declared explicitly by caller and supported.
    - DETECTED: Exactly one language grammar accepts or distinguishing features confirm it.
    - UNCERTAIN: Multiple grammars accept (e.g. plain JS vs TS, plain C vs C++) or ambiguity is genuine.
    - UNSUPPORTED: Caller declared an unsupported language label.
    """

    def __init__(self, parser_engine: Optional[ParserEngine] = None) -> None:
        self.parser_engine = parser_engine or get_default_parser_engine()

    def detect(
        self,
        source_code: str,
        declared_language: Optional[str] = None,
    ) -> LanguageDetectionResult:
        """Determines the language of the source code.

        Args:
            source_code: The raw source code to analyze.
            declared_language: Optional caller-specified language hint/declaration.

        Returns:
            LanguageDetectionResult with status, language, confidence, candidates, and details.
        """
        # Rule 1 & 2: Explicit declaration handling
        if declared_language is not None and declared_language.strip() != "":
            resolved_lang, is_supported = resolve_declared_language(declared_language)
            if is_supported:
                return LanguageDetectionResult(
                    language=resolved_lang,
                    status=DetectionStatus.DECLARED,
                    confidence=1.0,
                    candidate_languages=[resolved_lang],
                    details=f"Language explicitly declared as '{declared_language}'.",
                )
            else:
                return LanguageDetectionResult(
                    language=Language.UNKNOWN,
                    status=DetectionStatus.UNSUPPORTED,
                    confidence=0.0,
                    candidate_languages=[],
                    details=(
                        f"Declared language '{declared_language}' is not supported. "
                        "Supported languages are: python, java, c, cpp, javascript, typescript, go, rust."
                    ),
                )

        # Rule 3: Empty / whitespace input handling
        if not source_code or not source_code.strip():
            return LanguageDetectionResult(
                language=Language.UNKNOWN,
                status=DetectionStatus.UNCERTAIN,
                confidence=0.0,
                candidate_languages=[],
                details="Source code is empty or whitespace only; language cannot be determined.",
            )

        # Rule 3: Parser evidence across all 8 supported languages
        clean_parses: Dict[Language, ParsedSyntaxTree] = {}
        error_parses: Dict[Language, Tuple[ParsedSyntaxTree, int]] = {}

        for lang in self.parser_engine.registry.get_supported_languages():
            try:
                tree = self.parser_engine.parse(source_code, lang)
                if not tree.has_errors:
                    clean_parses[lang] = tree
                else:
                    error_parses[lang] = (tree, len(tree.errors))
            except Exception:
                continue

        clean_langs: Set[Language] = set(clean_parses.keys())

        # Prune spurious C/C++ typedef matches when explicit JS/TS keywords are present
        if (Language.JAVASCRIPT in clean_langs or Language.TYPESCRIPT in clean_langs) and (
            Language.C in clean_langs or Language.CPP in clean_langs
        ):
            if JS_TS_KEYWORDS.search(source_code) and not C_SPECIFIC_MARKERS.search(source_code):
                clean_langs.discard(Language.C)
                clean_langs.discard(Language.CPP)

        # Prune spurious Java matches when standard C main / C markers are present without Java class/package
        if Language.JAVA in clean_langs and (Language.C in clean_langs or Language.CPP in clean_langs):
            if C_SPECIFIC_MARKERS.search(source_code) and not matches_any_pattern(source_code, JAVA_PATTERNS):
                clean_langs.discard(Language.JAVA)

        # Rule 4: Exactly one clean parse
        if len(clean_langs) == 1:
            lang = next(iter(clean_langs))
            return LanguageDetectionResult(
                language=lang,
                status=DetectionStatus.DETECTED,
                confidence=0.95,
                candidate_languages=[lang],
                details=f"Language cleanly accepted by {lang.value} grammar with zero syntax errors.",
            )

        # Rule 5 & 6: Multiple clean parses -> conservative disambiguation
        if len(clean_langs) > 1:
            return self._disambiguate_multiple_clean(source_code, clean_parses, clean_langs)

        # Fallback: Zero clean parses (invalid / malformed source)
        return self._handle_malformed_code(source_code, error_parses)

    def _disambiguate_multiple_clean(
        self,
        source_code: str,
        clean_parses: Dict[Language, ParsedSyntaxTree],
        clean_langs: Set[Language],
    ) -> LanguageDetectionResult:
        # Disambiguation: JavaScript vs TypeScript
        if clean_langs == {Language.JAVASCRIPT, Language.TYPESCRIPT}:
            ts_tree = clean_parses.get(Language.TYPESCRIPT)
            if has_typescript_constructs(source_code, ts_tree):
                return LanguageDetectionResult(
                    language=Language.TYPESCRIPT,
                    status=DetectionStatus.DETECTED,
                    confidence=0.95,
                    candidate_languages=[Language.TYPESCRIPT],
                    details="TypeScript detected via explicit type annotations or TypeScript constructs.",
                )
            else:
                return LanguageDetectionResult(
                    language=Language.UNKNOWN,
                    status=DetectionStatus.UNCERTAIN,
                    confidence=0.5,
                    candidate_languages=[Language.JAVASCRIPT, Language.TYPESCRIPT],
                    details="Syntax is valid in both JavaScript and TypeScript without explicit type annotations.",
                )

        # Disambiguation: C vs C++
        if clean_langs == {Language.C, Language.CPP}:
            cpp_tree = clean_parses.get(Language.CPP)
            if has_cpp_constructs(source_code, cpp_tree):
                return LanguageDetectionResult(
                    language=Language.CPP,
                    status=DetectionStatus.DETECTED,
                    confidence=0.95,
                    candidate_languages=[Language.CPP],
                    details="C++ detected via explicit C++ constructs (classes, templates, namespaces, or C++ headers).",
                )
            else:
                return LanguageDetectionResult(
                    language=Language.UNKNOWN,
                    status=DetectionStatus.UNCERTAIN,
                    confidence=0.5,
                    candidate_languages=[Language.C, Language.CPP],
                    details="Syntax is valid in both C and C++ without explicit C++ constructs; cannot claim certainty.",
                )

        # Check for unique syntax markers to resolve other overlaps if possible
        if matches_any_pattern(source_code, PYTHON_PATTERNS) and Language.PYTHON in clean_langs:
            return LanguageDetectionResult(
                language=Language.PYTHON,
                status=DetectionStatus.DETECTED,
                confidence=0.90,
                candidate_languages=[Language.PYTHON],
                details="Python detected via unique syntax markers and clean grammar acceptance.",
            )

        if matches_any_pattern(source_code, GO_PATTERNS) and Language.GO in clean_langs:
            return LanguageDetectionResult(
                language=Language.GO,
                status=DetectionStatus.DETECTED,
                confidence=0.90,
                candidate_languages=[Language.GO],
                details="Go detected via unique package/func markers and clean grammar acceptance.",
            )

        if matches_any_pattern(source_code, RUST_PATTERNS) and Language.RUST in clean_langs:
            return LanguageDetectionResult(
                language=Language.RUST,
                status=DetectionStatus.DETECTED,
                confidence=0.90,
                candidate_languages=[Language.RUST],
                details="Rust detected via unique fn/let markers and clean grammar acceptance.",
            )

        if matches_any_pattern(source_code, JAVA_PATTERNS) and Language.JAVA in clean_langs:
            return LanguageDetectionResult(
                language=Language.JAVA,
                status=DetectionStatus.DETECTED,
                confidence=0.90,
                candidate_languages=[Language.JAVA],
                details="Java detected via package/class markers and clean grammar acceptance.",
            )

        # If clean matches include TS along with others, check TS markers
        if Language.TYPESCRIPT in clean_langs and has_typescript_constructs(source_code, clean_parses.get(Language.TYPESCRIPT)):
            clean_langs.discard(Language.JAVASCRIPT)
            clean_langs.discard(Language.C)
            clean_langs.discard(Language.CPP)
            clean_langs.discard(Language.RUST)
            if len(clean_langs) == 1:
                return LanguageDetectionResult(
                    language=Language.TYPESCRIPT,
                    status=DetectionStatus.DETECTED,
                    confidence=0.95,
                    candidate_languages=[Language.TYPESCRIPT],
                    details="TypeScript detected via explicit type annotations or TypeScript constructs.",
                )

        # If clean matches include C and CPP along with others, check CPP markers
        if Language.CPP in clean_langs and has_cpp_constructs(source_code, clean_parses.get(Language.CPP)):
            clean_langs.discard(Language.C)
            if len(clean_langs) == 1:
                return LanguageDetectionResult(
                    language=Language.CPP,
                    status=DetectionStatus.DETECTED,
                    confidence=0.95,
                    candidate_languages=[Language.CPP],
                    details="C++ detected via explicit C++ constructs.",
                )

        # True ambiguity: return UNCERTAIN with all clean candidates
        sorted_candidates = sorted(list(clean_langs), key=lambda l: l.value)
        return LanguageDetectionResult(
            language=Language.UNKNOWN,
            status=DetectionStatus.UNCERTAIN,
            confidence=round(1.0 / len(clean_langs), 2),
            candidate_languages=sorted_candidates,
            details=(
                f"Syntax parsed cleanly under multiple grammars: "
                f"{', '.join(l.value for l in sorted_candidates)}. "
                "Ambiguity is genuine; cannot determine language with certainty."
            ),
        )

    def _handle_malformed_code(
        self,
        source_code: str,
        error_parses: Dict[Language, Tuple[ParsedSyntaxTree, int]],
    ) -> LanguageDetectionResult:
        """Conservatively handles source code that produces errors across all parsers."""
        return LanguageDetectionResult(
            language=Language.UNKNOWN,
            status=DetectionStatus.UNCERTAIN,
            confidence=0.0,
            candidate_languages=[],
            details="Source code contains syntax errors across all supported grammars; cannot determine language with certainty.",
        )
