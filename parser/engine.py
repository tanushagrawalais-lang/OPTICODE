from __future__ import annotations
from typing import Dict, List, Optional
import tree_sitter

from opticode.models.common import CodeRange, Language, SourceLocation
from opticode.parser.exceptions import UnsupportedLanguageError
from opticode.parser.registry import GrammarRegistry
from opticode.parser.types import ParsedSyntaxTree, ParseError, SyntaxNode


class ParserEngine:
    """Core parser engine wrapping Tree-sitter.

    Manages grammar bindings, creates parsers, converts raw CSTs into decoupled
    SyntaxNode trees, and identifies ERROR and MISSING nodes without exposing
    raw Tree-sitter objects to external subsystems.
    """

    def __init__(self, registry: Optional[GrammarRegistry] = None) -> None:
        self.registry = registry or GrammarRegistry()
        self._parser_cache: Dict[Language, tree_sitter.Parser] = {}

    def _get_parser(self, language: Language) -> tree_sitter.Parser:
        if language in self._parser_cache:
            return self._parser_cache[language]

        ts_lang = self.registry.get_grammar(language)
        parser = tree_sitter.Parser(ts_lang)
        self._parser_cache[language] = parser
        return parser

    def parse(self, source_code: str, language: Language) -> ParsedSyntaxTree:
        """Parses source code in the given language into a ParsedSyntaxTree.

        Args:
            source_code: The raw source code string.
            language: Target programming language.

        Returns:
            ParsedSyntaxTree containing decoupled SyntaxNode root and any detected syntax errors.

        Raises:
            UnsupportedLanguageError: If the specified language is not supported.
        """
        parser = self._get_parser(language)

        # Convert to UTF-8 bytes for Tree-sitter
        source_bytes = source_code.encode("utf-8", errors="replace")
        ts_tree = parser.parse(source_bytes)

        # Recursively build decoupled SyntaxNode tree and collect errors
        errors: List[ParseError] = []
        root_node = self._build_syntax_node(
            ts_tree.root_node,
            source_lines=source_code.splitlines(),
            field_name=None,
            node_counter=[0],
            errors=errors,
        )

        has_errors = ts_tree.root_node.has_error or len(errors) > 0

        return ParsedSyntaxTree(
            language=language,
            source_code=source_code,
            root=root_node,
            has_errors=has_errors,
            errors=errors,
        )

    def _build_syntax_node(
        self,
        node: tree_sitter.Node,
        source_lines: List[str],
        field_name: Optional[str],
        node_counter: List[int],
        errors: List[ParseError],
    ) -> SyntaxNode:
        node_counter[0] += 1
        node_id = f"{node.type}_{node_counter[0]}"

        # Tree-sitter points are 0-indexed (row, column).
        # OptiCode SourceLocations are 1-indexed (line, column).
        start_loc = SourceLocation(
            line=node.start_point.row + 1,
            column=node.start_point.column + 1,
            byte_offset=node.start_byte,
        )
        end_loc = SourceLocation(
            line=node.end_point.row + 1,
            column=node.end_point.column + 1,
            byte_offset=node.end_byte,
        )
        node_range = CodeRange(start=start_loc, end=end_loc)

        text = node.text.decode("utf-8", errors="replace") if node.text else ""

        is_error = node.is_error or node.type == "ERROR"
        is_missing = node.is_missing

        # Detect error and missing nodes for diagnostics
        if is_missing:
            line_idx = node.start_point.row
            surrounding = source_lines[line_idx] if 0 <= line_idx < len(source_lines) else None
            errors.append(
                ParseError(
                    message=f"Missing expected token '{node.type}'",
                    range=node_range,
                    error_type="MISSING",
                    missing_token=node.type,
                    surrounding_text=surrounding,
                )
            )
        elif is_error:
            line_idx = node.start_point.row
            surrounding = source_lines[line_idx] if 0 <= line_idx < len(source_lines) else None
            errors.append(
                ParseError(
                    message=f"Syntax error near '{text[:50]}'" if text else "Syntax error",
                    range=node_range,
                    error_type="ERROR",
                    missing_token=None,
                    surrounding_text=surrounding,
                )
            )

        # Recursively process children
        children: List[SyntaxNode] = []
        for i, child in enumerate(node.children):
            child_field = node.field_name_for_child(i)
            children.append(
                self._build_syntax_node(
                    child,
                    source_lines=source_lines,
                    field_name=child_field,
                    node_counter=node_counter,
                    errors=errors,
                )
            )

        return SyntaxNode(
            id=node_id,
            type=node.type,
            range=node_range,
            text=text,
            is_named=node.is_named,
            is_error=is_error,
            is_missing=is_missing,
            has_error=node.has_error,
            field_name=field_name,
            children=children,
        )
