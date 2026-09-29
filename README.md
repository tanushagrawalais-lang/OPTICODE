# OptiCode Subsystem B: Code Intelligence, Analysis & Post-Processing

Backend B is the deterministic, parsing-based code intelligence subsystem of the OptiCode workspace. It resides directly between the Core Backend (Backend A) and the AI orchestration layer.

---

## Architectural Ownership & Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    OptiCode Architecture                    │
├──────────────────────────────┬──────────────────────────────┤
│    Backend A (Core API)      │  Backend B (Code Analyzer)   │
├──────────────────────────────┼──────────────────────────────┤
│ • HTTP / API Transport       │ • Source Code Analysis       │
│ • Authentication & Sessions  │ • Structural AST Processing  │
│ • Database & Persistence     │ • Target Localization        │
│ • User & Conversation State  │ • AI Context Preparation     │
│ • AI Provider Orchestration  │ • Output Post-Processing     │
│ • Streaming & WebSockets     │ • Processing-Level Validator │
└──────────────────────────────┴──────────────────────────────┘
```

> **Ownership Contract**:
> - **Backend A owns**: HTTP/API transport, authentication, persistence, users, conversations, and AI provider orchestration.
> - **Backend B owns**: source-code analysis, structural processing, localization, context preparation, post-processing, and processing-level validation.
>
> Backend A must never import raw parser libraries (such as `tree_sitter`) directly. All AST operations, grammar bindings, syntax error extraction, diff calculation, and scope enforcement are encapsulated behind `opticode.AnalysisService`.

---

## 1. What Backend B Does

1. **Multi-Grammar Parsing**: Robustly parses source files using concrete Tree-sitter grammars across 8 programming languages without crashing on syntax errors.
2. **Deterministic Language Detection**: Classifies language via explicit declaration or structural AST probing, strictly recognizing ambiguity between dialect pairs (C vs. C++, JS vs. TS).
3. **Normalized Structural Outlines**: Converts disparate syntax trees into a unified `StructuralOutline` containing `StructuralNode` hierarchies (functions, methods, classes, interfaces, loops, conditionals, imports, calls, assignments).
4. **Boundary Localization**: Resolves line, range, block, symbol, and contextual targets into strict `RequestedRange`, `EditableRegion`, and `ActualRelevantContext`.
5. **Conservative Structural Findings**: Identifies structural patterns (e.g. deeply nested loops, repeated expensive calls inside loops, empty exception handlers) as conservative observations without unjustified performance claims.
6. **Model Context Preparation**: Produces minimal, token-efficient, model-ready payloads (`ModelContextPayload`) providing the AI with necessary context while protecting unrelated code from leakage.
7. **AI Output Post-Processing**: Strips prose, extracts fenced/raw code blocks, repairs minor formatting, and reconstructs full candidate files from localized snippet outputs.
8. **Strict Scope-Guard Enforcement**: Computes line-level diffs and guarantees that any AI generation modifying code outside the allowed `EditableRegion` is explicitly rejected.
9. **Processing-Level Validation**: Validates candidate code against Tree-sitter grammars, checking for syntax errors, `ERROR` nodes, `MISSING` tokens, and language mismatches.

---

## 2. What Backend B Does Not Do

1. **Does NOT Call AI Providers**: Backend B never calls OpenAI, Anthropic, Google Gemini, Ollama, or any LLM provider. Backend A handles all LLM network requests.
2. **Does NOT Handle HTTP/Transport**: Backend B has no FastAPI, Flask, or web server dependencies. It is consumed as an in-process Python library.
3. **Does NOT Store Data**: Backend B is completely stateless. It performs zero database operations, file-system caching, or session tracking.
4. **Does NOT Perform Semantic Type Checking**: Backend B builds structural outlines from syntax trees. It does not perform full compiler-level type checking, cross-file resolution, or symbol table linking across project files.
5. **Does NOT Guarantee Runtime Correctness**: Parsing validation only confirms concrete syntax grammar compliance. It does not prove runtime behavior, algorithmic complexity, performance gains, memory safety, or security vulnerabilities.

---

## 3. Installation & Dependencies

OptiCode Analyzer requires **Python 3.10+** (fully verified up to Python 3.14).

### Package Dependencies
- `tree-sitter>=0.23.0`
- `tree-sitter-python>=0.23.0`
- `tree-sitter-java>=0.23.0`
- `tree-sitter-c>=0.23.0`
- `tree-sitter-cpp>=0.23.0`
- `tree-sitter-javascript>=0.23.0`
- `tree-sitter-typescript>=0.23.0`
- `tree-sitter-go>=0.23.0`
- `tree-sitter-rust>=0.23.0`

### Installation
From the package root:
```bash
pip install -e .
```

To run the complete verification suite:
```bash
pip install -e .[dev]
pytest
```

---

## 4. Usage & Quick Start

```python
from opticode import (
    AnalysisService,
    CodeAnalysisInput,
    LocalizationTarget,
    PostprocessRequest,
    TargetType,
)

