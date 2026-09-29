from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from opticode.models.common import CodeRange, Language
from opticode.models.localization import EditableRegion, LocalizationTarget


@dataclass
class ValidationRequest:
    """Request to validate source code syntax and scope conformance."""
    source_code: str
    language: Language
    expected_scope: Optional[CodeRange] = None
    original_source: Optional[str] = None

    @property
    def target_range(self) -> Optional[CodeRange]:
        """Alias for expected_scope."""
        return self.expected_scope

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_code": self.source_code,
            "language": self.language.value,
            "expected_scope": self.expected_scope.to_dict() if self.expected_scope else None,
            "target_range": self.expected_scope.to_dict() if self.expected_scope else None,
            "original_source": self.original_source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRequest":
        scope_data = data.get("expected_scope") or data.get("target_range")
        return cls(
            source_code=data["source_code"],
            language=Language(data["language"]),
            expected_scope=CodeRange.from_dict(scope_data) if scope_data else None,
            original_source=data.get("original_source"),
        )


@dataclass
class ValidationResult:
    """Processing-level validation outcome.

    Explicitly disclaims runtime/semantic correctness without execution.
    """
    is_valid_syntax: bool
    parse_errors: List[str] = field(default_factory=list)
    scope_violations: List[str] = field(default_factory=list)
    language_matched: bool = True
    error_node_count: int = 0
    missing_node_count: int = 0
    disclaimer: str = (
        "Syntax validity indicates grammar compliance only. "
        "Parsing does not verify runtime correctness, logical correctness, "
        "algorithmic correctness, performance improvement, or security."
    )

    @property
    def is_valid(self) -> bool:
        """True if syntax is valid, language matched, and no scope violations occurred."""
        return self.is_valid_syntax and self.language_matched and len(self.scope_violations) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "is_valid_syntax": self.is_valid_syntax,
            "parse_errors": list(self.parse_errors),
            "scope_violations": list(self.scope_violations),
            "language_matched": self.language_matched,
            "error_node_count": self.error_node_count,
            "missing_node_count": self.missing_node_count,
            "disclaimer": self.disclaimer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        return cls(
            is_valid_syntax=bool(data["is_valid_syntax"]),
            parse_errors=list(data.get("parse_errors", [])),
            scope_violations=list(data.get("scope_violations", [])),
            language_matched=bool(data.get("language_matched", True)),
            error_node_count=int(data.get("error_node_count", 0)),
            missing_node_count=int(data.get("missing_node_count", 0)),
            disclaimer=data.get("disclaimer", cls.disclaimer),
        )


@dataclass
class PostprocessRequest:
    """Request to extract, validate, and check scope of raw AI model output."""
    original_source: str
    raw_ai_output: str
    language: Language
    editable_region: Optional[EditableRegion] = None
    expected_target: Optional[LocalizationTarget] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_source": self.original_source,
            "raw_ai_output": self.raw_ai_output,
            "language": self.language.value,
            "editable_region": self.editable_region.to_dict() if self.editable_region else None,
            "expected_target": self.expected_target.to_dict() if self.expected_target else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostprocessRequest":
        return cls(
            original_source=data["original_source"],
            raw_ai_output=data["raw_ai_output"],
            language=Language(data["language"]),
            editable_region=EditableRegion.from_dict(data["editable_region"]) if data.get("editable_region") else None,
            expected_target=LocalizationTarget.from_dict(data["expected_target"]) if data.get("expected_target") else None,
        )


@dataclass
class PostprocessResult:
    """Outcome of processing AI output."""
    success: bool
    extracted_code: Optional[str] = None
    full_modified_source: Optional[str] = None
    modified_range: Optional[CodeRange] = None
    diff: Optional[str] = None
    is_within_scope: bool = True
    validation: Optional[ValidationResult] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "extracted_code": self.extracted_code,
            "full_modified_source": self.full_modified_source,
            "modified_range": self.modified_range.to_dict() if self.modified_range else None,
            "diff": self.diff,
            "is_within_scope": self.is_within_scope,
            "validation": self.validation.to_dict() if self.validation else None,
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostprocessResult":
        return cls(
            success=bool(data["success"]),
            extracted_code=data.get("extracted_code"),
            full_modified_source=data.get("full_modified_source"),
            modified_range=CodeRange.from_dict(data["modified_range"]) if data.get("modified_range") else None,
            diff=data.get("diff"),
            is_within_scope=bool(data.get("is_within_scope", True)),
            validation=ValidationResult.from_dict(data["validation"]) if data.get("validation") else None,
            errors=list(data.get("errors", [])),
        )
