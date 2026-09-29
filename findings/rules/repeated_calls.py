from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import NodeType, Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree


class RepeatedCallsInLoopRule(FindingRule):
    """Rule observing identical function/method calls repeated within the same loop body."""

    rule_id = "repeated-calls-in-loop"
    category = FindingCategory.REPEATED_CALL_IN_LOOP
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []
        finding_counter = 0

        # Find all loop nodes
        loops = outline.find_by_type(NodeType.LOOP)

        for loop in loops:
            calls = loop.find_all_by_type(NodeType.CALL)
            call_groups: Dict[str, List[StructuralNode]] = defaultdict(list)

            for call in calls:
                if call.name:
                    call_groups[call.name].append(call)

            for callee_name, occurrences in call_groups.items():
                if len(occurrences) >= 2:
                    finding_counter += 1
                    first_occ = occurrences[0]
                    lines = [str(o.start_line) for o in occurrences]
                    findings.append(
                        StructuralFinding(
                            id=f"finding_repeated_call_{finding_counter}",
                            rule_id=self.rule_id,
                            category=self.category,
                            severity=self.default_severity,
                            message=f"Repeated call to '{callee_name}' detected {len(occurrences)} times within loop body.",
                            range=first_occ.range,
                            node_id=first_occ.id,
                            observation_detail=(
                                f"Call '{callee_name}' appears on lines {', '.join(lines)} inside "
                                f"loop at lines {loop.start_line}-{loop.end_line}."
                            ),
                        )
                    )

        return findings
