from __future__ import annotations
from typing import List, Optional
from opticode.models.common import Language
from opticode.models.localization import EditableRegion
from opticode.models.postprocess import (
    PostprocessRequest,
    PostprocessResult,
    ValidationResult,
)
from opticode.postprocessor.diff import DiffDetector, DiffResult
from opticode.postprocessor.extractor import CodeExtractor
from opticode.postprocessor.scope_guard import ScopeGuard
from opticode.validator.syntax import SyntaxValidator


class Postprocessor:
    """Coordinates AI output postprocessing, code extraction, syntax validation,

    and strict editable-region scope enforcement.

    IMPORTANT:
    - Never executes or sandboxes code.
    - Never claims runtime correctness.
    - Rejects any modification outside the designated editable region.
    """

    def __init__(
        self,
        extractor: Optional[CodeExtractor] = None,
        diff_detector: Optional[DiffDetector] = None,
        scope_guard: Optional[ScopeGuard] = None,
        syntax_validator: Optional[SyntaxValidator] = None,
    ) -> None:
        self.extractor = extractor or CodeExtractor()
        self.diff_detector = diff_detector or DiffDetector()
        self.scope_guard = scope_guard or ScopeGuard()
        self.syntax_validator = syntax_validator or SyntaxValidator()

    def process(self, request: PostprocessRequest) -> PostprocessResult:
        """Processes raw AI output against original source and editable boundary."""
        errors: List[str] = []

        # Step 1: Code extraction from raw AI output
        extracted_code = self.extractor.extract(request.raw_ai_output, request.language)
        if extracted_code is None or not extracted_code.strip():
            return PostprocessResult(
                success=False,
                extracted_code=None,
                full_modified_source=None,
                modified_range=None,
                diff=None,
                is_within_scope=True,
                validation=None,
                errors=["No code found in AI output."],
            )

        # Step 2: Full source reconstruction
        full_modified_source = self._reconstruct_full_source(
            original_source=request.original_source,
            extracted_code=extracted_code,
            editable_region=request.editable_region,
        )

        # Step 3: Diff generation and modified-line detection
        diff_res: DiffResult = self.diff_detector.compare(
            request.original_source,
            full_modified_source,
        )

        # Step 4: Editable-region scope enforcement
        scope_res = self.scope_guard.check_scope(
            modified_lines=diff_res.modified_original_lines,
            editable_region=request.editable_region,
        )

        if not scope_res.is_within_scope:
            errors.extend(scope_res.violations)

        # Step 5: Syntax validation of candidate code
        validation_res: ValidationResult = self.syntax_validator.validate_code(
            source_code=full_modified_source,
            language=request.language,
            expected_scope=request.editable_region.range if request.editable_region else None,
        )
        validation_res.scope_violations = list(scope_res.violations)

        if not validation_res.is_valid_syntax:
            errors.extend([f"Syntax error: {err}" for err in validation_res.parse_errors])

        is_success = scope_res.is_within_scope and validation_res.is_valid_syntax and len(errors) == 0

        return PostprocessResult(
            success=is_success,
            extracted_code=extracted_code,
            full_modified_source=full_modified_source,
            modified_range=diff_res.modified_range,
            diff=diff_res.unified_diff,
            is_within_scope=scope_res.is_within_scope,
            validation=validation_res,
            errors=errors,
        )

    def _reconstruct_full_source(
        self,
        original_source: str,
        extracted_code: str,
        editable_region: Optional[EditableRegion],
    ) -> str:
        """Determines whether extracted code is full-file or localized, and reconstructs full source."""
        if editable_region is None:
            return extracted_code

        orig_norm = original_source.replace("\r\n", "\n")
        cand_norm = extracted_code.replace("\r\n", "\n")
        orig_lines = orig_norm.splitlines(keepends=True)

        total_orig_lines = len(orig_lines)
        start_line = editable_region.range.start.line
        end_line = editable_region.range.end.line

        # Check if editable region covers the full file
        if start_line <= 1 and end_line >= total_orig_lines:
            return cand_norm

        # Check if extracted code is a full-file candidate
        if self._is_full_file_candidate(orig_lines, cand_norm, start_line, end_line):
            return cand_norm

        # Otherwise, extracted code is a localized snippet to be spliced into the editable region
        prefix = orig_lines[: max(0, start_line - 1)]
        suffix = orig_lines[end_line:]

        cand_lines = cand_norm.splitlines(keepends=True)
        if cand_lines and not cand_lines[-1].endswith("\n"):
            cand_lines[-1] += "\n"

        return "".join(prefix + cand_lines + suffix)

    def _is_full_file_candidate(
        self,
        orig_lines: List[str],
        cand_norm: str,
        start_line: int,
        end_line: int,
    ) -> bool:
        """Determines if candidate code contains context outside the editable region."""
        cand_lines = cand_norm.splitlines(keepends=True)

        # If the candidate line count is close to or exceeds original lines
        if len(cand_lines) >= len(orig_lines) * 0.7:
            # Check if lines before the editable region appear at the start of candidate
            if start_line > 1 and orig_lines:
                first_orig_line = orig_lines[0].strip()
                if first_orig_line and any(first_orig_line == cl.strip() for cl in cand_lines[:5]):
                    return True

            # Check if lines after the editable region appear near the end of candidate
            if end_line < len(orig_lines):
                last_orig_line = orig_lines[-1].strip()
                if last_orig_line and any(last_orig_line == cl.strip() for cl in cand_lines[-5:]):
                    return True

        return False
