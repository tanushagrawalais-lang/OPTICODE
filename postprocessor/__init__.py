"""AI output postprocessing, code extraction, and scope guard subsystem for OptiCode Analyzer."""

from opticode.postprocessor.diff import DiffDetector, DiffResult
from opticode.postprocessor.extractor import CodeExtractor
from opticode.postprocessor.processor import Postprocessor
from opticode.postprocessor.scope_guard import ScopeCheckResult, ScopeGuard

__all__ = [
    "CodeExtractor",
    "DiffDetector",
    "DiffResult",
    "Postprocessor",
    "ScopeCheckResult",
    "ScopeGuard",
]
