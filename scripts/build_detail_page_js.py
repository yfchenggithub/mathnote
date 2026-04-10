from __future__ import annotations

"""
===============================================================================
build_detail_page_js.py
===============================================================================

Purpose
-------
Build one JS data file per module for the WeChat mini-program detail page.

This script is intentionally different from `build_search_bundle_js.py`:
- `build_search_bundle_js.py` prepares aggressively indexed search data.
- `build_detail_page_js.py` prepares display-oriented detail data.

Why this script exists
----------------------
The detail page has different needs from search:
1. It needs stable, readable, display-ready fields.
2. It should keep only detail-page metadata, not search-only metadata.
3. It benefits from a config-driven schema so future fields can be added
   without rewriting the whole pipeline.
4. It should be easy to debug when a single item or a single module fails.

Included fields
---------------
This builder keeps only detail-page data such as:
- identity and display fields (`id`, `title`, `alias`, `difficulty`, `tags`)
- math explanation fields (`core_formula`, `conditions`, `conclusions`)
- cleaned long-form text (`statement`, `explanation`, `proof`, `examples`,
  `traps`, `summary`)
- page configuration (`shareConfig`, `assets`, `interactive`, `relations`)

Excluded fields
---------------
Search-only metadata is intentionally excluded from this output:
- `search`
- `searchmeta`
- `ranking`
- search-specific values like `pinyin` and `pinyinAbbr`

Output shape
------------
Each generated file exports:

module.exports = {
  "I001": {
    "id": "I001",
    "title": "...",
    "core_formula": "...",
    "statement": "...",
    "explanation": "...",
    "proof": "...",
    "examples": "...",
    "traps": "...",
    "summary": "...",
    "shareConfig": {}
  }
}

Common usage
------------
1. Build all discoverable modules:
   `python scripts/build_detail_page_js.py`
2. Build one module:
   `python scripts/build_detail_page_js.py --module 07_inequality`
3. Build one item and inspect logs without writing files:
   `python scripts/build_detail_page_js.py --module 07_inequality --item I001 --debug --dry-run`
4. Fail immediately on missing required fields:
   `python scripts/build_detail_page_js.py --strict`

Maintenance guidance
--------------------
When you need to extend the detail page schema, start here:
- `DETAIL_META_FIELD_SPECS`
- `DETAIL_TEXT_FIELD_SPECS`

When you need to adjust how TeX is converted into display-friendly plain text,
start here:
- `clean_tex`

Last Updated: 2026-04-06
===============================================================================
"""

import argparse
import copy
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "content"
META_FILENAME = "meta.json"

DEFAULT_TARGET_MODULES: tuple[str, ...] = ()
IGNORED_TOP_LEVEL_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "assets",
    "data",
    "misc",
    "node_modules",
    "scripts",
    "search_engine",
    "templates",
}

LOGGER = logging.getLogger("build_detail_page_js")
MISSING = object()


class BuildError(RuntimeError):
    """A readable build-stage error that should be shown to the user."""


def default_none() -> None:
    """Return `None` for config-driven default values."""

    return None


@dataclass(frozen=True)
class TextFieldSpec:
    """Describe one cleaned text field in the detail-page output."""

    output_name: str
    source_filename: str
    description: str
    purpose: str
    required: bool = False
    fallback_paths: tuple[tuple[str, ...], ...] = ()
    transform: Callable[[str], str] | None = None


@dataclass(frozen=True)
class MetaFieldSpec:
    """Describe one metadata field that should survive into the detail page."""

    output_name: str
    source_paths: tuple[tuple[str, ...], ...]
    description: str
    purpose: str
    required: bool = False
    default_factory: Callable[[], Any] = default_none


@dataclass(frozen=True)
class BuildConfig:
    """Immutable runtime configuration for one build run."""

    project_root: Path
    output_dir: Path
    target_modules: tuple[str, ...]
    target_items: tuple[str, ...]
    dry_run: bool
    debug: bool
    strict: bool


@dataclass
class ModuleStats:
    """Collect module-level counters for logs and verification."""

    module_name: str
    scanned_items: int = 0
    built_items: int = 0
    filtered_items: int = 0
    skipped_items: int = 0


