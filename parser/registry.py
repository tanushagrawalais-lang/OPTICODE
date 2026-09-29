from __future__ import annotations
from typing import Dict, List, Optional
import tree_sitter

from opticode.models.common import Language
from opticode.parser.exceptions import GrammarLoadError, UnsupportedLanguageError


class GrammarRegistry:
    """Registry responsible for loading, mapping, and caching Tree-sitter grammars

    for all supported programming languages.
    """

    SUPPORTED_LANGUAGES = {
        Language.PYTHON,
        Language.JAVA,
        Language.C,
        Language.CPP,
        Language.JAVASCRIPT,
        Language.TYPESCRIPT,
        Language.GO,
        Language.RUST,
    }

    def __init__(self) -> None:
        self._grammar_cache: Dict[Language, tree_sitter.Language] = {}

    def is_supported(self, language: Language) -> bool:
        """Checks if a language is supported by the grammar registry."""
        return language in self.SUPPORTED_LANGUAGES

    def get_supported_languages(self) -> List[Language]:
        """Returns a list of all currently supported languages."""
        return sorted(list(self.SUPPORTED_LANGUAGES), key=lambda l: l.value)

    def get_grammar(self, language: Language) -> tree_sitter.Language:
        """Retrieves or loads the Tree-sitter Language instance for the given language.

        Raises:
            UnsupportedLanguageError: If the language is not among the supported 8.
            GrammarLoadError: If loading the grammar fails.
        """
        if not self.is_supported(language):
            raise UnsupportedLanguageError(language.value if isinstance(language, Language) else str(language))

        if language in self._grammar_cache:
            return self._grammar_cache[language]

        ts_lang = self._load_grammar(language)
        self._grammar_cache[language] = ts_lang
        return ts_lang

    def _load_grammar(self, language: Language) -> tree_sitter.Language:
        try:
            if language == Language.PYTHON:
                import tree_sitter_python as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.JAVA:
                import tree_sitter_java as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.C:
                import tree_sitter_c as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.CPP:
                import tree_sitter_cpp as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.JAVASCRIPT:
                import tree_sitter_javascript as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.TYPESCRIPT:
                import tree_sitter_typescript as mod
                return tree_sitter.Language(mod.language_typescript())
            elif language == Language.GO:
                import tree_sitter_go as mod
                return tree_sitter.Language(mod.language())
            elif language == Language.RUST:
                import tree_sitter_rust as mod
                return tree_sitter.Language(mod.language())
            else:
                raise UnsupportedLanguageError(language.value)
        except UnsupportedLanguageError:
            raise
        except Exception as e:
            raise GrammarLoadError(language.value, str(e)) from e
