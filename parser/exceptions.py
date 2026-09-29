class ParserError(Exception):
    """Base exception for parser subsystem errors."""
    pass


class UnsupportedLanguageError(ParserError):
    """Raised when a requested language is not supported by the parser engine."""
    def __init__(self, language: str) -> None:
        super().__init__(f"Language '{language}' is not supported by the parser subsystem.")
        self.language = language


class GrammarLoadError(ParserError):
    """Raised when a grammar fails to load or initialize."""
    def __init__(self, language: str, reason: str) -> None:
        super().__init__(f"Failed to load grammar for '{language}': {reason}")
        self.language = language
        self.reason = reason