def configure_console_encoding() -> None:
    """Best-effort UTF-8 stdout/stderr configuration for Windows terminals."""

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def configure_logging(debug: bool) -> None:
    """Initialize logging."""

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments with detail-page oriented examples."""

    parser = argparse.ArgumentParser(
        description="Build display-oriented JS data files for detail pages.",
        epilog=(
            "Examples:\n"
            "  python scripts/build_detail_page_js.py\n"
            "  python scripts/build_detail_page_js.py --module 07_inequality\n"
            "  python scripts/build_detail_page_js.py --module 07_inequality "
            "--item I001 --debug --dry-run\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--base-dir",
        default=str(PROJECT_ROOT),
        help=(
            "Project root. Module discovery and relative content paths are "
            "resolved from here."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=(
            "Directory where module detail files are written. "
            "Default: data/content"
        ),
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        help=(
            "Only build the given module directory. Can be repeated. "
            "Example: --module 07_inequality"
        ),
    )
    parser.add_argument(
        "--item",
        dest="items",
        action="append",
        help=(
            "Only build the given item directory name or content id. "
            "Can be repeated. Example: --item I001 or "
            "--item I001_Compound_Inequality_Transformation"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build everything in memory and print logs, but do not write files.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print verbose logs, including per-field previews and fallbacks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Fail the whole command when required fields are missing, JSON is "
            "invalid, or duplicate ids are found."
        ),
    )
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> BuildConfig:
    """Convert raw argparse output into one typed config object."""

    return BuildConfig(
        project_root=Path(args.base_dir).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        target_modules=tuple(args.modules or DEFAULT_TARGET_MODULES),
        target_items=tuple(args.items or ()),
        dry_run=bool(args.dry_run),
        debug=bool(args.debug),
        strict=bool(args.strict),
    )


def preview_text(text: str, limit: int = 96) -> str:
    """Return a one-line preview used in debug logs."""

    compact = re.sub(r"\s+", " ", text or "").strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def read_text_file(path: Path, *, strict: bool, required: bool) -> str:
    """Read a text file with controlled logging."""

    if not path.exists():
        message = f"Text file not found: {path}"
        if required:
            if strict:
                raise BuildError(message)
            LOGGER.warning(message)
        else:
            LOGGER.debug(message)
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        message = f"Failed to read text file: {path}"
        if strict:
            raise BuildError(message) from exc
        LOGGER.warning(message)
        return ""


def read_json_file(path: Path, *, strict: bool) -> dict[str, Any]:
    """Read `meta.json` and validate that its root is an object."""

    if not path.exists():
        message = f"JSON file not found: {path}"
        if strict:
            raise BuildError(message)
        LOGGER.warning(message)
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        message = f"Failed to parse JSON file: {path}"
        if strict:
            raise BuildError(message) from exc
        LOGGER.warning(message)
        return {}

    if not isinstance(data, dict):
        message = f"JSON root must be an object: {path}"
        if strict:
            raise BuildError(message)
        LOGGER.warning(message)
        return {}

    return data


def get_nested_value(data: Any, path: tuple[str, ...]) -> Any:
    """Return a nested value from a dict-like tree, or `MISSING` if absent."""

    current = data
    for segment in path:
        if not isinstance(current, dict) or segment not in current:
            return MISSING
        current = current[segment]
    return current


def resolve_first_value(
    data: dict[str, Any],
    candidate_paths: tuple[tuple[str, ...], ...],
) -> tuple[Any, tuple[str, ...] | None]:
    """Pick the first existing value from a list of candidate nested paths."""

    for path in candidate_paths:
        value = get_nested_value(data, path)
        if value is not MISSING:
            return value, path
    return MISSING, None


def clone_json_value(value: Any) -> Any:
    """Defensively copy JSON-compatible values before placing them in output."""

    return copy.deepcopy(value)


def stringify_text_value(value: Any) -> str:
    """Convert fallback metadata into plain text before `clean_tex`."""

    if value is MISSING or value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        lines: list[str] = []
        for key, nested_value in value.items():
            nested_text = stringify_text_value(nested_value).strip()
            if nested_text:
                lines.append(f"{key}: {nested_text}")
        return "\n".join(lines)

    if isinstance(value, (list, tuple)):
        parts = [stringify_text_value(item).strip() for item in value]
        return "\n".join(part for part in parts if part)

    return str(value)


# =============================================================================
# TeX cleaning helpers
# =============================================================================

# This script does not try to be a full LaTeX parser.
# Its goal is narrower and more practical:
# - keep the mathematical meaning readable
# - remove layout noise
# - emit stable plain text for the detail page

_NESTED_BRACE_CONTENT = r"(?:[^{}]|\{[^{}]*\})*"

_FRACTION_PATTERN = re.compile(
    rf"\\frac\{{({_NESTED_BRACE_CONTENT})\}}\{{({_NESTED_BRACE_CONTENT})\}}"
)
_SQRT_PATTERN = re.compile(rf"\\sqrt\{{({_NESTED_BRACE_CONTENT})\}}")
_WRAPPED_COMMAND_PATTERN = re.compile(
    rf"\\(?!frac\b)[a-zA-Z]+\{{({_NESTED_BRACE_CONTENT})\}}"
)
_TWO_ARGUMENT_COMMAND_PATTERN = re.compile(
    rf"\\(?!frac\b)[a-zA-Z]+\{{({_NESTED_BRACE_CONTENT})\}}\{{({_NESTED_BRACE_CONTENT})\}}"
)

_SYMBOL_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\\iff", " <=> "),
    (r"\\implies", " => "),
    (r"\\Rightarrow", " => "),
    (r"\\geqslant", " >= "),
    (r"\\geq", " >= "),
    (r"\\leqslant", " <= "),
    (r"\\leq", " <= "),
    (r"\\neq", " != "),
    (r"\\to", " -> "),
    (r"\\cdot", " * "),
    (r"\\times", " * "),
    (r"\\infty", " infinity "),
    (r"\\in", " in "),
)


def _repeat_substitution(
    pattern: re.Pattern[str],
    replacer: Callable[[re.Match[str]], str],
    text: str,
) -> str:
    """Apply a substitution until the text stops changing."""

    previous = None
    current = text
    while previous != current:
        previous = current
        current = pattern.sub(replacer, current)
    return current


def strip_latex_comments(text: str) -> str:
    """Remove LaTeX line comments while preserving escaped percent signs."""

    return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)


def strip_environment_markers(text: str) -> str:
    """Remove `\\begin{...}` and `\\end{...}` container markers."""

    return re.sub(r"\\(begin|end)\{[^{}]+\}", "", text)


def remove_standalone_option_lines(text: str) -> str:
    """Drop layout-only lines like `[style=nextline, ...]`."""

    return re.sub(r"^\s*\[[^\]]+\]\s*$", "", text, flags=re.MULTILINE)


def convert_list_items(text: str) -> str:
    """Turn `\\item` into readable bullet-like plain text."""

    return re.sub(r"\\item", "\n- ", text)


def unwrap_item_label_brackets(text: str) -> str:
    """Convert list labels like `- [Label]` into `- Label`."""

    return re.sub(r"(^\s*-\s*)\[([^\]]+)\]", r"\1\2", text, flags=re.MULTILINE)


def replace_fractions(text: str) -> str:
    """Convert `\\frac{a}{b}` into `(a) / (b)` before other cleanup runs."""

    def replacer(match: re.Match[str]) -> str:
        """Preserve numerator and denominator as readable grouped text."""

        return f"({match.group(1)}) / ({match.group(2)})"

    return _repeat_substitution(_FRACTION_PATTERN, replacer, text)


def replace_square_roots(text: str) -> str:
    """Convert `\\sqrt{a}` into `sqrt(a)`."""

    return _SQRT_PATTERN.sub(lambda match: f"sqrt({match.group(1)})", text)


def normalize_absolute_value_and_scalers(text: str) -> str:
    """Remove `\\left` and `\\right` while preserving `|...|`."""

    text = text.replace(r"\left|", "|").replace(r"\right|", "|")
    return text.replace(r"\left", "").replace(r"\right", "")


def unwrap_simple_commands(text: str) -> str:
    """Remove wrapper commands like `\\textbf{...}` while keeping inner text."""

    return _repeat_substitution(
        _WRAPPED_COMMAND_PATTERN,
        lambda match: match.group(1),
        text,
    )


def unwrap_two_argument_commands(text: str) -> str:
    """Keep the content argument of commands like `\\textcolor{red}{text}`."""

    return _repeat_substitution(
        _TWO_ARGUMENT_COMMAND_PATTERN,
        lambda match: match.group(2),
        text,
    )


def replace_symbol_commands(text: str) -> str:
    """Replace common no-argument math commands with ASCII-friendly symbols."""

    for pattern, replacement in _SYMBOL_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    return text


def remove_math_mode_markers(text: str) -> str:
    """Remove math-mode boundaries such as `$`, `\\[`, and `\\(`."""

    return (
        text.replace("$", "")
        .replace(r"\[", "\n")
        .replace(r"\]", "\n")
        .replace(r"\(", "")
        .replace(r"\)", "")
    )


def remove_remaining_commands(text: str) -> str:
    """Conservatively remove remaining LaTeX command names."""

    return re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?", " ", text)


def remove_curly_braces(text: str) -> str:
    """Drop leftover curly braces after other cleanup steps."""

    return text.replace("{", "").replace("}", "")


def normalize_whitespace(text: str) -> str:
    """Normalize line content while preserving line breaks for readability."""

    normalized_lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)


def clean_tex(text: str) -> str:
    """Convert TeX-like content into stable plain text for detail-page display."""

    if not text:
        return ""

    cleaned = text
    cleaned = strip_latex_comments(cleaned)
    cleaned = strip_environment_markers(cleaned)
    cleaned = remove_standalone_option_lines(cleaned)
    cleaned = convert_list_items(cleaned)
    cleaned = unwrap_item_label_brackets(cleaned)
    cleaned = replace_fractions(cleaned)
    cleaned = replace_square_roots(cleaned)
    cleaned = normalize_absolute_value_and_scalers(cleaned)
    cleaned = unwrap_two_argument_commands(cleaned)
    cleaned = unwrap_simple_commands(cleaned)
    cleaned = replace_symbol_commands(cleaned)
    cleaned = remove_math_mode_markers(cleaned)
    cleaned = remove_remaining_commands(cleaned)
    cleaned = remove_curly_braces(cleaned)
    cleaned = normalize_whitespace(cleaned)
    return cleaned


DETAIL_META_FIELD_SPECS: tuple[MetaFieldSpec, ...] = (
    MetaFieldSpec(
        output_name="module",
        source_paths=(("module",),),
        description="Logical module name from meta.json",
        purpose="Lets the detail page know the business module without using the directory name.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="alias",
        source_paths=(("core", "alias"),),
        description="Alternative titles or aliases",
        purpose="Useful for secondary display, FAQ labels, or future content hints.",
        default_factory=list,
    ),
    MetaFieldSpec(
        output_name="difficulty",
        source_paths=(("core", "difficulty"),),
        description="Difficulty level",
        purpose="Supports badges, filtering, or display of expected problem difficulty.",
        default_factory=default_none,
    ),
    MetaFieldSpec(
        output_name="category",
        source_paths=(("core", "category"),),
        description="Primary topic category",
        purpose="Supports detail-page labeling and page-level context.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="tags",
        source_paths=(("core", "tags"),),
        description="Topic tags",
        purpose="Useful for related content chips and page-level navigation.",
        default_factory=list,
    ),
    MetaFieldSpec(
        output_name="core_summary",
        source_paths=(("core", "summary"),),
        description="Short summary from core metadata",
        purpose="Keeps a compact summary separate from the long cleaned `summary` field.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="core_formula",
        source_paths=(("math", "core_formula"),),
        description="Primary formula or theorem statement",
        purpose="Usually the first math block the detail page wants to highlight.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="related_formulas",
        source_paths=(("math", "related_formulas"),),
        description="Closely related formulas",
        purpose="Supports extended reading and future expandable formula panels.",
        default_factory=list,
    ),
    MetaFieldSpec(
        output_name="variables",
        source_paths=(("math", "variables"),),
        description="Variables used by the formula",
        purpose="Helps the detail page explain notation without re-parsing the formula text.",
        default_factory=list,
    ),
    MetaFieldSpec(
        output_name="conditions",
        source_paths=(("math", "conditions"),),
        description="Conditions under which the statement holds",
        purpose="Important guardrails for the detail page so conditions are easy to show.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="conclusions",
        source_paths=(("math", "conclusions"),),
        description="Main conclusion or equality case",
        purpose="Lets the page show the takeaway without re-reading the full proof.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="usage",
        source_paths=(("usage",),),
        description="Usage scenarios and problem types",
        purpose="Supports 'when to use this' sections on the detail page.",
        default_factory=dict,
    ),
    MetaFieldSpec(
        output_name="interactive",
        source_paths=(("interactive",),),
        description="Interactive page configuration",
        purpose="Keeps detail-page interactive affordances close to the content record.",
        default_factory=dict,
    ),
    MetaFieldSpec(
        output_name="assets",
        source_paths=(("assets",),),
        description="Static asset references",
        purpose="The detail page can directly load svg, png, mp4, or other resources.",
        default_factory=dict,
    ),
    MetaFieldSpec(
        output_name="shareConfig",
        source_paths=(("shareConfig",),),
        description="Share card title and description",
        purpose="Used directly by the mini-program sharing entry points.",
        default_factory=dict,
    ),
    MetaFieldSpec(
        output_name="relations",
        source_paths=(("relations",),),
        description="Prerequisites and related content",
        purpose="Supports related-content blocks and learning-path navigation.",
        default_factory=dict,
    ),
    MetaFieldSpec(
        output_name="isPro",
        source_paths=(("isPro",),),
        description="Premium or gated flag",
        purpose="Allows the page to show lock states or access messaging.",
        default_factory=default_none,
    ),
    MetaFieldSpec(
        output_name="remarks",
        source_paths=(("remarks",),),
        description="Free-form remarks",
        purpose="Keeps room for editorial notes without changing the schema.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="knowledgeNode",
        source_paths=(("knowledgeNode",),),
        description="Primary knowledge-tree node",
        purpose="Useful for breadcrumb-like display or curriculum linking.",
        default_factory=str,
    ),
    MetaFieldSpec(
        output_name="altNodes",
        source_paths=(("altNodes",),),
        description="Alternative knowledge-tree nodes",
        purpose="Supports cross-linking when one topic belongs to multiple paths.",
        default_factory=str,
    ),
)


DETAIL_TEXT_FIELD_SPECS: tuple[TextFieldSpec, ...] = (
    TextFieldSpec(
        output_name="statement",
        source_filename="01_statement.tex",
        description="Main cleaned theorem/problem statement",
        purpose="This is the primary content block shown at the top of the detail page.",
        required=True,
        fallback_paths=(("content", "statement"),),
        transform=clean_tex,
    ),
    TextFieldSpec(
        output_name="explanation",
        source_filename="02_explanation.tex",
        description="Cleaned explanatory text",
        purpose="Used for intuition, decomposition, and interpretation under the statement.",
        transform=clean_tex,
    ),
    TextFieldSpec(
        output_name="proof",
        source_filename="03_proof.tex",
        description="Cleaned proof text",
        purpose="Keeps the formal derivation in display-ready plain text.",
        transform=clean_tex,
    ),
    TextFieldSpec(
        output_name="examples",
        source_filename="04_examples.tex",
        description="Cleaned examples text",
        purpose="Supports worked examples or application snippets on the detail page.",
        transform=clean_tex,
    ),
    TextFieldSpec(
        output_name="traps",
        source_filename="05_traps.tex",
        description="Cleaned common pitfalls text",
        purpose="Useful for mistake reminders and learning notes.",
        fallback_paths=(("content", "common_tricks"),),
        transform=clean_tex,
    ),
    TextFieldSpec(
        output_name="summary",
        source_filename="06_summary.tex",
        description="Cleaned summary text",
        purpose="Provides a concise end-of-page takeaway for quick review.",
        fallback_paths=(("core", "summary"),),
        transform=clean_tex,
    ),
)


def module_contains_content(module_dir: Path) -> bool:
    """Return whether a top-level directory looks like a content module."""

    try:
        for child in module_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / META_FILENAME).exists() or (child / "01_statement.tex").exists():
                return True
    except OSError:
        return False
    return False


def discover_all_module_directories(project_root: Path) -> list[Path]:
    """Auto-discover buildable module directories under the project root."""

    module_dirs: list[Path] = []
    for path in sorted(project_root.iterdir()):
        if not path.is_dir():
            continue
        if path.name in IGNORED_TOP_LEVEL_DIRS:
            continue
        if module_contains_content(path):
            module_dirs.append(path)
    return module_dirs


def resolve_target_module_directories(config: BuildConfig) -> list[Path]:
    """Resolve the final module directory list from CLI settings."""

    if not config.target_modules:
        return discover_all_module_directories(config.project_root)

    module_dirs: list[Path] = []
    missing_modules: list[str] = []
    for module_name in config.target_modules:
        module_dir = config.project_root / module_name
        if module_dir.is_dir():
            module_dirs.append(module_dir)
        else:
            missing_modules.append(module_name)

    if missing_modules:
        message = "Module directory not found: " + ", ".join(missing_modules)
        if config.strict:
            raise BuildError(message)
        LOGGER.warning(message)

    return module_dirs


def iter_item_directories(module_dir: Path) -> list[Path]:
    """Return immediate child item directories in stable sorted order."""

    return sorted(path for path in module_dir.iterdir() if path.is_dir())


def resolve_item_identity(meta: dict[str, Any], item_dir: Path) -> tuple[str, str]:
    """Resolve the stable detail record id and title."""

    item_id = str(meta.get("id") or item_dir.name)
    title_value, _ = resolve_first_value(
        meta,
        (
            ("core", "title"),
            ("title",),
        ),
    )
    title = (
        str(title_value)
        if title_value is not MISSING and title_value is not None
        else item_dir.name
    )
    return item_id, title


def matches_item_filter(
    item_dir: Path,
    item_id: str,
    target_items: tuple[str, ...],
) -> bool:
    """Return whether the current item matches the optional `--item` filter."""

    if not target_items:
        return True
    targets = set(target_items)
    return item_dir.name in targets or item_id in targets


DISPLAY_VERSION = 2
MATH_TOKEN_PATTERN = re.compile(r"@@M\d+@@")
CJK_CHAR_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]")
SIMPLE_SQRT_PATTERN = re.compile(r"\bsqrt\(\s*([^)]+?)\s*\)")

SECTION_DEFINITIONS: dict[str, tuple[str, str]] = {
    "core_formula": ("核心公式", "text"),
    "variables": ("涉及变量", "text"),
    "conditions": ("适用条件", "text"),
    "statement": ("命题表述", "theorem-list"),
    "explanation": ("理解与直觉", "text"),
    "proof": ("证明过程", "text"),
    "examples": ("例题应用", "text"),
    "traps": ("易错提醒", "text"),
    "summary": ("复盘总结", "text"),
}


def normalize_latex_for_display(latex: str) -> str:
    """Normalize latex conservatively for front-end math rendering.

    The goal is not to rewrite expressions aggressively.
    It only fixes a few common plain-text operator forms and preserves the
    mathematical structure expected by the mini-program renderer.
    """

    if not latex:
        return ""

    normalized = latex.strip()
    if normalized.startswith("$") and normalized.endswith("$") and len(normalized) >= 2:
        normalized = normalized[1:-1]

    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
    normalized = normalized.replace("!=", r"\neq")
    normalized = normalized.replace(">=", r"\geq")
    normalized = normalized.replace("<=", r"\leq")
    normalized = normalized.replace("≠", r"\neq")
    normalized = normalized.replace("≥", r"\geq")
    normalized = normalized.replace("≤", r"\leq")
    normalized = SIMPLE_SQRT_PATTERN.sub(
        lambda match: rf"\sqrt{{{match.group(1).strip()}}}",
        normalized,
    )
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n[ \t]+", "\n", normalized)
    return normalized.strip()


def looks_like_mathish(text: str) -> bool:
    """Return whether a plain string is likely intended as math content."""

    candidate = text.strip()
    if not candidate:
        return False
    if CJK_CHAR_RE.search(candidate):
        return False
    if any(token in candidate for token in ("\\", "_", "^", "=", ">", "<")):
        return True
    return bool(re.fullmatch(r"[A-Za-z0-9\s,.;:(){}\[\]+\-*/|]+", candidate))


def read_balanced_span(
    text: str,
    start_index: int,
    open_char: str,
    close_char: str,
) -> tuple[str, int]:
    """Read one balanced bracket span and return its content and end index."""

    if start_index >= len(text) or text[start_index] != open_char:
        return "", start_index

    depth = 0
    index = start_index
    while index < len(text):
        char = text[index]
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return text[start_index + 1 : index], index + 1
        index += 1

    return text[start_index + 1 :], len(text)


def protect_math_segments(text: str) -> tuple[str, dict[str, str]]:
    """Replace inline/display math with placeholders while keeping latex intact."""

    result: list[str] = []
    math_map: dict[str, str] = {}
    index = 0
    token_index = 0

    while index < len(text):
        if text.startswith("$$", index):
            end = text.find("$$", index + 2)
            if end != -1:
                token = f"@@M{token_index}@@"
                math_map[token] = normalize_latex_for_display(text[index + 2 : end])
                result.append(token)
                token_index += 1
                index = end + 2
                continue

        if text.startswith(r"\[", index):
            end = text.find(r"\]", index + 2)
            if end != -1:
                token = f"@@M{token_index}@@"
                math_map[token] = normalize_latex_for_display(text[index + 2 : end])
                result.append(token)
                token_index += 1
                index = end + 2
                continue

        if text.startswith(r"\(", index):
            end = text.find(r"\)", index + 2)
            if end != -1:
                token = f"@@M{token_index}@@"
                math_map[token] = normalize_latex_for_display(text[index + 2 : end])
                result.append(token)
                token_index += 1
                index = end + 2
                continue

        if text[index] == "$":
            end = index + 1
            while end < len(text):
                if text[end] == "$" and text[end - 1] != "\\":
                    break
                end += 1
            if end < len(text):
                token = f"@@M{token_index}@@"
                math_map[token] = normalize_latex_for_display(text[index + 1 : end])
                result.append(token)
                token_index += 1
                index = end + 1
                continue

        result.append(text[index])
        index += 1

    return "".join(result), math_map


def normalize_rich_text_markup(text: str) -> str:
    """Normalize text-only TeX markup while preserving math placeholders."""

    normalized = strip_latex_comments(text)
    normalized = normalized.replace(r"\medskip", "\n\n")
    normalized = normalized.replace(r"\smallskip", "\n\n")
    normalized = normalized.replace(r"\bigskip", "\n\n")
    normalized = normalized.replace(r"\par", "\n")
    normalized = normalized.replace(r"\\", "\n")
    normalized = strip_environment_markers(normalized)
    normalized = remove_standalone_option_lines(normalized)
    normalized = unwrap_two_argument_commands(normalized)
    normalized = unwrap_simple_commands(normalized)
    normalized = re.sub(
        r"\\(?:quad|qquad|noindent|hfill|vspace\*?|hspace\*?)",
        " ",
        normalized,
    )
    normalized = remove_remaining_commands(normalized)
    normalized = remove_curly_braces(normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def normalize_text_segment(text: str) -> str:
    """Normalize a plain-text segment without touching embedded math tokens."""

    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def protected_text_to_segments(
    protected_text: str,
    math_map: dict[str, str],
) -> list[dict[str, str]]:
    """Convert placeholder-protected mixed content into text/math segments."""

    parts = re.split(r"(@@M\d+@@)", protected_text)
    segments: list[dict[str, str]] = []

    for part in parts:
        if not part:
            continue
        if part in math_map:
            latex = normalize_latex_for_display(math_map[part])
            if latex:
                segments.append({"type": "math", "latex": latex})
            continue

        text = normalize_text_segment(part)
        if not text:
            continue

        if segments and segments[-1].get("type") == "text":
            segments[-1]["text"] = f"{segments[-1]['text']}\n{text}"
        else:
            segments.append({"type": "text", "text": text})

    return segments


def build_item_from_segments(segments: list[dict[str, str]]) -> dict[str, Any] | None:
    """Collapse a segment list into one of the supported item shapes."""

    if not segments:
        return None

    if len(segments) == 1:
        segment = segments[0]
        if segment["type"] == "text":
            return {"text": segment["text"]}
        if segment["type"] == "math":
            return {"latex": segment["latex"]}

    return {"segments": segments}


def build_rich_item_from_protected_text(
    protected_text: str,
    math_map: dict[str, str],
    *,
    label_text: str = "",
) -> dict[str, Any] | None:
    """Build one rich item from protected content, optionally with a text label."""

    normalized = normalize_rich_text_markup(protected_text)
    label = normalize_text_segment(label_text)

    if label:
        normalized = f"{label}\n{normalized}" if normalized else label

    segments = protected_text_to_segments(normalized, math_map)
    return build_item_from_segments(segments)


def extract_list_items_from_protected(
    protected_text: str,
) -> list[tuple[str, str]]:
    """Extract `\\item[...] body` or `\\item body` entries from protected text."""

    items: list[tuple[str, str]] = []
    index = 0

    while True:
        item_index = protected_text.find(r"\item", index)
        if item_index == -1:
            break

        cursor = item_index + len(r"\item")
        while cursor < len(protected_text) and protected_text[cursor].isspace():
            cursor += 1

        label = ""
        if cursor < len(protected_text) and protected_text[cursor] == "[":
            label, cursor = read_balanced_span(protected_text, cursor, "[", "]")

        next_item_index = protected_text.find(r"\item", cursor)
        body = protected_text[cursor:] if next_item_index == -1 else protected_text[cursor:next_item_index]
        items.append((label, body))

        if next_item_index == -1:
            break
        index = next_item_index

    return items


def strip_math_tokens(text: str) -> str:
    """Remove math placeholders from a text fragment before plain-text use."""

    return MATH_TOKEN_PATTERN.sub(" ", text)


def build_loose_rich_item(text: str) -> dict[str, Any] | None:
    """Build a rich item from metadata text that may contain math-like content."""

    raw_text = text.strip()
    if not raw_text:
        return None

    protected_text, math_map = protect_math_segments(raw_text)
    if math_map:
        return build_rich_item_from_protected_text(protected_text, math_map)

    math_note_match = re.match(
        r"^\s*([^()（）]+?)\s*([（(].*[）)])\s*$",
        raw_text,
    )
    if math_note_match:
        math_part = math_note_match.group(1).strip()
        note_part = math_note_match.group(2).strip()
        if looks_like_mathish(math_part):
            return {
                "segments": [
                    {"type": "math", "latex": normalize_latex_for_display(math_part)},
                    {"type": "text", "text": note_part},
                ]
            }

    if looks_like_mathish(raw_text):
        return {"latex": normalize_latex_for_display(raw_text)}

    normalized_text = normalize_text_segment(normalize_rich_text_markup(raw_text))
    return {"text": normalized_text} if normalized_text else None


def parse_generic_rich_items(raw_text: str) -> list[dict[str, Any]]:
    """Parse one raw tex field into rich items while preserving latex segments."""

    if not raw_text.strip():
        return []

    protected_text, math_map = protect_math_segments(raw_text)
    chunks = [
        chunk.strip()
        for chunk in re.split(r"\\(?:medskip|smallskip|bigskip)\s*", protected_text)
        if chunk.strip()
    ]

    items: list[dict[str, Any]] = []

    for chunk in chunks:
        first_item_index = chunk.find(r"\item")
        if first_item_index == -1:
            item = build_rich_item_from_protected_text(chunk, math_map)
            if item:
                items.append(item)
            continue

        prefix = chunk[:first_item_index]
        prefix_item = build_rich_item_from_protected_text(prefix, math_map)
        if prefix_item:
            items.append(prefix_item)

        list_text = chunk[first_item_index:]
        for label, body in extract_list_items_from_protected(list_text):
            label_text = normalize_text_segment(
                normalize_rich_text_markup(strip_math_tokens(label))
            )
            item = build_rich_item_from_protected_text(
                body,
                math_map,
                label_text=label_text,
            )
            if item:
                items.append(item)

    return items


def build_variable_entries(raw_variables: Any) -> list[dict[str, Any]]:
    """Convert meta math variables into math-aware descriptors for the front end."""

    if not isinstance(raw_variables, list):
        return []

    entries: list[dict[str, Any]] = []
    for value in raw_variables:
        if isinstance(value, str):
            latex = normalize_latex_for_display(value)
            if latex:
                entries.append({"latex": latex})
            continue

        if isinstance(value, dict):
            latex = normalize_latex_for_display(str(value.get("name", "")).strip())
            description = str(value.get("description", "")).strip()
            entry: dict[str, Any] = {}
            if latex:
                entry["latex"] = latex
            if description:
                entry["description"] = description
            if entry:
                entries.append(entry)
            continue

        text_value = str(value).strip()
        if text_value:
            entries.append({"text": text_value})

    return entries


def build_variables_section(variable_entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Build the structured `variables` section from normalized variable entries."""

    items: list[dict[str, Any]] = []
    for entry in variable_entries:
        latex = str(entry.get("latex", "")).strip()
        description = str(entry.get("description", "")).strip()
        text_value = str(entry.get("text", "")).strip()

        if latex and description:
            items.append(
                {
                    "segments": [
                        {"type": "math", "latex": latex},
                        {"type": "text", "text": f"：{description}"},
                    ]
                }
            )
        elif latex:
            items.append({"latex": latex})
        elif text_value:
            items.append({"text": text_value})

    if not items:
        return None

    title, layout = SECTION_DEFINITIONS["variables"]
    return {"key": "variables", "title": title, "layout": layout, "items": items}


