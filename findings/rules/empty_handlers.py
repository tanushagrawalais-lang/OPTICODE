from __future__ import annotations
from typing import List, Optional
from opticode.models.analysis import StructuralOutline
from opticode.models.common import Severity
from opticode.models.findings import FindingCategory, StructuralFinding
from opticode.findings.rules.base import FindingRule
from opticode.parser.types import ParsedSyntaxTree, SyntaxNode

EXCEPT_TYPES = {"except_clause"}
CATCH_TYPES = {"catch_clause"}
BLOCK_TYPES = {"block", "statement_block", "compound_statement"}


class EmptyExceptionHandlerRule(FindingRule):
    """Rule observing empty exception handlers (e.g. except: pass, catch (e) {})."""

    rule_id = "empty-exception-handler"
    category = FindingCategory.EMPTY_EXCEPTION_HANDLER
    default_severity = Severity.OBSERVATION

    def check(
        self,
        tree: ParsedSyntaxTree,
        outline: StructuralOutline,
    ) -> List[StructuralFinding]:
        findings: List[StructuralFinding] = []

        for node in tree.root.walk():
            # Check Python except clauses
            if node.type in EXCEPT_TYPES:
                if self._is_empty_python_except(node):
                    findings.append(self._create_finding(node, len(findings) + 1))

            # Check JS/TS/Java/C++ catch clauses
            elif node.type in CATCH_TYPES:
                if self._is_empty_catch_clause(node):
                    findings.append(self._create_finding(node, len(findings) + 1))

            # Check Go empty error handling: if err != nil {}
            elif node.type == "if_statement":
                if self._is_empty_go_error_handler(node):
                    findings.append(self._create_finding(node, len(findings) + 1))

        return findings

    def _is_empty_python_except(self, node: SyntaxNode) -> bool:
        """Determines if a Python except clause contains only pass, ellipsis, or is empty."""
        block = node.child_by_field_name("body")
        if not block:
            for child in node.children:
                if child.type == "block":
                    block = child
                    break

        if not block:
            return True

        named_children = [c for c in block.children if c.is_named and c.type != "comment"]
        if not named_children:
            return True

        # Check if all statements are pass or ellipsis
        for stmt in named_children:
            if stmt.type == "pass_statement":
                continue
            if stmt.type == "expression_statement":
                # Check for ellipsis (...) or docstring
                expr_children = [c for c in stmt.children if c.is_named]
                if all(c.type in {"ellipsis", "string"} for c in expr_children):
                    continue
            # If we encountered any real statement (call, raise, return, assignment), not empty
            return False

        return True

    def _is_empty_catch_clause(self, node: SyntaxNode) -> bool:
        """Determines if a JS/TS/Java/C++ catch clause contains an empty body block."""
        block = node.child_by_field_name("body")
        if not block:
            for child in node.children:
                if child.type in BLOCK_TYPES:
                    block = child
                    break

        if not block:
            return True

        # In C-like ASTs, statements in the block are named children (excluding comments)
        meaningful_statements = [
            c for c in block.children
            if c.is_named and c.type not in {"comment", "line_comment", "block_comment"}
        ]
        return len(meaningful_statements) == 0

    def _is_empty_go_error_handler(self, node: SyntaxNode) -> bool:
        """Determines if a Go if err != nil {} block is empty."""
        cond_text = ""
        cond = node.child_by_field_name("condition")
        if cond:
            cond_text = cond.text
        else:
            for child in node.children:
                if "err" in child.text and "!=" in child.text:
                    cond_text = child.text
                    break

        if "err" in cond_text and "!=" in cond_text and "nil" in cond_text:
            # Check body block
            consequence = node.child_by_field_name("consequence")
            if not consequence:
                for child in node.children:
                    if child.type == "block":
                        consequence = child
                        break
            if consequence:
                statements = [
                    c for c in consequence.children
                    if c.is_named and c.type not in {"comment"}
                ]
                return len(statements) == 0

        return False

    def _create_finding(self, node: SyntaxNode, counter: int) -> StructuralFinding:
        return StructuralFinding(
            id=f"finding_empty_handler_{counter}",
            rule_id=self.rule_id,
            category=self.category,
            severity=self.default_severity,
            message="Empty exception handler detected.",
            range=node.range,
            node_id=node.id,
            observation_detail=(
                f"Exception or error handling block at lines {node.range.start.line}-"
                f"{node.range.end.line} contains no executable handling, logging, or re-raising statements."
            ),
        )
