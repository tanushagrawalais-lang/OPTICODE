"""Structural findings and conservative observations subsystem for OptiCode Analyzer."""

from opticode.findings.analyzer import (
    DEFAULT_RULES,
    FindingsAnalyzer,
    analyze_findings,
)
from opticode.findings.rules.base import FindingRule
from opticode.findings.rules.deep_nesting import DeepNestingRule
from opticode.findings.rules.empty_handlers import EmptyExceptionHandlerRule
from opticode.findings.rules.nested_loops import NestedLoopsRule
from opticode.findings.rules.repeated_branches import RepeatedBranchConditionRule
from opticode.findings.rules.repeated_calls import RepeatedCallsInLoopRule
from opticode.findings.rules.repeated_computation import RepeatedComputationRule
from opticode.findings.rules.string_concat import StringConcatInLoopRule

__all__ = [
    "DEFAULT_RULES",
    "DeepNestingRule",
    "EmptyExceptionHandlerRule",
    "FindingRule",
    "FindingsAnalyzer",
    "NestedLoopsRule",
    "RepeatedBranchConditionRule",
    "RepeatedCallsInLoopRule",
    "RepeatedComputationRule",
    "StringConcatInLoopRule",
    "analyze_findings",
]
