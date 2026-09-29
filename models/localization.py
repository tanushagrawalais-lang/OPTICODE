from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from opticode.models.common import CodeRange


class TargetType(str, Enum):
    LINE = "line"
    RANGE = "range"
    BLOCK = "block"
    SYMBOL = "symbol"
    CONTEXTUAL = "contextual"


@dataclass
class LocalizationTarget:
    target_type: TargetType
    line: Optional[int] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    symbol_name: Optional[str] = None
    selected_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_type": self.target_type.value,
            "line": self.line,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol_name": self.symbol_name,
            "selected_text": self.selected_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalizationTarget":
        return cls(
            target_type=TargetType(data["target_type"]),
            line=data.get("line"),
            start_line=data.get("start_line"),
            end_line=data.get("end_line"),
            symbol_name=data.get("symbol_name"),
            selected_text=data.get("selected_text"),
        )


@dataclass
class EditableRegion:
    """The strictly restricted region that any modification is allowed to touch.

    Never silently broadened without explicit user intent.
    """
    range: CodeRange
    is_strict_block: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "range": self.range.to_dict(),
            "is_strict_block": self.is_strict_block,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditableRegion":
        return cls(
            range=CodeRange.from_dict(data["range"]),
            is_strict_block=bool(data.get("is_strict_block", False)),
            description=data.get("description"),
        )


@dataclass
class ActualRelevantContext:
    """The enclosing scope (e.g. function, class, file) required by the AI model

    to understand variable definitions, types, and dependencies.
    This context is read-only and does not expand the editable boundary.
    """
    range: CodeRange
    enclosing_symbol: Optional[str] = None
    enclosing_node_type: Optional[str] = None
    surrounding_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "range": self.range.to_dict(),
            "enclosing_symbol": self.enclosing_symbol,
            "enclosing_node_type": self.enclosing_node_type,
            "surrounding_code": self.surrounding_code,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActualRelevantContext":
        return cls(
            range=CodeRange.from_dict(data["range"]),
            enclosing_symbol=data.get("enclosing_symbol"),
            enclosing_node_type=data.get("enclosing_node_type"),
            surrounding_code=data.get("surrounding_code"),
        )


@dataclass
class ResolvedTarget:
    """Resolution of user targeting intent against AST boundaries."""
    requested_range: CodeRange
    editable_region: EditableRegion
    actual_relevant_context: ActualRelevantContext
    target_node_ids: List[str] = field(default_factory=list)
    ambiguity_detected: bool = False
    candidate_descriptions: List[str] = field(default_factory=list)
    success: bool = True
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requested_range": self.requested_range.to_dict(),
            "editable_region": self.editable_region.to_dict(),
            "actual_relevant_context": self.actual_relevant_context.to_dict(),
            "target_node_ids": list(self.target_node_ids),
            "ambiguity_detected": self.ambiguity_detected,
            "candidate_descriptions": list(self.candidate_descriptions),
            "success": self.success,
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResolvedTarget":
        return cls(
            requested_range=CodeRange.from_dict(data["requested_range"]),
            editable_region=EditableRegion.from_dict(data["editable_region"]),
            actual_relevant_context=ActualRelevantContext.from_dict(data["actual_relevant_context"]),
            target_node_ids=list(data.get("target_node_ids", [])),
            ambiguity_detected=bool(data.get("ambiguity_detected", False)),
            candidate_descriptions=list(data.get("candidate_descriptions", [])),
            success=bool(data.get("success", True)),
            errors=list(data.get("errors", [])),
        )
