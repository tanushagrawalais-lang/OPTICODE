from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from opticode.models.localization import EditableRegion


@dataclass
class ScopeCheckResult:
    """Outcome of checking whether modifications stayed strictly within editable boundaries."""
    is_within_scope: bool
    violations: List[str]
    out_of_scope_lines: List[int]


class ScopeGuard:
    """Strictly enforces that modifications do not touch lines outside the designated editable region."""

    def check_scope(
        self,
        modified_lines: List[int],
        editable_region: Optional[EditableRegion],
    ) -> ScopeCheckResult:
        """Verifies that all modified original lines are inside editable_region."""
        if editable_region is None:
            # Full file is allowed
            return ScopeCheckResult(
                is_within_scope=True,
                violations=[],
                out_of_scope_lines=[],
            )

        start_line = editable_region.range.start.line
        end_line = editable_region.range.end.line

        out_of_scope: List[int] = [
            line for line in modified_lines
            if line < start_line or line > end_line
        ]

        if not out_of_scope:
            return ScopeCheckResult(
                is_within_scope=True,
                violations=[],
                out_of_scope_lines=[],
            )

        # Group contiguous out-of-scope lines for clear error reporting
        line_ranges = self._group_contiguous(out_of_scope)
        range_strs = [
            f"lines {r[0]}-{r[1]}" if r[0] != r[1] else f"line {r[0]}"
            for r in line_ranges
        ]

        violations = [
            f"Modification outside allowed editable region: {', '.join(range_strs)} "
            f"were modified, but allowed editable region is lines {start_line}-{end_line}."
        ]

        return ScopeCheckResult(
            is_within_scope=False,
            violations=violations,
            out_of_scope_lines=out_of_scope,
        )

    def _group_contiguous(self, numbers: List[int]) -> List[tuple[int, int]]:
        """Groups a sorted list of numbers into contiguous (start, end) tuples."""
        if not numbers:
            return []

        ranges: List[tuple[int, int]] = []
        range_start = numbers[0]
        prev = numbers[0]

        for n in numbers[1:]:
            if n == prev + 1:
                prev = n
            else:
                ranges.append((range_start, prev))
                range_start = n
                prev = n

        ranges.append((range_start, prev))
        return ranges
