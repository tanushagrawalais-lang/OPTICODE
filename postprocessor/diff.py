from __future__ import annotations
import difflib
from dataclasses import dataclass
from typing import List, Optional, Set
from opticode.models.common import CodeRange, SourceLocation


@dataclass
class DiffResult:
    """Detailed comparison between original and candidate source code."""
    modified_original_lines: List[int]
    modified_range: Optional[CodeRange]
    unified_diff: str
    is_identical: bool
    is_whitespace_only: bool


class DiffDetector:
    """Computes line-level diffs, modified lines, and bounding ranges."""

    def compare(self, original_source: str, candidate_source: str) -> DiffResult:
        """Compares original source and candidate source."""
        # Normalize line endings for reliable diffing
        orig_norm = original_source.replace("\r\n", "\n")
        cand_norm = candidate_source.replace("\r\n", "\n")

        if orig_norm == cand_norm or orig_norm.strip() == cand_norm.strip():
            return DiffResult(
                modified_original_lines=[],
                modified_range=None,
                unified_diff="",
                is_identical=True,
                is_whitespace_only=False,
            )

        orig_lines = orig_norm.splitlines(keepends=True)
        cand_lines = cand_norm.splitlines(keepends=True)

        matcher = difflib.SequenceMatcher(None, orig_lines, cand_lines)
        modified_line_numbers: Set[int] = set()
        is_whitespace_only = True

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            # Check if this change is purely whitespace
            chunk_orig = "".join(orig_lines[i1:i2])
            chunk_cand = "".join(cand_lines[j1:j2])
            if chunk_orig.split() != chunk_cand.split():
                is_whitespace_only = False

            if tag in ("replace", "delete"):
                # Lines i1+1 through i2 (1-indexed) were modified or deleted
                for line_num in range(i1 + 1, i2 + 1):
                    modified_line_numbers.add(line_num)
            elif tag == "insert":
                # An insertion after line i1 affects boundary line i1 (or 1 if at beginning)
                affected = i1 if i1 > 0 else 1
                if orig_lines:
                    affected = min(len(orig_lines), affected)
                modified_line_numbers.add(affected)

        sorted_lines = sorted(modified_line_numbers)
        modified_range: Optional[CodeRange] = None

        if sorted_lines:
            min_line = sorted_lines[0]
            max_line = sorted_lines[-1]
            end_line_content = orig_lines[max_line - 1] if max_line <= len(orig_lines) else ""
            end_col = max(1, len(end_line_content.rstrip("\r\n")) + 1)
            modified_range = CodeRange(
                start=SourceLocation(line=min_line, column=1),
                end=SourceLocation(line=max_line, column=end_col),
            )

        unified_diff = "".join(
            difflib.unified_diff(
                orig_lines,
                cand_lines,
                fromfile="original",
                tofile="candidate",
            )
        )

        return DiffResult(
            modified_original_lines=sorted_lines,
            modified_range=modified_range,
            unified_diff=unified_diff,
            is_identical=False,
            is_whitespace_only=is_whitespace_only,
        )
