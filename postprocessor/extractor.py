from __future__ import annotations
import re
from typing import List, Optional, Tuple
from opticode.models.common import Language
from opticode.parser.engine import ParserEngine

FENCE_PATTERN = re.compile(
    r"(?:^|\n)[ \t]*```+([a-zA-Z0-9_\-\+\#]*)[ \t]*\r?\n(.*?)(?:\n[ \t]*```+[ \t]*(?:\r?\n|$)|$)",
    re.DOTALL,
)

COMMON_CODE_KEYWORDS = {
    "def", "class", "function", "var", "let", "const", "import", "from",
    "return", "int", "void", "public", "private", "protected", "struct",
    "if", "for", "while", "switch", "case", "package", "type", "func",
    "fn", "pub", "impl", "use", "include", "namespace",
}


class CodeExtractor:
    """Extracts candidate source code from raw AI model responses.

    Handles:
    - Standard markdown fenced blocks (```lang ... ```)
    - Multi-backtick and whitespace-padded fences
    - Malformed or unclosed fences (```lang ... EOF)
    - Surrounding conversational prose before and after code
    - Raw code without markdown fences
    - Rejection of pure prose responses containing no code
    """

    def __init__(self, parser_engine: Optional[ParserEngine] = None) -> None:
        self.parser_engine = parser_engine or ParserEngine()

    def extract(self, raw_output: str, language: Language) -> Optional[str]:
        """Extracts candidate code from raw AI output.

        Returns normalized code string, or None if no code is present.
        """
        if not raw_output or not raw_output.strip():
            return None

        normalized_output = raw_output.replace("\r\n", "\n")

        # Step 1: Look for markdown code fences
        fenced_blocks = self._extract_fenced_blocks(normalized_output)
        if fenced_blocks:
            return self._select_best_block(fenced_blocks, language)

        # Step 2: If no fences found, evaluate if raw output is code or conversational prose
        if self._is_raw_code(normalized_output, language):
            return self._normalize_code(normalized_output)

        return None

    def _extract_fenced_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Finds all (language_tag, block_content) pairs in text."""
        blocks: List[Tuple[str, str]] = []
        for match in FENCE_PATTERN.finditer(text):
            tag = match.group(1).strip().lower()
            content = match.group(2)
            blocks.append((tag, content))
        return blocks

    def _select_best_block(self, blocks: List[Tuple[str, str]], language: Language) -> str:
        """Selects the most suitable code block among multiple candidates."""
        if len(blocks) == 1:
            return self._normalize_code(blocks[0][1])

        # Priority 1: Match block language tag to target language
        target_name = language.value.lower()
        matching_blocks = [
            content for tag, content in blocks
            if tag and (tag == target_name or tag in Language.aliases().get(target_name, []))
        ]
        if matching_blocks:
            # Return the largest matching block
            return self._normalize_code(max(matching_blocks, key=len))

        # Priority 2: Return largest block among all fences
        largest_block = max(blocks, key=lambda b: len(b[1]))[1]
        return self._normalize_code(largest_block)

    def _is_raw_code(self, text: str, language: Language) -> bool:
        """Determines if a non-fenced string is raw code or pure conversational prose."""
        stripped = text.strip()
        if not stripped:
            return False

        # Attempt to parse with the language grammar
        try:
            tree = self.parser_engine.parse(stripped, language)
            if not tree.has_errors:
                return True
        except Exception:
            pass

        # If parser detected errors, check whether the text is conversational prose
        words_lower = set(re.findall(r"\b[a-zA-Z_]\w*\b", stripped.lower()))
        prose_stopwords = {
            "i", "am", "unable", "sorry", "cannot", "please", "here", "hope",
            "unfortunately", "sure", "thanks", "thank", "clarify", "requirements",
            "instructions", "because", "would", "could", "should",
        }

        # If it contains typical conversational words, treat as prose
        if len(words_lower & prose_stopwords) >= 2:
            return False

        has_keywords = bool(words_lower & COMMON_CODE_KEYWORDS)
        has_syntax_symbols = any(sym in stripped for sym in ["{", "}", ";", "()", "->", "=>", ":="])

        if has_keywords or has_syntax_symbols:
            return True

        return False

    def _normalize_code(self, code: str) -> str:
        """Normalizes code line endings and trims outer empty lines while preserving indentation."""
        lines = code.replace("\r\n", "\n").split("\n")
        # Strip leading empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        # Strip trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)
