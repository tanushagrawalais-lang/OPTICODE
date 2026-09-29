from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional
from opticode.models.common import CodeRange, Language, SourceLocation


@dataclass
class ParseError:
    """Represents a syntax error or missing token detected in the AST."""
    message: str
    range: CodeRange
    error_type: str  # "ERROR" or "MISSING"
    missing_token: Optional[str] = None
    surrounding_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "range": self.range.to_dict(),
            "error_type": self.error_type,
            "missing_token": self.missing_token,
            "surrounding_text": self.surrounding_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParseError":
        return cls(
            message=data["message"],
            range=CodeRange.from_dict(data["range"]),
            error_type=data["error_type"],
            missing_token=data.get("missing_token"),
            surrounding_text=data.get("surrounding_text"),
        )


@dataclass
class SyntaxNode:
    """Safe, decoupled representation of a Concrete Syntax Tree node.

    Encapsulates all AST properties without exposing raw Tree-sitter pointers.
    """
    id: str
    type: str
    range: CodeRange
    text: str
    is_named: bool
    is_error: bool
    is_missing: bool
    has_error: bool
    field_name: Optional[str] = None
    children: List["SyntaxNode"] = field(default_factory=list)

    def child_by_field_name(self, name: str) -> Optional["SyntaxNode"]:
        for child in self.children:
            if child.field_name == name:
                return child
        return None

    def find_all_by_type(self, node_type: str) -> List["SyntaxNode"]:
        matches: List[SyntaxNode] = []
        for node in self.walk():
            if node.type == node_type:
                matches.append(node)
        return matches

    def find_first_by_type(self, node_type: str) -> Optional["SyntaxNode"]:
        for node in self.walk():
            if node.type == node_type:
                return node
        return None

    def walk(self) -> Iterator["SyntaxNode"]:
        """Pre-order depth-first traversal of the node and its descendants."""
        yield self
        for child in self.children:
            yield from child.walk()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "range": self.range.to_dict(),
            "text": self.text,
            "is_named": self.is_named,
            "is_error": self.is_error,
            "is_missing": self.is_missing,
            "has_error": self.has_error,
            "field_name": self.field_name,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyntaxNode":
        return cls(
            id=data["id"],
            type=data["type"],
            range=CodeRange.from_dict(data["range"]),
            text=data["text"],
            is_named=bool(data["is_named"]),
            is_error=bool(data["is_error"]),
            is_missing=bool(data["is_missing"]),
            has_error=bool(data["has_error"]),
            field_name=data.get("field_name"),
            children=[cls.from_dict(c) for c in data.get("children", [])],
        )


@dataclass
class ParsedSyntaxTree:
    """Safe abstraction of a parsed syntax tree for a source code unit.

    Provides high-level queries and error inspection without exposing
    underlying parser implementation details.
    """
    language: Language
    source_code: str
    root: SyntaxNode
    has_errors: bool
    errors: List[ParseError] = field(default_factory=list)

    def find_by_type(self, node_type: str) -> List[SyntaxNode]:
        """Finds all nodes in the tree matching the specified type."""
        return self.root.find_all_by_type(node_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language.value,
            "source_code": self.source_code,
            "root": self.root.to_dict(),
            "has_errors": self.has_errors,
            "errors": [e.to_dict() for e in self.errors],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParsedSyntaxTree":
        return cls(
            language=Language(data["language"]),
            source_code=data["source_code"],
            root=SyntaxNode.from_dict(data["root"]),
            has_errors=bool(data["has_errors"]),
            errors=[ParseError.from_dict(e) for e in data.get("errors", [])],
        )
