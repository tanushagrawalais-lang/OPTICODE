class LocalizationError(Exception):
    """Base exception for code localization errors."""
    pass


class InvalidRangeError(LocalizationError):
    """Raised when start line is greater than end line or invalid."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class OutOfRangeError(LocalizationError):
    """Raised when requested lines are outside of the file boundary."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SymbolNotFoundError(LocalizationError):
    """Raised when a targeted symbol cannot be found in the AST."""
    def __init__(self, symbol_name: str) -> None:
        super().__init__(f"Symbol '{symbol_name}' was not found in the source code outline.")
        self.symbol_name = symbol_name


class AmbiguousSymbolError(LocalizationError):
    """Raised when multiple candidate symbols match and cannot be disambiguated."""
    def __init__(self, symbol_name: str, candidates: list[str]) -> None:
        cand_str = "; ".join(candidates)
        super().__init__(f"Symbol '{symbol_name}' is ambiguous. Found candidates: {cand_str}")
        self.symbol_name = symbol_name
        self.candidates = candidates