def build_conditions_section(meta: dict[str, Any]) -> dict[str, Any] | None:
    """Build the structured conditions section from metadata first."""

    math_section = meta.get("math")
    if not isinstance(math_section, dict):
        return None

    conditions_value = math_section.get("conditions")
    if not isinstance(conditions_value, str):
        return None

    item = build_loose_rich_item(conditions_value)
    if not item:
        return None

    title, layout = SECTION_DEFINITIONS["conditions"]
    return {"key": "conditions", "title": title, "layout": layout, "items": [item]}


def build_core_formula_section(record: dict[str, Any]) -> dict[str, Any] | None:
    """Build a dedicated core-formula section for front-end math rendering."""

    core_formula = str(record.get("core_formula") or "").strip()
    if not core_formula:
        return None

    title, layout = SECTION_DEFINITIONS["core_formula"]
    return {
        "key": "core_formula",
        "title": title,
        "layout": layout,
        "items": [{"latex": normalize_latex_for_display(core_formula)}],
    }


def build_statement_theorem_items(
    raw_text: str,
    meta: dict[str, Any],
) -> list[dict[str, Any]]:
    """Parse theorem-list style items from `01_statement.tex`."""

    protected_text, math_map = protect_math_segments(raw_text)
    theorem_items: list[dict[str, Any]] = []

    for label, body in extract_list_items_from_protected(protected_text):
        title = normalize_text_segment(normalize_rich_text_markup(strip_math_tokens(label)))
        if not title or "条件" in title:
            continue

        formula_tokens = MATH_TOKEN_PATTERN.findall(body)
        formulas: list[str] = []
        for token in formula_tokens:
            latex = normalize_latex_for_display(math_map.get(token, ""))
            if latex and latex not in formulas:
                formulas.append(latex)

        first_formula_match = MATH_TOKEN_PATTERN.search(body)
        desc_source = body if first_formula_match is None else body[: first_formula_match.start()]
        desc_text = normalize_text_segment(
            normalize_rich_text_markup(strip_math_tokens(desc_source))
        )
        desc_text = re.sub(r"^(直观描述|说明|描述)\s*[：:]\s*", "", desc_text)

        theorem_item: dict[str, Any] = {"title": title}
        if desc_text:
            theorem_item["desc"] = desc_text
        if formulas:
            theorem_item["latex"] = r" \qquad ".join(formulas)
        theorem_items.append(theorem_item)

    if theorem_items:
        return theorem_items

    core_formula = str(get_nested_value(meta, ("math", "core_formula")) or "").strip()
    if not core_formula:
        return []

    return [
        {
            "title": "核心结论",
            "desc": "由元数据回退生成的核心不等式。",
            "latex": normalize_latex_for_display(core_formula),
        }
    ]