# 1. Initialize the service facade
service = AnalysisService()

# 2. Analyze user source code with a targeted function
source = """def calculate_total(items):
    total = 0
    for item in items:
        total = total + item.price
    return total
"""

analysis = service.analyze(
    CodeAnalysisInput(
        source_code=source,
        declared_language="python",
        target=LocalizationTarget(
            target_type=TargetType.SYMBOL,
            symbol_name="calculate_total",
        ),
        user_instruction="Optimize item summation",
    )
)

print(f"Language: {analysis.language.value}")
print(f"Parse Success: {analysis.parse_success}")
print(f"Editable Region: Lines {analysis.resolved_target.editable_region.range.start.line}-{analysis.resolved_target.editable_region.range.end.line}")

# 3. Backend A sends analysis.model_context to AI model...
raw_ai_response = """Here is the optimized function:
```python
def calculate_total(items):
    return sum(item.price for item in items)
```
"""

# 4. Postprocess & scope-guard the AI output
post = service.postprocess(
    PostprocessRequest(
        original_source=source,
        raw_ai_output=raw_ai_response,
        language=analysis.language,
        editable_region=analysis.resolved_target.editable_region,
    )
)

if post.success and post.is_within_scope:
    print("Full modified file ready to return to user:")
    print(post.full_modified_source)
else:
    print(f"Postprocessing rejected: {post.errors}")
