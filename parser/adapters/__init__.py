from __future__ import annotations
from typing import Dict
from opticode.models.common import Language
from opticode.models.analysis import StructuralOutline
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.adapters.c import CAdapter
from opticode.parser.adapters.cpp import CppAdapter
from opticode.parser.adapters.go import GoAdapter
from opticode.parser.adapters.java import JavaAdapter
from opticode.parser.adapters.javascript import JavascriptAdapter
from opticode.parser.adapters.python import PythonAdapter
from opticode.parser.adapters.rust import RustAdapter
from opticode.parser.adapters.typescript import TypescriptAdapter
from opticode.parser.exceptions import UnsupportedLanguageError
from opticode.parser.types import ParsedSyntaxTree

_ADAPTERS: Dict[Language, LanguageAdapter] = {
    Language.PYTHON: PythonAdapter(),
    Language.JAVA: JavaAdapter(),
    Language.C: CAdapter(),
    Language.CPP: CppAdapter(),
    Language.JAVASCRIPT: JavascriptAdapter(),
    Language.TYPESCRIPT: TypescriptAdapter(),
    Language.GO: GoAdapter(),
    Language.RUST: RustAdapter(),
}


def get_adapter(language: Language) -> LanguageAdapter:
    """Returns the LanguageAdapter corresponding to the specified language."""
    if language not in _ADAPTERS:
        raise UnsupportedLanguageError(language.value if isinstance(language, Language) else str(language))
    return _ADAPTERS[language]


def extract_structure(tree: ParsedSyntaxTree) -> StructuralOutline:
    """Convenience function to extract normalized StructuralOutline from a ParsedSyntaxTree."""
    adapter = get_adapter(tree.language)
    return adapter.extract(tree)


__all__ = [
    "LanguageAdapter",
    "PythonAdapter",
    "JavaAdapter",
    "CAdapter",
    "CppAdapter",
    "JavascriptAdapter",
    "TypescriptAdapter",
    "GoAdapter",
    "RustAdapter",
    "get_adapter",
    "extract_structure",
]