def build_statement_section(
    raw_text: str,
    meta: dict[str, Any],
) -> dict[str, Any] | None:
    """Build the theorem-list statement section from raw statement tex."""

    items = build_statement_theorem_items(raw_text, meta)
    if not items:
        return None

    title, layout = SECTION_DEFINITIONS["statement"]
    return {"key": "statement", "title": title, "layout": layout, "items": items}


def build_generic_section(
    key: str,
    raw_text: str,
) -> dict[str, Any] | None:
    """Build a generic rich section from raw tex content."""

    items = parse_generic_rich_items(raw_text)
    if not items:
        return None

    title, layout = SECTION_DEFINITIONS[key]
    return {"key": key, "title": title, "layout": layout, "items": items}


def build_meta_fields(
    meta: dict[str, Any],
    item_id: str,
    title: str,
) -> dict[str, Any]:
    """Build detail-page metadata fields from the whitelist configuration."""

    record: dict[str, Any] = {
        "id": item_id,
        "title": title,
    }

    for field_spec in DETAIL_META_FIELD_SPECS:
        value, source_path = resolve_first_value(meta, field_spec.source_paths)
        if value is MISSING:
            value = field_spec.default_factory()
        else:
            value = clone_json_value(value)

        if field_spec.output_name == "variables":
            value = build_variable_entries(value)

        if field_spec.required and value in (None, "", [], {}):
            source_description = ", ".join(
                ".".join(path) for path in field_spec.source_paths
            )
            raise BuildError(
                f"Required meta field '{field_spec.output_name}' is empty "
                f"(expected from {source_description})"
            )

        record[field_spec.output_name] = value

        if source_path is None:
            LOGGER.debug(
                "Meta field defaulted | field=%s | value=%r",
                field_spec.output_name,
                value,
            )
        else:
            LOGGER.debug(
                "Meta field built | field=%s | source=%s | value=%s",
                field_spec.output_name,
                ".".join(source_path),
                preview_text(stringify_text_value(value)),
            )

    return record


