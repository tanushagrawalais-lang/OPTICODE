"""Target localization and scope boundary subsystem for OptiCode Analyzer.

Converts caller targeting requests into RequestedRange, EditableRegion, and ActualRelevantContext.
"""

from typing import Optional
from opticode.localization.exceptions import (
    AmbiguousSymbolError,
    InvalidRangeError,
    LocalizationError,
    OutOfRangeError,
    SymbolNotFoundError,
)
from opticode.localization.resolver import TargetResolver
from opticode.models.analysis import StructuralOutline
from opticode.models.localization import LocalizationTarget, ResolvedTarget

_default_resolver: Optional[TargetResolver] = None


def get_default_target_resolver() -> TargetResolver:
    """Returns the shared default TargetResolver instance."""
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = TargetResolver()
    return _default_resolver


def resolve_target(
    source_code: str,
    outline: StructuralOutline,
    target: LocalizationTarget,
    strict: bool = False,
) -> ResolvedTarget:
    """Convenience function to resolve a target using the default resolver."""
    return get_default_target_resolver().resolve(source_code, outline, target, strict=strict)


__all__ = [
    "TargetResolver",
    "LocalizationError",
    "InvalidRangeError",
    "OutOfRangeError",
    "SymbolNotFoundError",
    "AmbiguousSymbolError",
    "get_default_target_resolver",
    "resolve_target",
]
