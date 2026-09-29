from __future__ import annotations
from typing import Any, Dict, List, Optional
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import CodeRange, DetectionStatus, Language, SourceLocation
from opticode.models.context import ModelContextPayload
from opticode.models.findings import StructuralFinding
from opticode.models.localization import ResolvedTarget


class ContextGenerator:
    """Generates structured, minimal, and deterministic ModelContextPayload objects.

    IMPORTANT:
    - Does NOT call any AI provider (OpenAI, Claude, Gemini, etc.).
    - Does NOT format vendor-specific prompts.
    - Strictly preserves the boundary between editable regions and broader relevant context.
    - Deterministic output suitable for Backend A model orchestration.
    """

    def generate(
        self,
        source_code: str,
        language: Language,
        detection_status: DetectionStatus,
        user_instruction: Optional[str] = None,
        resolved_target: Optional[ResolvedTarget] = None,
        outline: Optional[StructuralOutline] = None,
        findings: Optional[List[StructuralFinding]] = None,
        errors: Optional[List[str]] = None,
    ) -> ModelContextPayload:
        """Constructs a deterministic ModelContextPayload from code analysis outputs."""
        source_lines = source_code.splitlines(keepends=True)
        total_lines = max(1, len(source_lines))
        last_line_len = len(source_lines[-1]) if source_lines else 1

        full_file_range = CodeRange(
            start=SourceLocation(line=1, column=1, byte_offset=0),
            end=SourceLocation(line=total_lines, column=max(1, last_line_len), byte_offset=len(source_code)),
        )

        all_findings = findings or []
        outline_summary = self._format_outline(outline)

        # 1. Handle Unsupported Language
        if detection_status == DetectionStatus.UNSUPPORTED:
            metadata: Dict[str, Any] = {
                "target_type": "unsupported",
                "supported": False,
                "is_strict_block": False,
                "errors": list(errors or ["Unsupported programming language."]),
            }
            return ModelContextPayload(
                language=language.value if isinstance(language, Language) else str(language),
                detection_status=detection_status.value,
                target_range=full_file_range,
                editable_range=full_file_range,
                relevant_source=source_code,
                user_instruction=user_instruction,
                enclosing_symbol=None,
                structural_outline=[],
                findings=[],
                localization_metadata=metadata,
            )

        # 2. Handle Ambiguous Target
        if resolved_target is not None and resolved_target.ambiguity_detected:
            metadata = {
                "target_type": "ambiguous",
                "ambiguity_detected": True,
                "candidate_descriptions": list(resolved_target.candidate_descriptions),
                "is_strict_block": False,
                "errors": list(resolved_target.errors),
            }
            return ModelContextPayload(
                language=language.value,
                detection_status=detection_status.value,
                target_range=resolved_target.requested_range,
                editable_range=resolved_target.editable_region.range,
                relevant_source="",
                user_instruction=user_instruction,
                enclosing_symbol=None,
                structural_outline=outline_summary,
                findings=[],
                localization_metadata=metadata,
            )

        # 3. Handle Full-File Analysis (no specific target provided)
        if resolved_target is None:
            metadata = {
                "target_type": "full_file",
                "is_strict_block": False,
            }
            return ModelContextPayload(
                language=language.value,
                detection_status=detection_status.value,
                target_range=full_file_range,
                editable_range=full_file_range,
                relevant_source=source_code,
                user_instruction=user_instruction,
                enclosing_symbol=None,
                structural_outline=outline_summary,
                findings=all_findings,
                localization_metadata=metadata,
            )

        # 4. Handle Localized Target (LINE, RANGE, BLOCK, SYMBOL, CONTEXTUAL)
        target_range = resolved_target.requested_range
        editable_range = resolved_target.editable_region.range

        # Extract relevant source code:
        # Prefer the pre-extracted surrounding_code if provided by actual_relevant_context,
        # otherwise slice the relevant_context range from source_code.
        rel_context_range = resolved_target.actual_relevant_context.range
        if resolved_target.actual_relevant_context.surrounding_code:
            relevant_source = resolved_target.actual_relevant_context.surrounding_code
        else:
            relevant_source = self._extract_source_slice(source_lines, rel_context_range)

        # Filter findings to those overlapping with or inside the relevant context range
        relevant_findings = [
            f for f in all_findings
            if rel_context_range.contains_range(f.range) or rel_context_range.overlaps(f.range)
        ]

        metadata = {
            "target_type": resolved_target.actual_relevant_context.enclosing_node_type or "localized",
            "is_strict_block": resolved_target.editable_region.is_strict_block,
            "description": resolved_target.editable_region.description,
            "ambiguity_detected": False,
            "target_node_ids": list(resolved_target.target_node_ids),
            "relevant_context_range": rel_context_range.to_dict(),
            "enclosing_node_type": resolved_target.actual_relevant_context.enclosing_node_type,
            "success": resolved_target.success,
        }

        return ModelContextPayload(
            language=language.value,
            detection_status=detection_status.value,
            target_range=target_range,
            editable_range=editable_range,
            relevant_source=relevant_source,
            user_instruction=user_instruction,
            enclosing_symbol=resolved_target.actual_relevant_context.enclosing_symbol,
            structural_outline=outline_summary,
            findings=relevant_findings,
            localization_metadata=metadata,
        )

    def _extract_source_slice(self, lines: List[str], code_range: CodeRange) -> str:
        """Extracts the exact line slice from source lines for a given range (1-indexed)."""
        start_idx = max(0, code_range.start.line - 1)
        end_idx = min(len(lines), code_range.end.line)
        return "".join(lines[start_idx:end_idx])

    def _format_outline(self, outline: Optional[StructuralOutline]) -> List[Dict[str, Any]]:
        """Formats a compact, deterministic summary of the structural outline."""
        if not outline or not outline.root_nodes:
            return []

        def summarize_node(node: StructuralNode) -> Dict[str, Any]:
            children_summary = [
                summarize_node(c) for c in node.children
                if c.name or c.node_type.value in {"function", "method", "class", "interface"}
            ]
            # Sort children deterministically by start line and column
            children_summary.sort(key=lambda c: (c["range"]["start"]["line"], c["range"]["start"]["column"]))
            return {
                "id": node.id,
                "type": node.node_type.value,
                "name": node.name,
                "range": node.range.to_dict(),
                "children": children_summary,
            }

        summary = [summarize_node(r) for r in outline.root_nodes]
        summary.sort(key=lambda r: (r["range"]["start"]["line"], r["range"]["start"]["column"]))
        return summary


def generate_model_context(
    source_code: str,
    language: Language,
    detection_status: DetectionStatus,
    user_instruction: Optional[str] = None,
    resolved_target: Optional[ResolvedTarget] = None,
    outline: Optional[StructuralOutline] = None,
    findings: Optional[List[StructuralFinding]] = None,
    errors: Optional[List[str]] = None,
) -> ModelContextPayload:
    """Convenience function to generate a ModelContextPayload."""
    generator = ContextGenerator()
    return generator.generate(
        source_code=source_code,
        language=language,
        detection_status=detection_status,
        user_instruction=user_instruction,
        resolved_target=resolved_target,
        outline=outline,
        findings=findings,
        errors=errors,
    )