def build_text_field(
    raw_text: str,
    item_id: str,
    field_spec: TextFieldSpec,
) -> str:
    """Build one cleaned legacy detail text field from already loaded raw text."""

    transform = field_spec.transform or (lambda text: text)
    cleaned_text = transform(raw_text)

    if field_spec.required and not cleaned_text:
        raise BuildError(
            f"Required detail text field '{field_spec.output_name}' is empty"
        )

    LOGGER.debug(
        "Legacy text field built | item=%s | field=%s | preview=%s",
        item_id,
        field_spec.output_name,
        preview_text(cleaned_text),
    )

    return cleaned_text


def resolve_raw_text_field(
    item_dir: Path,
    meta: dict[str, Any],
    field_spec: TextFieldSpec,
    config: BuildConfig,
) -> tuple[str, str]:
    """Resolve raw content for one text field before legacy/rich branching.

    This helper exists so both pipelines read from the same upstream source:
    - legacy plain-text fields use `clean_tex(raw_text)`
    - rich sections parse directly from `raw_text`
    """

    source_path = item_dir / field_spec.source_filename
    raw_text = read_text_file(
        source_path,
        strict=config.strict,
        required=field_spec.required,
    )

    source_used = source_path.name if raw_text.strip() else ""
    if not raw_text.strip() and field_spec.fallback_paths:
        fallback_value, fallback_path = resolve_first_value(meta, field_spec.fallback_paths)
        if fallback_value is not MISSING:
            raw_text = stringify_text_value(fallback_value)
            source_used = ".".join(fallback_path or ())

    if field_spec.required and not raw_text.strip():
        raise BuildError(
            f"Required detail text field '{field_spec.output_name}' is empty: {item_dir}"
        )

    LOGGER.debug(
        "Raw text field resolved | field=%s | source=%s | preview=%s",
        field_spec.output_name,
        source_used or "<empty>",
        preview_text(raw_text),
    )
    return raw_text, source_used or "<empty>"