```

---

## 5. `AnalysisService`

The central facade class (`opticode.AnalysisService`) exposes four primary methods:

### Method Signatures

```python
class AnalysisService:
    def __init__(self, ...) -> None: ...

    def analyze(self, input_data: CodeAnalysisInput) -> AnalysisResult:
        """Runs the complete analysis pipeline:
        Detection -> Parsing -> Outlines -> Localization -> Findings -> Context.
        """

    def build_context(
        self,
        input_data: CodeAnalysisInput,
        resolved_target: ResolvedTarget,
    ) -> ModelContextPayload:
        """Extracts and formats targeted, compact context for the AI layer."""

    def postprocess(self, request: PostprocessRequest) -> PostprocessResult:
        """Extracts code from AI output, reconstructs full source, verifies
        syntax, and strictly enforces editable-region boundaries.
        """

    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Validates candidate code syntax and checks scope conformance."""
```

---

## 6. `CodeAnalysisInput`

Data structure representing incoming requests from Backend A.

| Field | Type | Description |
|---|---|---|
| `source_code` | `str` | Complete source code string of the active file |
| `declared_language` | `Optional[str]` | Optional user- or frontend-declared language tag (e.g. `"python"`, `"ts"`, `"cpp"`) |
| `target` | `Optional[LocalizationTarget]` | Optional user targeting information (line, symbol, range, block) |
| `user_instruction` | `Optional[str]` | Natural language prompt or task instruction from user |

All models provide `.to_dict()` and `.from_dict()` for JSON serialization.

---

## 7. `AnalysisResult`

Result returned by `service.analyze(input_data)`.

| Field | Type | Description |
|---|---|---|
| `language` | `Language` | Resolved language enum (`PYTHON`, `JAVA`, etc.) |
| `detection_status` | `DetectionStatus` | `DECLARED`, `DETECTED`, `UNCERTAIN`, or `UNSUPPORTED` |
| `detection_details` | `str` | Human-readable explanation of detection outcome |
| `parse_success` | `bool` | `True` if parsed with zero AST `ERROR` or `MISSING` nodes |
| `outline` | `Optional[StructuralOutline]` | Extracted symbols, hierarchy, and structural index |
| `resolved_target` | `Optional[ResolvedTarget]` | Boundaries of requested target, editable region, and context |
| `findings` | `List[StructuralFinding]` | Conservative structural observations detected |
| `model_context` | `Optional[ModelContextPayload]` | Compact payload ready for LLM prompt construction |
| `errors` | `List[str]` | List of parse or processing errors encountered |

---

## 8. `LocalizationTarget`

Specifies what part of the source the user wants to inspect or modify.

| Field | Type | Description |
|---|---|---|
| `target_type` | `TargetType` | `LINE`, `RANGE`, `BLOCK`, `SYMBOL`, or `CONTEXTUAL` |
| `line` | `Optional[int]` | Target line number (1-indexed) |
| `start_line` | `Optional[int]` | Starting line for `RANGE` or `BLOCK` (1-indexed) |
| `end_line` | `Optional[int]` | Ending line for `RANGE` or `BLOCK` (1-indexed) |
| `symbol_name` | `Optional[str]` | Function, method, or class name for `SYMBOL` |
| `selected_text` | `Optional[str]` | Verbatim selected code snippet for `BLOCK` |

---

## 9. `ResolvedTarget`

Calculated AST boundaries returned after target resolution.

| Field | Type | Description |
|---|---|---|
| `requested_range` | `CodeRange` | Exact lines/columns the user requested |
| `editable_region` | `EditableRegion` | Strict boundary the AI is permitted to alter |
| `actual_relevant_context` | `ActualRelevantContext` | Surrounding scope (e.g. enclosing class/function) provided for understanding |
| `target_node_ids` | `List[str]` | Node IDs in `StructuralOutline` corresponding to target |
| `ambiguity_detected` | `bool` | `True` if multiple symbols match the given target name |
| `success` | `bool` | `True` if resolution succeeded |
| `errors` | `List[str]` | Error details if target could not be resolved |

### Components:
- **`EditableRegion`**: Contains `range: CodeRange` and `is_strict_block: bool`. Expansion never happens silently.
- **`ActualRelevantContext`**: Contains `range: CodeRange`, `enclosing_symbol: Optional[str]`, and `surrounding_code: Optional[str]`. This context is read-only.

---

## 10. `ModelContextPayload`

Compact, vendor-agnostic context payload designed for Backend A's AI prompt generation.

| Field | Type | Description |
|---|---|---|
| `language` | `str` | Canonical language name |
| `target_range` | `CodeRange` | User requested range (start/end line and column) |
| `editable_range` | `CodeRange` | Permitted modification boundary |
| `relevant_source` | `str` | Targeted code plus necessary surrounding context |
| `detection_status` | `Optional[str]` | Confidence level of language detection |
| `user_instruction` | `Optional[str]` | User prompt / request instruction |
| `enclosing_symbol` | `Optional[str]` | Name of enclosing class/function (if any) |
| `structural_outline` | `List[Dict]` | High-level symbol definitions |
| `findings` | `List[StructuralFinding]` | Conservative structural observations |
| `localization_metadata`| `Dict[str, Any]` | Targeting metadata and context ranges |

---

## 11. `PostprocessRequest`

Payload submitted to `service.postprocess(...)` to handle raw LLM text.

| Field | Type | Description |
|---|---|---|
| `original_source` | `str` | Complete original source code before AI edits |
| `raw_ai_output` | `str` | Raw string received from the AI model (markdown, prose, code) |
| `language` | `Language` | Expected programming language |
| `editable_region` | `Optional[EditableRegion]` | Allowed modification boundary |
| `expected_target` | `Optional[LocalizationTarget]`| Original localization target (optional) |

---

## 12. `PostprocessResult`

Outcome of post-processing and scope validation.

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if code was extracted, valid, and within scope |
| `extracted_code` | `Optional[str]` | Isolated code extracted from fences or raw output |
| `full_modified_source` | `Optional[str]`| Complete reconstructed source file with modifications applied |
| `modified_range` | `Optional[CodeRange]` | Exact line/column span modified by the AI |
| `diff` | `Optional[str]` | Unified diff of modifications against original |
| `is_within_scope` | `bool` | `False` if changes touched lines outside `editable_region` |
| `validation` | `Optional[ValidationResult]`| Concrete syntax validation report |
| `errors` | `List[str]` | Rejection reasons or syntax error messages |

---

## 13. `ValidationRequest`

Direct validation request for candidate source code.

| Field | Type | Description |
|---|---|---|
| `source_code` | `str` | Candidate source code to validate |
| `language` | `Language` | Target language grammar |
| `expected_scope` | `Optional[CodeRange]` | Optional boundary outside of which modifications are forbidden |
| `original_source` | `Optional[str]` | Original source code (required if `expected_scope` is provided) |

---

## 14. `ValidationResult`

Result of processing-level syntax and scope verification.

| Field | Type | Description |
|---|---|---|
| `is_valid` | `bool` | `True` if syntax is valid, language matches, and scope is respected |
| `is_valid_syntax` | `bool` | `True` if AST contains zero `ERROR` or `MISSING` nodes |
| `parse_errors` | `List[str]` | Specific syntax error locations and descriptions |
| `scope_violations` | `List[str]` | Descriptions of out-of-scope line modifications |
| `language_matched` | `bool` | `True` if code matches expected language grammar |
| `error_node_count` | `int` | Total number of Tree-sitter `ERROR` nodes |
| `missing_node_count` | `int` | Total number of Tree-sitter `MISSING` nodes |
| `disclaimer` | `str` | Standard disclaimer regarding limits of static parsing |

---

## 15. Language Detection States

The `LanguageDetector` classifies input into one of four states:

1. **`DECLARED`**: The caller provided a supported declared language or recognized alias (e.g. `"py"` → `PYTHON`).
2. **`DETECTED`**: No language was declared, but Tree-sitter parsing and conservative syntax heuristics definitively matched exactly one grammar.
3. **`UNCERTAIN`**: Multiple grammars accept the source cleanly without disambiguating features (e.g. plain `int x = 1;` in C vs. C++, or empty source). Backend B refuses to guess silently.
4. **`UNSUPPORTED`**: The language is explicitly not supported (e.g. `"ruby"`, `"php"`, `"kotlin"`).

---

## 16. Supported Languages & Aliases

Backend B provides full AST parsing, structural outline extraction, and syntax validation for 8 languages:

| Canonical Language | Enum | Supported Aliases |
|---|---|---|
| Python | `Language.PYTHON` | `python`, `py` |
| Java | `Language.JAVA` | `java` |
| C | `Language.C` | `c` |
| C++ | `Language.CPP` | `cpp`, `c++`, `cc`, `cxx` |
| JavaScript | `Language.JAVASCRIPT` | `javascript`, `js` |
| TypeScript | `Language.TYPESCRIPT` | `typescript`, `ts` |
| Go | `Language.GO` | `go`, `golang` |
| Rust | `Language.RUST` | `rust`, `rs` |

### Disambiguation Logic:
- **JS vs. TS**: Code containing explicit TypeScript annotations (`interface`, `type`, `: string`, `as const`) resolves to `TYPESCRIPT`. Plain JavaScript syntax with no TypeScript features reports `UNCERTAIN` when undeclared.
- **C vs. C++**: Code containing C++ features (`class`, `template`, `namespace`, `std::`, `cout`) resolves to `CPP`. Pure C syntax without C++ features reports `UNCERTAIN` when undeclared.

---

## 17. Localization Behavior

Localization maps user requests into precise boundaries:

1. **`LINE` Target**: Focuses on a single line number. If the line is inside a subroutine, `ActualRelevantContext` expands to the enclosing function/method, but `EditableRegion` remains strictly bounded.
2. **`RANGE` Target**: Line range `[start_line, end_line]`. Automatically clamped to valid file boundaries.
3. **`BLOCK` Target**: Explicit block selection. Treated as a strict boundary (`is_strict_block = True`); AI cannot edit outside these lines.
4. **`SYMBOL` Target**: Resolves function, method, class, or interface declarations by identifier.
   - Ambiguous duplicate names in different scopes return `ambiguity_detected = True` with candidates.
   - Nonexistent symbols fail cleanly with descriptive error messages.
5. **`CONTEXTUAL` Target**: Cursor position targeting. Resolves the closest enclosing structural node.

---

## 18. Scope-Guard Behavior

The `ScopeGuard` enforces that AI modifications remain strictly within the designated `EditableRegion`.

1. **Diff Calculation**: Backend B computes line-by-line unified diffs between the original source and candidate source.
2. **Modified Line Tracking**: Identifies all inserted, deleted, or altered line indices.
3. **Strict Containment**: Every modified line index must fall within `[editable_region.start.line, editable_region.end.line]`.
4. **Out-of-Scope Rejection**: If an AI prompt was asked to modify lines 10–15, but also modifies line 40, `is_within_scope` is set to `False` and `success` is set to `False`. The modification is rejected immediately.
5. **Full-Source Reconstruction**: If the AI returns only the modified snippet, Backend B accurately splices it into the original file at the target region before verifying scope.

---

## 19. Validation Limitations

Backend B's validator operates at the **concrete syntax and parsing level**.

> [!WARNING]
> **Validation Guarantees & Limitations**:
> - Tree-sitter parsing guarantees that the code conforms to the formal grammar of the language.
> - Parsing **DOES NOT** guarantee runtime correctness, termination, or absence of exceptions.
> - Parsing **DOES NOT** verify semantic logic, business requirements, or algorithmic correctness.
> - Parsing **DOES NOT** prove performance improvement or memory efficiency.
> - Parsing **DOES NOT** guarantee security or absence of vulnerabilities.

Every `ValidationResult` carries the standard disclaimer attribute:
```
"Syntax validity indicates grammar compliance only. Parsing does not verify
runtime correctness, logical correctness, algorithmic correctness,
performance improvement, or security."
```

---

## 20. Integration Example for Backend A

Below is the complete end-to-end integration lifecycle demonstrating how Backend A consumes Backend B:

```python
"""Example Backend A Controller / Worker Integration."""

from opticode import (
    AnalysisService,
    CodeAnalysisInput,
    LocalizationTarget,
    PostprocessRequest,
    TargetType,
)

# 1. Instantiate the singleton facade during Backend A startup
analysis_service = AnalysisService()


async def handle_user_optimization_request(
    file_content: str,
    target_symbol: str,
    user_prompt: str,
) -> dict:
    """Step 1: Analyze user source and extract model context."""
    analysis_input = CodeAnalysisInput(
        source_code=file_content,
        target=LocalizationTarget(
            target_type=TargetType.SYMBOL,
            symbol_name=target_symbol,
        ),
        user_instruction=user_prompt,
    )

    analysis_result = analysis_service.analyze(analysis_input)

    if not analysis_result.parse_success:
        return {
            "status": "error",
            "message": "Source code contains syntax errors.",
            "details": analysis_result.errors,
        }

    # Step 2: Backend A orchestrates the AI Provider call using the prepared context
    # (Notice: Backend B created the payload; Backend A calls the LLM)
    context_payload = analysis_result.model_context
    system_prompt = (
        f"You are optimizing {context_payload.language} code.\n"
        f"Only modify the permitted editable range: "
        f"lines {context_payload.editable_range.start.line}-{context_payload.editable_range.end.line}.\n"
        f"Structural findings observed: {[f.description for f in context_payload.findings]}"
    )
    user_message = f"{user_prompt}\n\nCode:\n{context_payload.relevant_source}"

    # Simulated AI call (Backend A's responsibility)
    raw_ai_response = await fake_ai_provider_call(system_prompt, user_message)

    # Step 3: Validate and scope-guard the AI output through Backend B
    postprocess_request = PostprocessRequest(
        original_source=file_content,
        raw_ai_output=raw_ai_response,
        language=analysis_result.language,
        editable_region=analysis_result.resolved_target.editable_region,
    )

    post_result = analysis_service.postprocess(postprocess_request)

    # Step 4: Handle validation or scope-guard failures
    if not post_result.success:
        return {
            "status": "rejected",
            "reason": "AI response failed validation or scope guard.",
            "is_within_scope": post_result.is_within_scope,
            "errors": post_result.errors,
            "diff": post_result.diff,
        }

    # Step 5: Deliver safely reconstructed full code to user
    return {
        "status": "success",
        "modified_source": post_result.full_modified_source,
        "diff": post_result.diff,
    }


async def fake_ai_provider_call(system: str, prompt: str) -> str:
    return "```python\ndef helper():\n    return 42\n```"
```
