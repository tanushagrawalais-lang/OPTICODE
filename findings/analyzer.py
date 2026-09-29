from __future__ import annotations
from typing import List, Optional, Sequence
from opticode.models.analysis import StructuralOutline
from opticode.models.findings import StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.findings.rules.nested_loops import NestedLoopsRule
from opticode.findings.rules.repeated_calls import RepeatedCallsInLoopRule
from opticode.findings.rules.repeated_computation import RepeatedComputationRule
from opticode.findings.rules.deep_nesting import DeepNestingRule
from opticode.findings.rules.repeated_branches import RepeatedBranchConditionRule
from opticode.findings.rules.string_concat import StringConcatInLoopRule
from opticode.findings.rules.empty_handlers import EmptyExceptionHandlerRule
from opticode.parser.types import ParsedSyntaxTree

DEFAULT_RULES = (
    NestedLoopsRule,
    RepeatedCallsInLoopRule,
    RepeatedComputationRule,
    DeepNestingRule,
    RepeatedBranchConditionRule,
    StringConcatInLoopRule,
    EmptyExceptionHandlerRule,
)


class FindingsAnalyzer:
    """Coordinates structural observation rules to generate conservative code findings.

    IMPORTANT:
    Findings are strictly AST-level structural observations, NOT guaranteed performance issues.
    Never outputs unverified runtime claims, benchmarks, or percentage promises.
    """

    def __init__(self, rules: Optional[Sequence[FindingRule]] = None) -> None:
        if rules is None:
            self.rules: List[FindingRule] = [rule_cls() for rule_cls in DEFAULT_RULES]
        else:
            self.rules = list(rules)

    def register_rule(self, rule: FindingRule) -> None:
        """Registers an additional finding rule."""
        self.rules.append(rule)

    def analyze(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        """Runs all configured structural rules and returns sorted, deterministic findings."""
        findings: List[StructuralFinding] = []
        for rule in self.rules:
            rule_findings = rule.check(tree, outline)
            findings.extend(rule_findings)

        # Sort findings deterministically by start line, start column, rule_id, and id
        findings.sort(
            key=lambda f: (
                f.range.start.line,
                f.range.start.column,
                f.rule_id,
                f.id,
            )
        )
        return findings


def analyze_findings(
    tree: ParsedSyntaxTree,
    outline: StructuralOutline,
    rules: Optional[Sequence[FindingRule]] = None,
) -> List[StructuralFinding]:
    """Convenience function to analyze a syntax tree and structural outline."""
    analyzer = FindingsAnalyzer(rules=rules)
    return analyzer.analyze(tree, outline)