def collect_raw_text_fields(
    item_dir: Path,
    meta: dict[str, Any],
    config: BuildConfig,
) -> dict[str, str]:
    """Load all raw text field inputs once for both legacy and rich pipelines."""

    raw_fields: dict[str, str] = {}
    for field_spec in DETAIL_TEXT_FIELD_SPECS:
        raw_text, _source_used = resolve_raw_text_field(
            item_dir=item_dir,
            meta=meta,
            field_spec=field_spec,
            config=config,
        )
        raw_fields[field_spec.output_name] = raw_text
    return raw_fields


def build_structured_sections(
    meta: dict[str, Any],
    record: dict[str, Any],
    raw_fields: dict[str, str],
) -> list[dict[str, Any]]:
    """Build latex-first sections from raw tex and structured metadata."""

    sections: list[dict[str, Any]] = []

    core_formula_section = build_core_formula_section(record)
    if core_formula_section:
        sections.append(core_formula_section)

    variables_section = build_variables_section(
        record.get("variables", []) if isinstance(record.get("variables"), list) else []
    )
    if variables_section:
        sections.append(variables_section)

    conditions_section = build_conditions_section(meta)
    if conditions_section:
        sections.append(conditions_section)

    statement_section = build_statement_section(raw_fields.get("statement", ""), meta)
    if statement_section:
        sections.append(statement_section)

    for key in ("explanation", "proof", "examples", "traps", "summary"):
        section = build_generic_section(key, raw_fields.get(key, ""))
        if section:
            sections.append(section)

    return sections


