from __future__ import annotations
from typing import List, Optional
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import CodeRange, NodeType, SourceLocation
from opticode.models.localization import (
    ActualRelevantContext,
    EditableRegion,
    LocalizationTarget,
    ResolvedTarget,
    TargetType,
)
from opticode.localization.context_builder import build_relevant_context
from opticode.localization.exceptions import (
    AmbiguousSymbolError,
    InvalidRangeError,
    OutOfRangeError,
    SymbolNotFoundError,
)


class TargetResolver:
    """Resolves caller targeting intent (line, range, block, symbol, contextual)

    against the normalized structural tree.
    """

    def resolve(
        self,
        source_code: str,
        outline: StructuralOutline,
        target: LocalizationTarget,
        strict: bool = False,
    ) -> ResolvedTarget:
        """Resolves a LocalizationTarget against the source code and structural outline.

        Args:
            source_code: The raw source code string.
            outline: The normalized StructuralOutline of the source code.
            target: The user's targeting request.
            strict: If True, raises exceptions on invalid/out-of-range/ambiguous targets;
                    if False, returns ResolvedTarget with success=False and errors populated.

        Returns:
            ResolvedTarget containing RequestedRange, EditableRegion, ActualRelevantContext,
            and metadata.
        """
        source_lines = source_code.splitlines()
        total_lines = len(source_lines) if source_lines else 1

        try:
            if target.target_type == TargetType.LINE:
                return self._resolve_line(target, source_lines, total_lines, outline)
            elif target.target_type == TargetType.RANGE:
                return self._resolve_range(target, source_lines, total_lines, outline)
            elif target.target_type == TargetType.BLOCK:
                return self._resolve_block(target, source_code, source_lines, total_lines, outline)
            elif target.target_type == TargetType.SYMBOL:
                return self._resolve_symbol(target, source_lines, outline)
            elif target.target_type == TargetType.CONTEXTUAL:
                return self._resolve_contextual(target, source_lines, total_lines, outline)
            else:
                raise InvalidRangeError(f"Unsupported target type '{target.target_type}'.")
        except (InvalidRangeError, OutOfRangeError, SymbolNotFoundError, AmbiguousSymbolError) as e:
            if strict:
                raise
            candidates = e.candidates if isinstance(e, AmbiguousSymbolError) else []
            return self._build_error_result(str(e), target, source_lines, ambiguity=isinstance(e, AmbiguousSymbolError), candidates=candidates)

    def _resolve_line(
        self,
        target: LocalizationTarget,
        source_lines: List[str],
        total_lines: int,
        outline: StructuralOutline,
    ) -> ResolvedTarget:
        if target.line is None:
            raise InvalidRangeError("Line target requires 'line' field.")

        line = target.line
        if line < 1:
            raise InvalidRangeError(f"Line number must be >= 1, got {line}.")
        if line > total_lines:
            raise OutOfRangeError(f"Target line {line} exceeds total file lines ({total_lines}).")

        line_len = len(source_lines[line - 1]) if line <= len(source_lines) else 0
        requested_range = CodeRange(
            start=SourceLocation(line=line, column=1),
            end=SourceLocation(line=line, column=max(1, line_len + 1)),
        )

        editable_region = EditableRegion(
            range=requested_range,
            is_strict_block=True,
            description=f"Strict single line {line}",
        )

        context = build_relevant_context(source_lines, outline, requested_range)
        enclosing_ids = self._find_containing_node_ids(outline, requested_range)

        return ResolvedTarget(
            requested_range=requested_range,
            editable_region=editable_region,
            actual_relevant_context=context,
            target_node_ids=enclosing_ids,
            ambiguity_detected=False,
            candidate_descriptions=[],
            success=True,
            errors=[],
        )

    def _resolve_range(
        self,
        target: LocalizationTarget,
        source_lines: List[str],
        total_lines: int,
        outline: StructuralOutline,
    ) -> ResolvedTarget:
        if target.start_line is None or target.end_line is None:
            raise InvalidRangeError("Range target requires both 'start_line' and 'end_line'.")

        start = target.start_line
        end = target.end_line

        if start < 1:
            raise InvalidRangeError(f"start_line must be >= 1, got {start}.")
        if start > end:
            raise InvalidRangeError(f"start_line ({start}) cannot be greater than end_line ({end}).")
        if start > total_lines:
            raise OutOfRangeError(f"Requested start line {start} exceeds total file lines ({total_lines}).")

        # Documented rule 8: normalize end line if it exceeds total lines
        effective_end = min(end, total_lines)

        end_len = len(source_lines[effective_end - 1]) if effective_end <= len(source_lines) else 0
        requested_range = CodeRange(
            start=SourceLocation(line=start, column=1),
            end=SourceLocation(line=effective_end, column=max(1, end_len + 1)),
        )

        editable_region = EditableRegion(
            range=requested_range,
            is_strict_block=True,
            description=f"Strict line range {start}-{effective_end}",
        )

        context = build_relevant_context(source_lines, outline, requested_range)
        enclosing_ids = self._find_containing_node_ids(outline, requested_range)

        return ResolvedTarget(
            requested_range=requested_range,
            editable_region=editable_region,
            actual_relevant_context=context,
            target_node_ids=enclosing_ids,
            ambiguity_detected=False,
            candidate_descriptions=[],
            success=True,
            errors=[],
        )

    def _resolve_block(
        self,
        target: LocalizationTarget,
        source_code: str,
        source_lines: List[str],
        total_lines: int,
        outline: StructuralOutline,
    ) -> ResolvedTarget:
        # If line range is supplied, use it
        if target.start_line is not None and target.end_line is not None:
            return self._resolve_range(target, source_lines, total_lines, outline)

        # If selected_text is supplied without lines, locate it
        if target.selected_text:
            text = target.selected_text
            count = source_code.count(text)
            if count == 0:
                raise InvalidRangeError(f"Selected text snippet was not found in the source code.")
            if count > 1:
                raise AmbiguousSymbolError(
                    f"Selected snippet matches {count} different locations. Provide line numbers.",
                    [f"Occurrence {i+1}" for i in range(count)],
                )

            idx = source_code.index(text)
            start_line = source_code[:idx].count("\n") + 1
            lines_in_text = text.count("\n")
            end_line = start_line + lines_in_text

            return self._resolve_range(
                LocalizationTarget(target_type=TargetType.RANGE, start_line=start_line, end_line=end_line),
                source_lines,
                total_lines,
                outline,
            )

        raise InvalidRangeError("Selected block target requires start_line/end_line or selected_text.")

    def _resolve_symbol(
        self,
        target: LocalizationTarget,
        source_lines: List[str],
        outline: StructuralOutline,
    ) -> ResolvedTarget:
        if not target.symbol_name or not target.symbol_name.strip():
            raise InvalidRangeError("Symbol target requires a non-empty 'symbol_name'.")

        name = target.symbol_name.strip()
        matches = outline.find_by_name(name)

        if not matches:
            raise SymbolNotFoundError(name)

        if len(matches) > 1:
            candidate_descs = [
                f"{m.node_type.value} '{m.name}' at lines {m.start_line}-{m.end_line}"
                for m in matches
            ]
            raise AmbiguousSymbolError(name, candidate_descs)

        target_node = matches[0]
        requested_range = target_node.range

        editable_region = EditableRegion(
            range=requested_range,
            is_strict_block=False,
            description=f"Scope of {target_node.node_type.value} '{target_node.name}'",
        )

        context = build_relevant_context(source_lines, outline, requested_range, target_node=target_node)

        return ResolvedTarget(
            requested_range=requested_range,
            editable_region=editable_region,
            actual_relevant_context=context,
            target_node_ids=[target_node.id],
            ambiguity_detected=False,
            candidate_descriptions=[],
            success=True,
            errors=[],
        )

    def _resolve_contextual(
        self,
        target: LocalizationTarget,
        source_lines: List[str],
        total_lines: int,
        outline: StructuralOutline,
    ) -> ResolvedTarget:
        line = target.line or target.start_line
        if line is None:
            raise InvalidRangeError("Contextual target requires a cursor line.")
        if line < 1 or line > total_lines:
            raise OutOfRangeError(f"Contextual cursor line {line} is outside file (1-{total_lines}).")

        # Find innermost function, method, or class at cursor line
        cursor_loc = SourceLocation(line=line, column=1)
        cursor_range = CodeRange(start=cursor_loc, end=cursor_loc)

        candidates: List[StructuralNode] = []
        for root in outline.root_nodes:
            for node in root.walk():
                if node.range.contains_line(line) and node.node_type in (
                    NodeType.FUNCTION,
                    NodeType.METHOD,
                    NodeType.CLASS,
                ):
                    candidates.append(node)

        if candidates:
            # Pick the innermost candidate
            best = min(candidates, key=lambda n: n.end_line - n.start_line)
            requested_range = best.range
            editable_region = EditableRegion(
                range=requested_range,
                is_strict_block=False,
                description=f"Contextual scope of {best.node_type.value} '{best.name}'",
            )
            context = build_relevant_context(source_lines, outline, requested_range, target_node=best)
            return ResolvedTarget(
                requested_range=requested_range,
                editable_region=editable_region,
                actual_relevant_context=context,
                target_node_ids=[best.id],
                ambiguity_detected=False,
                candidate_descriptions=[],
                success=True,
                errors=[],
            )

        # Fallback to single line if not inside function/class
        return self._resolve_line(
            LocalizationTarget(target_type=TargetType.LINE, line=line),
            source_lines,
            total_lines,
            outline,
        )

    def _find_containing_node_ids(self, outline: StructuralOutline, target_range: CodeRange) -> List[str]:
        node_ids: List[str] = []
        for root in outline.root_nodes:
            for node in root.walk():
                if node.range.contains_range(target_range) or target_range.contains_range(node.range):
                    node_ids.append(node.id)
        return node_ids

    def _build_error_result(
        self,
        error_msg: str,
        target: LocalizationTarget,
        source_lines: List[str],
        ambiguity: bool = False,
        candidates: Optional[List[str]] = None,
    ) -> ResolvedTarget:
        dummy_loc = SourceLocation(line=target.line or target.start_line or 1, column=1)
        dummy_range = CodeRange(start=dummy_loc, end=dummy_loc)
        return ResolvedTarget(
            requested_range=dummy_range,
            editable_region=EditableRegion(range=dummy_range, is_strict_block=True),
            actual_relevant_context=ActualRelevantContext(range=dummy_range, surrounding_code=""),
            target_node_ids=[],
            ambiguity_detected=ambiguity,
            candidate_descriptions=candidates if candidates is not None else ([error_msg] if ambiguity else []),
            success=False,
            errors=[error_msg],
        )
