from __future__ import annotations
from typing import List
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import NodeType, Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree


class NestedLoopsRule(FindingRule):
    """Rule observing nested loop structures (loops containing other loops)."""

    rule_id = "nested-loops"
    category = FindingCategory.NESTED_LOOP
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []
        finding_counter = 0

        def inspect_node(node: StructuralNode, current_loop_depth: int, outer_loop: StructuralNode | None) -> None:
            nonlocal finding_counter
            if node.node_type == NodeType.LOOP:
                new_depth = current_loop_depth + 1
                if new_depth >= 2 and outer_loop is not None:
                    finding_counter += 1
                    findings.append(
                        StructuralFinding(
                            id=f"finding_nested_loop_{finding_counter}",
                            rule_id=self.rule_id,
                            category=self.category,
                            severity=self.default_severity,
                            message=f"Nested loop structure detected at nesting depth {new_depth}.",
                            range=node.range,
                            node_id=node.id,
                            observation_detail=(
                                f"Inner loop at lines {node.start_line}-{node.end_line} is nested "
                                f"inside outer loop at lines {outer_loop.start_line}-{outer_loop.end_line}."
                            ),
                        )
                    )
                for child in node.children:
                    inspect_node(child, new_depth, outer_loop or node)
            else:
                for child in node.children:
                    inspect_node(child, current_loop_depth, outer_loop)

        for root in outline.root_nodes:
            inspect_node(root, 0, None)

        return findings