def build_detail_record(
    item_dir: Path,
    meta: dict[str, Any],
    item_id: str,
    title: str,
    config: BuildConfig,
) -> dict[str, Any]:
    """Build the full detail-page record for one item."""

    raw_fields = collect_raw_text_fields(item_dir, meta, config)
    record = build_meta_fields(meta, item_id, title)
    for field_spec in DETAIL_TEXT_FIELD_SPECS:
        record[field_spec.output_name] = build_text_field(
            raw_text=raw_fields.get(field_spec.output_name, ""),
            item_id=item_id,
            field_spec=field_spec,
        )

    record["display_version"] = DISPLAY_VERSION
    record["sections"] = build_structured_sections(meta, record, raw_fields)
    return record


def process_module(
    module_dir: Path,
    config: BuildConfig,
) -> tuple[str, dict[str, dict[str, Any]], ModuleStats]:
    """Process one module directory into `{item_id: detail_record}` output."""

    module_name = module_dir.name
    stats = ModuleStats(module_name=module_name)
    result: dict[str, dict[str, Any]] = {}

    LOGGER.info("Module start | %s", module_name)

    for item_dir in iter_item_directories(module_dir):
        stats.scanned_items += 1

        try:
            meta = read_json_file(item_dir / META_FILENAME, strict=config.strict)
            item_id, title = resolve_item_identity(meta, item_dir)

            if not matches_item_filter(item_dir, item_id, config.target_items):
                stats.filtered_items += 1
                LOGGER.debug(
                    "Item filtered | module=%s | item_dir=%s | item_id=%s",
                    module_name,
                    item_dir.name,
                    item_id,
                )
                continue

            if item_id in result:
                raise BuildError(
                    f"Duplicate item id '{item_id}' found in module '{module_name}'."
                )

            result[item_id] = build_detail_record(
                item_dir=item_dir,
                meta=meta,
                item_id=item_id,
                title=title,
                config=config,
            )
            stats.built_items += 1

        except Exception as exc:
            stats.skipped_items += 1
            if config.strict:
                raise
            LOGGER.warning(
                "Skip item | module=%s | item=%s | reason=%s",
                module_name,
                item_dir.name,
                exc,
            )

    LOGGER.info(
        "Module summary | module=%s | scanned=%d | built=%d | filtered=%d | skipped=%d",
        module_name,
        stats.scanned_items,
        stats.built_items,
        stats.filtered_items,
        stats.skipped_items,
    )

    return module_name, result, stats


