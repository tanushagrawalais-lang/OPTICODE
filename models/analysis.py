from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from opticode.models.common import CodeRange, DetectionStatus, Language, NodeType
from opticode.models.context import ModelContextPayload
from opticode.models.findings import StructuralFinding
from opticode.models.localization import LocalizationTarget, ResolvedTarget


@dataclass
class StructuralNode:
    """Normalized structural representation of an AST node."""
    id: str
    node_type: NodeType
    range: CodeRange
    name: Optional[str] = None
    parent_id: Optional[str] = None
    children: List["StructuralNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def start_line(self) -> int:
        return self.range.start.line

    @property
    def end_line(self) -> int:
        return self.range.end.line

    @property
    def start_column(self) -> int:
        return self.range.start.column

    @property
    def end_column(self) -> int:
        return self.range.end.column

    def walk(self) -> Any:
        """Pre-order traversal of this node and all descendant structural nodes."""
        yield self
        for child in self.children:
            yield from child.walk()

    def find_all_by_type(self, node_type: NodeType) -> List["StructuralNode"]:
        return [n for n in self.walk() if n.node_type == node_type]

    def find_by_name(self, name: str) -> List["StructuralNode"]:
        return [n for n in self.walk() if n.name == name]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "range": self.range.to_dict(),
            "name": self.name,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuralNode":
        return cls(
            id=data["id"],
            node_type=NodeType(data["node_type"]),
            range=CodeRange.from_dict(data["range"]),
            name=data.get("name"),
            parent_id=data.get("parent_id"),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class StructuralOutline:
    """High-level summary of the source code structure."""
    root_nodes: List[StructuralNode] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    symbol_index: Dict[str, List[CodeRange]] = field(default_factory=dict)

    def find_by_type(self, node_type: NodeType) -> List[StructuralNode]:
        """Finds all structural nodes of the specified type in the outline."""
        matches: List[StructuralNode] = []
        for root in self.root_nodes:
            matches.extend(root.find_all_by_type(node_type))
        return matches

    def find_by_name(self, name: str) -> List[StructuralNode]:
        """Finds all structural nodes matching the given symbol name."""
        matches: List[StructuralNode] = []
        for root in self.root_nodes:
            matches.extend(root.find_by_name(name))
        return matches

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_nodes": [n.to_dict() for n in self.root_nodes],
            "imports": list(self.imports),
            "symbol_index": {
                k: [r.to_dict() for r in v] for k, v in self.symbol_index.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuralOutline":
        return cls(
            root_nodes=[StructuralNode.from_dict(n) for n in data.get("root_nodes", [])],
            imports=list(data.get("imports", [])),
            symbol_index={
                k: [CodeRange.from_dict(r) for r in v]
                for k, v in data.get("symbol_index", {}).items()
            },
        )


@dataclass
class CodeAnalysisInput:
    """Primary input from Core Backend to Analysis Subsystem."""
    source_code: str
    declared_language: Optional[str] = None
    target: Optional[LocalizationTarget] = None
    user_instruction: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_code": self.source_code,
            "declared_language": self.declared_language,
            "target": self.target.to_dict() if self.target else None,
            "user_instruction": self.user_instruction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeAnalysisInput":
        return cls(
            source_code=data["source_code"],
            declared_language=data.get("declared_language"),
            target=LocalizationTarget.from_dict(data["target"]) if data.get("target") else None,
            user_instruction=data.get("user_instruction"),
        )


@dataclass
class AnalysisResult:
    """Consolidated analysis result returned to Core Backend."""
    language: Language
    detection_status: DetectionStatus
    detection_details: str
    parse_success: bool
    outline: Optional[StructuralOutline] = None
    resolved_target: Optional[ResolvedTarget] = None
    findings: List[StructuralFinding] = field(default_factory=list)
    model_context: Optional[ModelContextPayload] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language.value,
            "detection_status": self.detection_status.value,
            "detection_details": self.detection_details,
            "parse_success": self.parse_success,
            "outline": self.outline.to_dict() if self.outline else None,
            "resolved_target": self.resolved_target.to_dict() if self.resolved_target else None,
            "findings": [f.to_dict() for f in self.findings],
            "model_context": self.model_context.to_dict() if self.model_context else None,
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        return cls(
            language=Language(data["language"]),
            detection_status=DetectionStatus(data["detection_status"]),
            detection_details=data["detection_details"],
            parse_success=bool(data["parse_success"]),
            outline=StructuralOutline.from_dict(data["outline"]) if data.get("outline") else None,
            resolved_target=ResolvedTarget.from_dict(data["resolved_target"]) if data.get("resolved_target") else None,
            findings=[StructuralFinding.from_dict(f) for f in data.get("findings", [])],
            model_context=ModelContextPayload.from_dict(data["model_context"]) if data.get("model_context") else None,
            errors=list(data.get("errors", [])),
        )
