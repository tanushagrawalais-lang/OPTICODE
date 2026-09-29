from __future__ import annotations
from typing import List, Optional, Tuple
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import CodeRange, NodeType, SourceLocation
from opticode.models.localization import ActualRelevantContext


def find_enclosing_structural_node(
    outline: StructuralOutline,
    target_range: CodeRange,
    prefer_subroutine: bool = True,
) -> Optional[StructuralNode]:
    """Finds the most relevant enclosing structural node (innermost function, method, or class)

    that completely encompasses the target range.
    """
    candidates: List[StructuralNode] = []

    def check_node(node: StructuralNode) -> None:
        if node.range.contains_range(target_range):
            candidates.append(node)
            for child in node.children:
                check_node(child)

    for root in outline.root_nodes:
        check_node(root)

    if not candidates:
        return None

    # If prefer_subroutine is True, search for the innermost FUNCTION or METHOD first
    if prefer_subroutine:
        subroutines = [c for c in candidates if c.node_type in (NodeType.FUNCTION, NodeType.METHOD)]
        if subroutines:
            # Innermost subroutine is the deepest in the tree (smallest range span)
            return min(subroutines, key=lambda n: n.end_line - n.start_line)

    # Otherwise return the deepest/innermost enclosing candidate
    return min(candidates, key=lambda n: n.end_line - n.start_line)


def extract_surrounding_code(
    source_lines: List[str],
    start_line: int,
    end_line: int,
) -> str:
    """Extracts a slice of source code lines (1-indexed, inclusive)."""
    start_idx = max(0, start_line - 1)
    end_idx = min(len(source_lines), end_line)
    return "\n".join(source_lines[start_idx:end_idx])


def build_relevant_context(
    source_lines: List[str],
    outline: StructuralOutline,
    target_range: CodeRange,
    target_node: Optional[StructuralNode] = None,
) -> ActualRelevantContext:
    """Constructs the read-only ActualRelevantContext for a target range."""
    # Find enclosing function/method or class
    enclosing = find_enclosing_structural_node(outline, target_range, prefer_subroutine=True)

    # If the target node itself is already the function/method, check for an enclosing class
    if target_node and target_node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
        # Look for parent class if available
        if target_node.parent_id:
            parent_class = _find_node_by_id(outline, target_node.parent_id)
            if parent_class and parent_class.node_type == NodeType.CLASS:
                enclosing = parent_class

    if enclosing is not None:
        code_slice = extract_surrounding_code(source_lines, enclosing.start_line, enclosing.end_line)
        return ActualRelevantContext(
            range=enclosing.range,
            enclosing_symbol=enclosing.name,
            enclosing_node_type=enclosing.node_type.value,
            surrounding_code=code_slice,
        )

    # Fallback to the target range itself or file boundary
    start_line = max(1, target_range.start.line - 2)
    end_line = min(len(source_lines), target_range.end.line + 2)
    fallback_range = CodeRange(
        start=SourceLocation(line=start_line, column=1),
        end=SourceLocation(line=end_line, column=len(source_lines[end_line - 1]) + 1 if source_lines else 1),
    )
    code_slice = extract_surrounding_code(source_lines, start_line, end_line)
    return ActualRelevantContext(
        range=fallback_range,
        enclosing_symbol=None,
        enclosing_node_type=None,
        surrounding_code=code_slice,
    )


def _find_node_by_id(outline: StructuralOutline, node_id: str) -> Optional[StructuralNode]:
    for root in outline.root_nodes:
        for node in root.walk():
            if node.id == node_id:
                return node
    return None
