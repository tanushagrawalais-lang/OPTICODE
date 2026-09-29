from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from opticode.models.common import CodeRange
from opticode.models.findings import StructuralFinding


@dataclass
class ModelContextPayload:
    """Structured, minimal context payload designed specifically for consumption
    by the AI orchestration layer (Backend Developer / Model orchestrator).
    """
    language: str
    target_range: CodeRange
    editable_range: CodeRange
    relevant_source: str
    detection_status: Optional[str] = None
    user_instruction: Optional[str] = None
    enclosing_symbol: Optional[str] = None
    structural_outline: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[StructuralFinding] = field(default_factory=list)
    localization_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def requested_range(self) -> CodeRange:
        """Alias for target_range for clarity in localization contexts."""
        return self.target_range

    @property
    def editable_region(self) -> CodeRange:
        """Alias for editable_range for clarity in localization contexts."""
        return self.editable_range

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "detection_status": self.detection_status,
            "target_range": self.target_range.to_dict(),
            "requested_range": self.target_range.to_dict(),
            "editable_range": self.editable_range.to_dict(),
            "editable_region": self.editable_range.to_dict(),
            "relevant_source": self.relevant_source,
            "user_instruction": self.user_instruction,
            "enclosing_symbol": self.enclosing_symbol,
            "structural_outline": list(self.structural_outline),
            "findings": [f.to_dict() for f in self.findings],
            "localization_metadata": dict(self.localization_metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelContextPayload":
        target_dict = data.get("target_range") or data.get("requested_range")
        if not target_dict:
            raise KeyError("Neither 'target_range' nor 'requested_range' found in payload data.")
        editable_dict = data.get("editable_range") or data.get("editable_region")
        if not editable_dict:
            raise KeyError("Neither 'editable_range' nor 'editable_region' found in payload data.")

        return cls(
            language=data["language"],
            target_range=CodeRange.from_dict(target_dict),
            editable_range=CodeRange.from_dict(editable_dict),
            relevant_source=data["relevant_source"],
            detection_status=data.get("detection_status"),
            user_instruction=data.get("user_instruction"),
            enclosing_symbol=data.get("enclosing_symbol"),
            structural_outline=list(data.get("structural_outline", [])),
            findings=[StructuralFinding.from_dict(f) for f in data.get("findings", [])],
            localization_metadata=dict(data.get("localization_metadata", {})),
        )
