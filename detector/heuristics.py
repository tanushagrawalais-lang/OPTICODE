from __future__ import annotations
import re
from typing import Optional
from opticode.parser.types import ParsedSyntaxTree

# TypeScript-exclusive AST node types produced by tree-sitter-typescript
TS_EXCLUSIVE_NODE_TYPES = {
    "interface_declaration",
    "type_alias_declaration",
    "enum_declaration",
    "type_annotation",
    "as_expression",
    "type_arguments",
    "type_parameters",
    "ambient_declaration",
    "implements_clause",
    "predefined_type",
    "non_null_expression",
    "type_assertion",
    "index_signature",
    "mapped_type_clause",
}

# C++-exclusive AST node types produced by tree-sitter-cpp
CPP_EXCLUSIVE_NODE_TYPES = {
    "class_specifier",
    "template_declaration",
    "namespace_definition",
    "using_declaration",
    "try_statement",
    "catch_clause",
    "throw_expression",
    "new_expression",
    "delete_expression",
    "scoped_identifier",
    "access_specifier",
    "user_defined_literal",
    "lambda_expression",
}

# Regular expressions for explicit syntactic markers
TS_TOKEN_PATTERNS = [
    re.compile(r"\binterface\s+[A-Z]\w*"),
    re.compile(r"\btype\s+[A-Z]\w*\s*="),
    re.compile(r"\benum\s+[A-Z]\w*"),
    re.compile(r":\s*(string|number|boolean|any|void|unknown|never|Record<|Array<|Promise<)\b"),
    re.compile(r"\bas\s+const\b"),
]

CPP_TOKEN_PATTERNS = [
    re.compile(r"\bstd::"),
    re.compile(r"\b(nullptr|constexpr)\b"),
    re.compile(r"\bclass\s+\w+\s*(\{|\:)"),
    re.compile(r"\btemplate\s*<"),
    re.compile(r"\bnamespace\s+\w+"),
    re.compile(r"\busing\s+namespace\b"),
    re.compile(r"#include\s*<(iostream|vector|string|memory|algorithm|map|set|chrono|thread)>"),
]

PYTHON_PATTERNS = [
    re.compile(r"^\s*def\s+\w+\s*\([^)]*\)\s*:", re.MULTILINE),
    re.compile(r"^\s*class\s+\w+(\([^)]*\))?\s*:", re.MULTILINE),
    re.compile(r"\b(elif|import|from\s+\w+\s+import)\b"),
    re.compile(r"__name__\s*==\s*['\"]__main__['\"]"),
]

GO_PATTERNS = [
    re.compile(r"^\s*package\s+\w+", re.MULTILINE),
    re.compile(r"\bfunc\s+(\([^)]*\)\s*)?\w+\s*\([^)]*\)"),
    re.compile(r":="),
    re.compile(r"\b(chan|go\s+\w+|select\s*\{)\b"),
]

RUST_PATTERNS = [
    re.compile(r"\bfn\s+\w+\s*\([^)]*\)"),
    re.compile(r"\blet\s+(mut\s+)?\w+"),
    re.compile(r"\bimpl(\s+.*?)?\s+(for|\{)"),
    re.compile(r"\b(match\s+\w+|println!|vec!|format!)\b"),
    re.compile(r"->\s*([A-Z]\w*|i32|i64|u32|u64|usize|bool|String|&str)\b"),
]

JAVA_PATTERNS = [
    re.compile(r"\bpublic\s+(static\s+)?(void|class|interface|enum)\b"),
    re.compile(r"\bSystem\.(out|err)\.print"),
    re.compile(r"^\s*package\s+[a-zA-Z_][\w.]*;\s*$", re.MULTILINE),
    re.compile(r"^\s*import\s+[a-zA-Z_][\w.]*;\s*$", re.MULTILINE),
]


def has_typescript_constructs(code: str, tree: Optional[ParsedSyntaxTree] = None) -> bool:
    """Checks whether the code contains explicit TypeScript constructs."""
    if tree and not tree.has_errors:
        for node in tree.root.walk():
            if node.type in TS_EXCLUSIVE_NODE_TYPES:
                return True

    return any(pattern.search(code) for pattern in TS_TOKEN_PATTERNS)


def has_cpp_constructs(code: str, tree: Optional[ParsedSyntaxTree] = None) -> bool:
    """Checks whether the code contains explicit C++ constructs."""
    if tree and not tree.has_errors:
        for node in tree.root.walk():
            if node.type in CPP_EXCLUSIVE_NODE_TYPES:
                return True

    return any(pattern.search(code) for pattern in CPP_TOKEN_PATTERNS)


def matches_any_pattern(code: str, patterns: list[re.Pattern]) -> bool:
    """Helper to check if any regex pattern in a list matches the code."""
    return any(pattern.search(code) for pattern in patterns)
