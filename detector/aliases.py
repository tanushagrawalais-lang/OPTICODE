from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from opticode.models.common import Language

# Canonical Language Alias Table
# Maps common extensions, CLI labels, and naming variations to supported Languages.
CANONICAL_ALIASES: Dict[str, Language] = {
    # Python
    "py": Language.PYTHON,
    "python": Language.PYTHON,
    "python3": Language.PYTHON,
    "py3": Language.PYTHON,
    "pyw": Language.PYTHON,
    # Java
    "java": Language.JAVA,
    # C
    "c": Language.C,
    "c99": Language.C,
    "c11": Language.C,
    "c17": Language.C,
    # C++
    "cpp": Language.CPP,
    "c++": Language.CPP,
    "cxx": Language.CPP,
    "cc": Language.CPP,
    "cplusplus": Language.CPP,
    # JavaScript
    "js": Language.JAVASCRIPT,
    "javascript": Language.JAVASCRIPT,
    "ecmascript": Language.JAVASCRIPT,
    "node": Language.JAVASCRIPT,
    "nodejs": Language.JAVASCRIPT,
    "mjs": Language.JAVASCRIPT,
    "cjs": Language.JAVASCRIPT,
    # TypeScript
    "ts": Language.TYPESCRIPT,
    "typescript": Language.TYPESCRIPT,
    "mts": Language.TYPESCRIPT,
    "cts": Language.TYPESCRIPT,
    # Go
    "go": Language.GO,
    "golang": Language.GO,
    # Rust
    "rs": Language.RUST,
    "rust": Language.RUST,
}


def normalize_alias(name: str) -> str:
    """Normalizes an alias string by stripping whitespace and lowercasing."""
    return name.strip().lower()


def resolve_declared_language(declared: Optional[str]) -> Tuple[Language, bool]:
    """Resolves a user-declared language string to a supported Language enum.

    Returns:
        Tuple of (Language, is_supported):
        - If declared is None or empty: (Language.UNKNOWN, False)
        - If declared is valid and supported: (Language.XYZ, True)
        - If declared is unrecognized/unsupported: (Language.UNKNOWN, False)
    """
    if not declared:
        return Language.UNKNOWN, False

    normalized = normalize_alias(declared)
    if normalized in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[normalized], True

    return Language.UNKNOWN, False


def get_supported_aliases() -> Dict[str, str]:
    """Returns a dictionary of all supported aliases mapped to canonical language values."""
    return {alias: lang.value for alias, lang in sorted(CANONICAL_ALIASES.items())}
