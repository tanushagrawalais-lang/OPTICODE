from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from opticode.models.common import DetectionStatus, Language


@dataclass
class LanguageDetectionResult:
    """Consolidated outcome of the language detection subsystem."""
    language: Language
    status: DetectionStatus
    confidence: float
    candidate_languages: List[Language] = field(default_factory=list)
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language.value,
            "status": self.status.value,
            "confidence": self.confidence,
            "candidate_languages": [l.value for l in self.candidate_languages],
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LanguageDetectionResult":
        return cls(
            language=Language(data["language"]),
            status=DetectionStatus(data["status"]),
            confidence=float(data["confidence"]),
            candidate_languages=[Language(l) for l in data.get("candidate_languages", [])],
            details=data.get("details", ""),
        )
