from __future__ import annotations
import re
from collections import defaultdict
from typing import Dict, List
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import NodeType, Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree, SyntaxNode

BINARY_EXPR_TYPES = {
    "binary_operator",
    "binary_expression",
}

# Trivial index or increment patterns to ignore
TRIVIAL_PATTERN = re.compile(r"^\w+\s*(\+|\-)\s*1$")


class RepeatedComputationRule(FindingRule):
    """Rule observing identical arithmetic/computation expressions evaluated multiple times in the same scope."""

    rule_id = "repeated-computation"
    category = FindingCategory.REPEATED_COMPUTATION
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []
        finding_counter = 0

        # Group binary expressions within each top-level function/method or the whole tree
        subroutines = outline.find_by_type(NodeType.FUNCTION) + outline.find_by_type(NodeType.METHOD)

        if subroutines:
            for sub in subroutines:
                self._check_scope(tree, sub.range, findings, finding_counter)
        else:
            self._check_scope(tree, tree.root.range, findings, finding_counter)

        return findings

    def _check_scope(
        self,
        tree: ParsedSyntaxTree,
        scope_range,
        findings: List[StructuralFinding],
        counter: int,
    ) -> None:
        expr_occurrences: Dict[str, List[SyntaxNode]] = defaultdict(list)

        for node in tree.root.walk():
            if node.type in BINARY_EXPR_TYPES:
                # Check if node is inside this scope
                if scope_range.contains_range(node.range):
                    normalized_text = re.sub(r"\s+", " ", node.text.strip())
                    # Ignore trivial increments like 'i + 1' or 'count - 1'
                    if not TRIVIAL_PATTERN.match(normalized_text) and len(normalized_text) >= 4:
                        expr_occurrences[normalized_text].append(node)

        for expr_text, occurrences in expr_occurrences.items():
            if len(occurrences) >= 2:
                first = occurrences[0]
                lines = [str(o.range.start.line) for o in occurrences]
                findings.append(
                    StructuralFinding(
                        id=f"finding_repeated_comp_{len(findings) + 1}",
                        rule_id=self.rule_id,
                        category=self.category,
                        severity=self.default_severity,
                        message=f"Repeated computation expression '{expr_text}' detected {len(occurrences)} times.",
                        range=first.range,
                        node_id=first.id,
                        observation_detail=f"Identical expression is computed on lines {', '.join(lines)}.",
                    )
                )
