from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict


class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, val: str) -> "Language":
        normalized = val.strip().lower()
        alias_map = {
            "py": cls.PYTHON,
            "python": cls.PYTHON,
            "java": cls.JAVA,
            "c": cls.C,
            "cpp": cls.CPP,
            "c++": cls.CPP,
            "js": cls.JAVASCRIPT,
            "javascript": cls.JAVASCRIPT,
            "ts": cls.TYPESCRIPT,
            "typescript": cls.TYPESCRIPT,
            "go": cls.GO,
            "golang": cls.GO,
            "rust": cls.RUST,
            "rs": cls.RUST,
        }
        return alias_map.get(normalized, cls.UNKNOWN)


class DetectionStatus(str, Enum):
    DECLARED = "DECLARED"
    DETECTED = "DETECTED"
    UNCERTAIN = "UNCERTAIN"
    UNSUPPORTED = "UNSUPPORTED"


class NodeType(str, Enum):
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    INTERFACE = "interface"
    LOOP = "loop"
    CONDITIONAL = "conditional"
    IMPORT = "import"
    CALL = "call"
    ASSIGNMENT = "assignment"
    BLOCK = "block"
    OTHER = "other"


class Severity(str, Enum):
    INFO = "info"
    OBSERVATION = "observation"
    WARNING = "warning"


@dataclass
class SourceLocation:
    line: int          # 1-indexed
    column: int        # 1-indexed
    byte_offset: int = 0  # 0-indexed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "byte_offset": self.byte_offset,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceLocation":
        return cls(
            line=int(data["line"]),
            column=int(data["column"]),
            byte_offset=int(data.get("byte_offset", 0)),
        )


@dataclass
class CodeRange:
    start: SourceLocation
    end: SourceLocation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeRange":
        return cls(
            start=SourceLocation.from_dict(data["start"]),
            end=SourceLocation.from_dict(data["end"]),
        )

    def contains_line(self, line: int) -> bool:
        return self.start.line <= line <= self.end.line

    def contains_range(self, other: "CodeRange") -> bool:
        if other.start.line < self.start.line:
            return False
        if other.end.line > self.end.line:
            return False
        if other.start.line == self.start.line and other.start.column < self.start.column:
            return False
        if other.end.line == self.end.line and other.end.column > self.end.column:
            return False
        return True

    def overlaps(self, other: "CodeRange") -> bool:
        if self.end.line < other.start.line or (
            self.end.line == other.start.line and self.end.column < other.start.column
        ):
            return False
        if other.end.line < self.start.line or (
            other.end.line == self.start.line and other.end.column < self.start.column
        ):
            return False
        return True
