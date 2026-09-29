from __future__ import annotations
from typing import List, Optional
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import NodeType, Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree

CONTROL_FLOW_TYPES = {NodeType.LOOP, NodeType.CONDITIONAL}
SCOPE_RESET_TYPES = {NodeType.FUNCTION, NodeType.METHOD}


class DeepNestingRule(FindingRule):
    """Rule observing deeply nested control structures (depth >= threshold)."""

    rule_id = "deep-nesting"
    category = FindingCategory.DEEP_NESTING
    default_severity = Severity.OBSERVATION

    def __init__(self, threshold: int = 4) -> None:
        self.threshold = threshold

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []

        def inspect_node(node: StructuralNode, current_depth: int) -> None:
            if node.node_type in SCOPE_RESET_TYPES:
                # Function/method boundaries reset control nesting depth
                for child in node.children:
                    inspect_node(child, 0)
                return

            if node.node_type in CONTROL_FLOW_TYPES:
                new_depth = current_depth + 1
                if new_depth >= self.threshold:
                    findings.append(
                        StructuralFinding(
                            id=f"finding_deep_nesting_{len(findings) + 1}",
                            rule_id=self.rule_id,
                            category=self.category,
                            severity=self.default_severity,
                            message=(
                                f"Deep control-flow nesting detected at depth {new_depth} "
                                f"(threshold: {self.threshold})."
                            ),
                            range=node.range,
                            node_id=node.id,
                            observation_detail=(
                                f"Control structure '{node.node_type.value}' at lines "
                                f"{node.start_line}-{node.end_line} is nested {new_depth} levels "
                                f"deep within enclosing control blocks."
                            ),
                        )
                    )
                for child in node.children:
                    inspect_node(child, new_depth)
            else:
                for child in node.children:
                    inspect_node(child, current_depth)

        for root in outline.root_nodes:
            inspect_node(root, 0)

        return findings
