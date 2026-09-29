from __future__ import annotations
import re
from typing import List, Optional, Set
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import NodeType, Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree, SyntaxNode

STRING_LITERAL_TYPES = {
    "string",
    "string_literal",
    "template_string",
    "raw_string_literal",
    "interpreted_string_literal",
}

ASSIGNMENT_TYPES = {
    "augmented_assignment",
    "assignment",
    "assignment_expression",
    "assignment_statement",
}


class StringConcatInLoopRule(FindingRule):
    """Rule observing string concatenation / accumulation patterns inside loop bodies."""

    rule_id = "string-concat-in-loop"
    category = FindingCategory.STRING_CONCATENATION_IN_LOOP
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []

        # Find all loop structural nodes
        loops = outline.find_by_type(NodeType.LOOP)
        if not loops:
            return findings

        # Step 1: Discover variables initialized to string literals prior to loops
        string_vars = self._discover_string_variables(tree)

        # Step 2: Inspect syntax nodes inside each loop
        for loop in loops:
            for node in tree.root.walk():
                if node.type in ASSIGNMENT_TYPES and loop.range.contains_range(node.range):
                    finding = self._check_assignment(node, loop, string_vars, len(findings) + 1)
                    if finding:
                        findings.append(finding)

        return findings

    def _discover_string_variables(self, tree: ParsedSyntaxTree) -> Set[str]:
        string_vars: Set[str] = set()

        for node in tree.root.walk():
            # Check Python / Go / C / JS variable assignments initialized with string literals
            # Pattern: var_name = "..."
            if node.type in {"assignment", "variable_declarator", "short_var_declaration", "let_declaration"}:
                has_str_lit = any(c.type in STRING_LITERAL_TYPES for c in node.walk())
                if has_str_lit:
                    # Find identifier on LHS
                    for child in node.children:
                        if child.type in {"identifier", "variable_name", "pattern"}:
                            string_vars.add(child.text.strip())
                            break
                        if child.field_name in {"name", "left"}:
                            string_vars.add(child.text.strip())
                            break

        return string_vars

    def _check_assignment(
        self,
        node: SyntaxNode,
        loop: StructuralNode,
        known_string_vars: Set[str],
        counter: int,
    ) -> Optional[StructuralFinding]:
        node_text = node.text.strip()

        # Check for augmented assignment (+=)
        is_augmented = "+=" in node_text
        # Check for var = var + ... or var = ... + var
        is_addition_assignment = False
        target_var = ""

        # Extract LHS identifier if possible
        lhs_node = node.child_by_field_name("left")
        if not lhs_node and node.children:
            lhs_node = node.children[0]

        if lhs_node:
            target_var = lhs_node.text.strip()

        # Check if RHS has addition containing target_var
        if "=" in node_text and not is_augmented and target_var:
            rhs_text = node_text.split("=", 1)[1]
            if "+" in rhs_text and re.search(rf"\b{re.escape(target_var)}\b", rhs_text):
                is_addition_assignment = True

        if not (is_augmented or is_addition_assignment):
            return None

        # Check if there is strong string evidence:
        # 1. Contains a string literal in this assignment
        has_string_literal = any(c.type in STRING_LITERAL_TYPES for c in node.walk())
        # 2. Variable was initialized as a string
        is_known_string = target_var in known_string_vars if target_var else False
        # 3. Explicit call to str() or .toString() on RHS
        has_str_call = bool(re.search(r"\b(str|toString)\b", node_text))

        if not (has_string_literal or is_known_string or has_str_call):
            # Avoid false positives for numeric increments like total += x
            return None

        var_label = f"variable '{target_var}'" if target_var else "variable"
        return StructuralFinding(
            id=f"finding_string_concat_{counter}",
            rule_id=self.rule_id,
            category=self.category,
            severity=self.default_severity,
            message=f"String concatenation observed inside loop body on {var_label}.",
            range=node.range,
            node_id=node.id,
            observation_detail=(
                f"{var_label.capitalize()} is accumulated inside the loop at lines "
                f"{loop.start_line}-{loop.end_line}. Repeated string concatenation in loops "
                f"creates intermediate allocations."
            ),
        )
