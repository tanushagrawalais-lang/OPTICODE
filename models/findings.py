from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional
from opticode.models.common import CodeRange, Severity


class FindingCategory(str, Enum):
    NESTED_LOOP = "nested_loop"
    REPEATED_CALL_IN_LOOP = "repeated_call_in_loop"
    REPEATED_COMPUTATION = "repeated_computation"
    DEEP_NESTING = "deep_nesting"
    EMPTY_EXCEPTION_HANDLER = "empty_exception_handler"
    STRING_CONCATENATION_IN_LOOP = "string_concatenation_in_loop"
    REPEATED_BRANCH_CONDITION = "repeated_branch_condition"
    OTHER_OBSERVATION = "other_observation"


@dataclass
class StructuralFinding:
    """An objective, structural observation derived directly from the AST.

    Does not make unverified runtime performance claims.
    """
    id: str
    rule_id: str
    category: FindingCategory
    severity: Severity
    message: str
    range: CodeRange
    node_id: Optional[str] = None
    observation_detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "range": self.range.to_dict(),
            "node_id": self.node_id,
            "observation_detail": self.observation_detail,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuralFinding":
        return cls(
            id=data["id"],
            rule_id=data["rule_id"],
            category=FindingCategory(data["category"]),
            severity=Severity(data["severity"]),
            message=data["message"],
            range=CodeRange.from_dict(data["range"]),
            node_id=data.get("node_id"),
            observation_detail=data.get("observation_detail"),
        )
