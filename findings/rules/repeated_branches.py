from __future__ import annotations
import re
from typing import List, Optional, Set, Tuple
from opticode.models.analysis import StructuralOutline
from opticode.models.common import Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree, SyntaxNode

IF_NODE_TYPES = {"if_statement", "if_expression"}
ELIF_NODE_TYPES = {"elif_clause"}


class RepeatedBranchConditionRule(FindingRule):
    """Rule observing identical condition expressions repeated in an if-elif / else-if chain."""

    rule_id = "repeated-branch-condition"
    category = FindingCategory.REPEATED_BRANCH_CONDITION
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []
        chained_if_ids: Set[str] = set()

        # Step 1: Pre-identify all `if` nodes that are chained as alternatives of an outer if
        for node in tree.root.walk():
            if node.type in IF_NODE_TYPES:
                # Check alternative child
                alt = node.child_by_field_name("alternative")
                if alt:
                    if alt.type in IF_NODE_TYPES:
                        chained_if_ids.add(alt.id)
                    else:
                        # e.g. else_clause containing if_statement
                        for c in alt.children:
                            if c.type in IF_NODE_TYPES:
                                chained_if_ids.add(c.id)
                # Also check direct else_clause children in languages where alternative isn't named
                for c in node.children:
                    if c.type == "else_clause":
                        for gc in c.children:
                            if gc.type in IF_NODE_TYPES:
                                chained_if_ids.add(gc.id)

        # Step 2: For every ROOT if node, collect all branches in the chain
        for node in tree.root.walk():
            if node.type in IF_NODE_TYPES and node.id not in chained_if_ids:
                branches = self._collect_chain_branches(node)
                if len(branches) >= 2:
                    seen_conditions: dict[str, SyntaxNode] = {}
                    for cond_text, cond_node in branches:
                        if cond_text in seen_conditions:
                            first_cond = seen_conditions[cond_text]
                            findings.append(
                                StructuralFinding(
                                    id=f"finding_repeated_branch_{len(findings) + 1}",
                                    rule_id=self.rule_id,
                                    category=self.category,
                                    severity=self.default_severity,
                                    message=(
                                        f"Repeated branch condition '{cond_text}' detected "
                                        f"in conditional chain."
                                    ),
                                    range=cond_node.range,
                                    node_id=cond_node.id,
                                    observation_detail=(
                                        f"Condition '{cond_text}' on line {cond_node.range.start.line} "
                                        f"is identical to earlier branch condition on line "
                                        f"{first_cond.range.start.line} in the same conditional chain."
                                    ),
                                )
                            )
                        else:
                            seen_conditions[cond_text] = cond_node

        return findings

    def _collect_chain_branches(self, if_node: SyntaxNode) -> List[Tuple[str, SyntaxNode]]:
        """Collects (normalized_condition_text, condition_syntax_node) for the chain."""
        branches: List[Tuple[str, SyntaxNode]] = []

        curr: Optional[SyntaxNode] = if_node
        while curr is not None:
            cond = self._extract_condition_node(curr)
            if cond:
                norm_text = self._normalize_condition(cond.text)
                if norm_text:
                    branches.append((norm_text, cond))

            # In Python, elif clauses are direct children of the if_statement
            for child in curr.children:
                if child.type in ELIF_NODE_TYPES:
                    elif_cond = self._extract_condition_node(child)
                    if elif_cond:
                        norm_elif = self._normalize_condition(elif_cond.text)
                        if norm_elif:
                            branches.append((norm_elif, elif_cond))

            # In C/JS/Java/Rust/Go, else if is an alternative containing an if
            next_if: Optional[SyntaxNode] = None
            alt = curr.child_by_field_name("alternative")
            if alt:
                if alt.type in IF_NODE_TYPES:
                    next_if = alt
                else:
                    for c in alt.children:
                        if c.type in IF_NODE_TYPES:
                            next_if = c
                            break

            if not next_if:
                for c in curr.children:
                    if c.type == "else_clause":
                        for gc in c.children:
                            if gc.type in IF_NODE_TYPES:
                                next_if = gc
                                break
                        break

            curr = next_if

        return branches

    def _extract_condition_node(self, node: SyntaxNode) -> Optional[SyntaxNode]:
        """Extracts the syntax node representing the boolean condition of an if or elif."""
        cond = node.child_by_field_name("condition")
        if cond:
            return cond

        # Fallback based on structure
        for child in node.children:
            if child.type in {"parenthesized_expression", "binary_expression", "comparison_operator"}:
                return child
            # In Python, first named child before block
            if child.is_named and child.type not in {"block", "elif_clause", "else_clause"}:
                return child

        return None

    def _normalize_condition(self, text: str) -> str:
        s = re.sub(r"\s+", " ", text.strip())
        if s.startswith("(") and s.endswith(")") and len(s) > 2:
            s = s[1:-1].strip()
        return s