def build_schema_comment() -> str:
    """Generate an output-file header that documents schema and intent."""

    lines: list[str] = [
        "/**",
        " * Auto-generated by scripts/build_detail_page_js.py.",
        " *",
        " * This file is for the mini-program detail page only.",
        " * It intentionally excludes search-only metadata such as:",
        " *   - search",
        " *   - searchmeta",
        " *   - ranking",
        " *   - pinyin / pinyinAbbr and other search keys under search.*",
        " *",
        " * Top-level export:",
        " *   module.exports = { [id]: DetailRecord }",
        " *",
        " * DetailRecord core fields:",
        " *   - id: stable content id from meta.json:id",
        " *   - title: display title from meta.json:core.title",
        " *   - display_version: currently 2, meaning structured latex-first sections are available",
        " *   - sections: structured display sections built from raw tex before clean_tex",
        " *",
        " * DetailRecord metadata fields:",
    ]

    for field_spec in DETAIL_META_FIELD_SPECS:
        source_text = " | ".join(".".join(path) for path in field_spec.source_paths)
        lines.append(
            f" *   - {field_spec.output_name}: {field_spec.description}; "
            f"source={source_text}; why={field_spec.purpose}"
        )
        if field_spec.output_name == "variables":
            lines.append(
                " *     variables shape: [{ latex, description? }] so the front end can render variables as math."
            )

    lines.append(" *")
    lines.append(" * DetailRecord cleaned text fields:")
    for field_spec in DETAIL_TEXT_FIELD_SPECS:
        fallback_text = (
            " | ".join(".".join(path) for path in field_spec.fallback_paths)
            if field_spec.fallback_paths
            else "none"
        )
        lines.append(
            f" *   - {field_spec.output_name}: {field_spec.description}; "
            f"source={field_spec.source_filename}; fallback={fallback_text}; "
            f"why={field_spec.purpose}"
        )

    lines.extend(
        [
            " *",
            " * Structured sections schema:",
            " *   - Section = { key, title, layout, items }",
            " *   - Supported item forms:",
            " *     1. { text: string }",
            " *     2. { latex: string }",
            " *     3. { segments: [{ type: 'text', text } | { type: 'math', latex }] }",
            " *     4. theorem-list item: { title, desc?, latex }",
            " *   - Important layouts used by this builder:",
            " *     - text",
            " *     - theorem-list",
            " *   - Legacy plain-text fields remain in the record for compatibility and debugging.",
        ]
    )

    lines.extend(
        [
            " */",
            "",
        ]
    )
    return "\n".join(lines)


def write_module_js(
    module_name: str,
    data: dict[str, dict[str, Any]],
    output_dir: Path,
) -> Path:
    """Write one module output file in a debug-friendly JS format."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{module_name}.js"
    js_content = build_schema_comment() + "module.exports = " + json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
    ) + "\n"
    output_path.write_text(js_content, encoding="utf-8")
    return output_path


def run_build(config: BuildConfig) -> None:
    """Run the full detail-page build workflow with clear stage logs."""

    LOGGER.info("Step 1/5 | Resolve target modules")
    module_dirs = resolve_target_module_directories(config)
    if not module_dirs:
        message = "No module directories matched the current configuration."
        if config.strict:
            raise BuildError(message)
        LOGGER.warning(message)
        return

    LOGGER.info("Project root: %s", config.project_root)
    LOGGER.info("Output dir: %s", config.output_dir)
    LOGGER.info(
        "Target modules: %s",
        ", ".join(config.target_modules) if config.target_modules else "auto discover",
    )
    if config.target_items:
        LOGGER.info("Target items: %s", ", ".join(config.target_items))

    LOGGER.info("Step 2/5 | Build detail-page records")

    total_modules = 0
    total_items = 0
    total_filtered = 0
    total_skipped = 0

    pending_outputs: list[tuple[str, dict[str, dict[str, Any]]]] = []
    for module_index, module_dir in enumerate(module_dirs, start=1):
        LOGGER.info(
            "Module progress | %d/%d | %s",
            module_index,
            len(module_dirs),
            module_dir.name,
        )
        module_name, data, stats = process_module(module_dir, config)
        pending_outputs.append((module_name, data))
        total_modules += 1
        total_items += stats.built_items
        total_filtered += stats.filtered_items
        total_skipped += stats.skipped_items

    LOGGER.info("Step 3/5 | Validate build results")
    LOGGER.info(
        "Build stats | modules=%d | items=%d | filtered=%d | skipped=%d",
        total_modules,
        total_items,
        total_filtered,
        total_skipped,
    )

    LOGGER.info("Step 4/5 | Write JS files")
    written_files: list[Path] = []
    for module_name, data in pending_outputs:
        if config.dry_run:
            LOGGER.info(
                "[dry-run] Skip write | module=%s | items=%d",
                module_name,
                len(data),
            )
            continue

        output_path = write_module_js(module_name, data, config.output_dir)
        written_files.append(output_path)
        LOGGER.info(
            "Wrote detail file | module=%s | path=%s | items=%d",
            module_name,
            output_path,
            len(data),
        )

    LOGGER.info("Step 5/5 | Finished")
    if written_files:
        for path in written_files:
            LOGGER.info("Output ready | %s | bytes=%d", path, path.stat().st_size)
    elif config.dry_run:
        LOGGER.info("Dry-run finished without writing output files.")


def main() -> int:
    """CLI entry point."""

    configure_console_encoding()
    args = parse_args()
    configure_logging(args.debug)
    config = build_config_from_args(args)

    try:
        run_build(config)
        return 0
    except BuildError as exc:
        LOGGER.error("%s", exc)
        return 1
    except Exception:
        LOGGER.exception("Unexpected build failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
