"""AST parsing and grammar normalization subsystem for OptiCode Analyzer.

Encapsulates Tree-sitter parsers and provides decoupled syntax tree representations.
"""

from typing import Optional
from opticode.models.common import Language
from opticode.parser.adapters import (
    extract_structure,
    get_adapter,
)
from opticode.parser.engine import ParserEngine
from opticode.parser.exceptions import (
    GrammarLoadError,
    ParserError,
    UnsupportedLanguageError,
)
from opticode.parser.registry import GrammarRegistry
from opticode.parser.types import ParsedSyntaxTree, ParseError, SyntaxNode

_default_engine: Optional[ParserEngine] = None


def get_default_parser_engine() -> ParserEngine:
    """Returns the shared default ParserEngine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = ParserEngine()
    return _default_engine


def parse(source_code: str, language: Language) -> ParsedSyntaxTree:
    """Convenience function to parse source code using the default parser engine."""
    return get_default_parser_engine().parse(source_code, language)


__all__ = [
    "ParserEngine",
    "GrammarRegistry",
    "ParsedSyntaxTree",
    "SyntaxNode",
    "ParseError",
    "ParserError",
    "UnsupportedLanguageError",
    "GrammarLoadError",
    "get_default_parser_engine",
    "parse",
    "get_adapter",
    "extract_structure",
]
