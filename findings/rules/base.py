from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from opticode.models.analysis import StructuralOutline
from opticode.models.common import Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.parser.types import ParsedSyntaxTree


class FindingRule(ABC):
    """Abstract base class for conservative structural observation rules."""

    rule_id: str
    category: FindingCategory
    default_severity: Severity = Severity.OBSERVATION

    @abstractmethod
    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        """Inspects the syntax tree and structural outline and returns structural observations."""
        pass
