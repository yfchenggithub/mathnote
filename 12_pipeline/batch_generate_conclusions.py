#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch process pending conclusion rows from module readme.md files.

Each pending markdown table row is treated as one conclusion. The script keeps
formula pipes such as P(B|A), strips trailing star-rating cells before the LLM
prompt, writes validated LaTeX to source.tex, runs the pipeline with an explicit
module selector, then publishes the generated NEW_ID.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = PROJECT_ROOT / "12_pipeline"
SOURCE_TEX = PIPELINE_DIR / "source.tex"
CONFIG_DIR = PIPELINE_DIR / "config"
MODULE_PREFIX_MAP_PATH = CONFIG_DIR / "module_prefix_map.json"
APP_CONFIG_PATH = CONFIG_DIR / "app_config.json"
LOG_PATH = PROJECT_ROOT / "batch_generate.log"
STATE_PATH = PROJECT_ROOT / "batch_generate_state.jsonl"
GENERATED_SOURCE_DIR = PIPELINE_DIR / "generated_sources"
PENDING_MARKER = "待整理结论"
DRY_RUN_MODE = False
DEFAULT_TIMEOUT_SECONDS = 3600
POST_TIMEOUT_RECOVERY_WAIT_SECONDS = 900
POST_TIMEOUT_RECOVERY_POLL_SECONDS = 15
LECTURE_FILES = (
    "01_statement.tex",
    "02_explanation.tex",
    "03_proof.tex",
    "04_examples.tex",
    "05_traps.tex",
    "06_summary.tex",
)
L6_DIRNAME_PATTERN_TEMPLATE = r"^{item_id}_[a-z0-9]+(?:_[a-z0-9]+)*$"
MATH_DELIMITER_PATTERN = re.compile(
    r"(\\\[.*?\\\]|\\\(.*?\\\)|\$\$.*?\$\$|(?<!\\)\$(?!\$).+?(?<!\\)\$|"
    r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?)\})",
    re.DOTALL,
)
SOURCE_REQUIRED_LABELS = (
    "结论名称",
    "适用条件",
    "变量说明",
    "核心公式",
    "使用场景",
    "简单例子",
)

MODULE_DIRS = [
    "00_set", "01_function", "02_sequence", "03_conic",
    "04_vector", "05_geometry-solid", "06_probability-stat",
    "07_inequality", "08_trigonometry", "09_geometry-plane",
    "10_junior_basics",
]

NEW_ID_PATTERN = re.compile(r"^NEW_ID=([A-Za-z]\d{3})\s*$", re.MULTILINE)
PDF_READY_PATTERN = re.compile(r"^PDF_READY=(.+?)\s*$", re.MULTILINE)
PDF_FAILURE_LOG_PATTERN = re.compile(
    r"(12_pipeline[/\\]output[/\\][A-Za-z]\d{3}[/\\]pdf_compile_error_attempt\d+\.log)"
)

# Match conclusion table rows: | I043 | title | ...
CONCLUSION_ROW_PATTERN = re.compile(
    r"^\|\s*([A-Z]\d{3})\s*\|\s*(.+?)\s*(?:\|.*)?$"
)

def build_latex_prompt(title: str, module_name: str) -> str:
    """Build the LaTeX generation prompt with proper brace escaping."""
    return (
        "你是高考数学二级结论的LaTeX撰写专家。请根据以下结论主题，生成一个简洁完整的LaTeX文档。\n"
        "\n"
        "要求：\n"
        "1. 必须包含数学公式（使用 \\[ ... \\] 或 \\( ... \\) ）\n"
        "2. 内容要包括：结论的数学表述、关键公式、简要说明\n"
        "3. 使用 \\textbf{} 标记重点\n"
        "4. 使用 \\boxed{} 框出核心公式\n"
        "5. 简洁精炼，不要冗长解释\n"
        "6. 不要使用 \\documentclass、\\begin{document} 等包装\n"
        "7. 只输出纯LaTeX内容\n"
        "\n"
        f"结论主题：{title}\n"
        f"所属模块：{module_name}\n"
        "\n"
        "请直接输出LaTeX代码："
    )


def load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_module_prefix_map() -> dict[str, str]:
    if MODULE_PREFIX_MAP_PATH.exists():
        return load_json(MODULE_PREFIX_MAP_PATH)
    return {}


def load_api_config() -> dict[str, Any]:
    return load_json(APP_CONFIG_PATH)


def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_readme(module_dir: str) -> list[dict[str, str]]:
    """
    Parse a module's readme.md and extract pending conclusions.
    Returns list of {id, title, module_dir} dicts.
    """
    readme_path = PROJECT_ROOT / module_dir / "readme.md"
    if not readme_path.exists():
        log(f"[skip] No readme.md in {module_dir}")
        return []

    content = readme_path.read_text(encoding="utf-8")

    # Split by sections, find all "待整理结论" sections
    lines = content.split("\n")
    pending_conclusions: list[dict[str, str]] = []
    in_pending_section = False

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped.startswith("## ") and "待整理结论" in stripped:
            in_pending_section = True
            continue
        elif stripped.startswith("## ") and "待整理结论" not in stripped:
            in_pending_section = False
            continue
        elif stripped.startswith("---"):
            # Horizontal rule may end a section, but "待整理" sections
            # often have multiple subsections separated by ---
            # Keep in_pending_section = True; only ## headers flip it
            pass

        if not in_pending_section:
            continue

        # Match table rows: | I043 | title text | ... |
        m = CONCLUSION_ROW_PATTERN.match(stripped)
        if m:
            conclusion_id = m.group(1)
            title = m.group(2).strip()
            # Remove trailing | if present
            title = re.sub(r"\s*\|\s*$", "", title)
            pending_conclusions.append({
                "id": conclusion_id,
                "title": title,
                "module_dir": module_dir,
            })

    log(f"[parse] {module_dir}: found {len(pending_conclusions)} pending conclusions")
    return pending_conclusions


def get_module_name(module_dir: str) -> str:
    """Convert directory name like '07_inequality' to '不等式'."""
    name_map = {
        "00_set": "集合与逻辑",
        "01_function": "函数与导数",
        "02_sequence": "数列",
        "03_conic": "圆锥曲线",
        "04_vector": "平面向量",
        "05_geometry-solid": "立体几何",
        "06_probability-stat": "概率与统计",
        "07_inequality": "不等式",
        "08_trigonometry": "三角函数",
        "09_geometry-plane": "平面几何",
        "10_junior_basics": "初中基础",
    }
    return name_map.get(module_dir, module_dir)


def generate_latex_via_llm(
    conclusion: dict[str, str],
    api_config: dict[str, Any],
    model_config: dict[str, Any],
) -> str | None:
    """Generate LaTeX content for a conclusion using the LLM API."""
    module_name = get_module_name(conclusion["module_dir"])

    prompt = build_latex_prompt(
        title=f"{conclusion['id']} {conclusion['title']}",
        module_name=module_name,
    )

    model = model_config.get("flash", model_config.get("default", "deepseek-v4-flash"))

    client = OpenAI(
        api_key=api_config["api_key"],
        base_url=api_config["base_url"],
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=180,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except Exception as e:
            log(f"[llm] attempt {attempt + 1}/3 failed for {conclusion['id']}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def ensure_formulas_in_latex(latex: str) -> bool:
    """Check that the generated LaTeX contains math formulas."""
    has_display = "\\[" in latex or "$$" in latex or "\\begin{" in latex
    has_inline = "\\(" in latex or "$" in latex
    return has_display or has_inline


def run_pipeline(python_exe: str, skip_git_commit: bool = False) -> tuple[str | None, str | None]:
    """
    Run run_source_to_pdf.py and capture NEW_ID.
    Returns (new_id, error_msg).
    """
    script = PIPELINE_DIR / "run_source_to_pdf.py"
    cmd = [python_exe, str(script)]
    if skip_git_commit:
        cmd.append("--skip-git-commit")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=600,  # 10 min timeout
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            return None, f"Pipeline failed (rc={result.returncode}): {stdout[-500:]}"

        m = NEW_ID_PATTERN.search(stdout)
        if m:
            return m.group(1).upper(), None
        else:
            return None, f"Cannot parse NEW_ID from output: {stdout[-500:]}"

    except subprocess.TimeoutExpired:
        return None, "Pipeline timed out (>10 min)"
    except Exception as e:
        return None, f"Pipeline error: {e}"


def run_incremental_publish(python_exe: str, new_id: str, no_deploy: bool = False) -> bool:
    """Run incremental_publish.py for the given ID."""
    script = PROJECT_ROOT / "scripts" / "incremental_publish.py"
    cmd = [python_exe, str(script), new_id]
    if no_deploy:
        cmd.append("--no-deploy")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=600,
        )
        if result.returncode != 0:
            log(f"[publish] incremental_publish.py failed for {new_id}: {result.stderr[-300:]}")
            return False
        log(f"[publish] {new_id} published successfully")
        return True
    except subprocess.TimeoutExpired:
        log(f"[publish] incremental_publish.py timed out for {new_id}")
        return False
    except Exception as e:
        log(f"[publish] incremental_publish.py error for {new_id}: {e}")
        return False


def process_one_conclusion(
    conclusion: dict[str, str],
    api_config: dict[str, Any],
    model_config: dict[str, Any],
    python_exe: str,
    dry_run: bool,
    skip_git_commit: bool = False,
    no_deploy: bool = False,
) -> bool:
    """Process a single conclusion through the full pipeline."""
    cid = conclusion["id"]
    title = conclusion["title"]

    log(f"[start] {cid}: {title}")

    # Step 1: Generate LaTeX
    log(f"[latex] Generating LaTeX for {cid}...")
    latex_content = generate_latex_via_llm(conclusion, api_config, model_config)

    if not latex_content:
        log(f"[fail] {cid}: LaTeX generation returned empty")
        return False

    if not ensure_formulas_in_latex(latex_content):
        log(f"[warn] {cid}: Generated LaTeX may lack formulas, but proceeding")

    # Step 2: Write to source.tex
    SOURCE_TEX.write_text(latex_content, encoding="utf-8")
    log(f"[write] source.tex updated ({len(latex_content)} chars)")

    if dry_run:
        log(f"[dry-run] {cid}: would run pipeline + incremental_publish")
        return True

    # Step 3: Run pipeline
    log(f"[pipeline] Running run_source_to_pdf.py for {cid}...")
    new_id, error = run_pipeline(python_exe, skip_git_commit=skip_git_commit)

    if error:
        log(f"[fail] {cid}: {error}")
        return False

    if new_id != cid:
        log(f"[warn] {cid}: Expected ID {cid} but pipeline produced {new_id}")

    # Step 4: Run incremental_publish
    log(f"[publish] Running incremental_publish.py for {new_id}...")
    published = run_incremental_publish(python_exe, new_id, no_deploy=no_deploy)

    if published:
        log(f"[done] {cid} → {new_id}: Complete!")
    else:
        log(f"[warn] {cid} → {new_id}: Pipeline OK but incremental_publish may have issues")

    return published


def get_existing_ids() -> set[str]:
    """Collect all existing conclusion IDs across all module directories."""
    existing: set[str] = set()
    for module_dir in MODULE_DIRS:
        module_path = PROJECT_ROOT / module_dir
        if not module_path.is_dir():
            continue
        for item in module_path.iterdir():
            if item.is_dir():
                # Match ID pattern at start of directory name
                m = re.match(r"^([A-Z]\d{3})", item.name.upper())
                if m:
                    existing.add(m.group(1))
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch generate pending conclusions from readme.md files"
    )
    parser.add_argument(
        "--module", "-m",
        default=None,
        help="Process a single module directory (e.g., 07_inequality)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without executing pipeline",
    )
    parser.add_argument(
        "--start-from",
        default=None,
        help="Resume from a specific conclusion ID (e.g., I043)",
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable path",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip conclusions that already have directories (default: True)",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Process all pending conclusions, even if directories exist",
    )
    parser.add_argument(
        "--skip-git-commit",
        action="store_true",
        help="Pass --skip-git-commit to run_source_to_pdf.py",
    )
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Pass --no-deploy to incremental_publish.py (skip remote deployment)",
    )
    args = parser.parse_args()

    # Load configs
    try:
        api_config_raw = load_api_config()
        api_config = api_config_raw["api"]
        model_config = api_config_raw["model"]
    except Exception as e:
        log(f"[error] Cannot load API config: {e}")
        return 1

    # Determine which modules to process
    if args.module:
        modules = [args.module]
        if args.module not in MODULE_DIRS:
            log(f"[error] Unknown module: {args.module}")
            log(f"[info] Available: {MODULE_DIRS}")
            return 1
    else:
        modules = MODULE_DIRS

    # Collect all pending conclusions
    all_conclusions: list[dict[str, str]] = []
    for module_dir in modules:
        conclusions = parse_readme(module_dir)
        all_conclusions.extend(conclusions)

    if not all_conclusions:
        log("[info] No pending conclusions found.")
        return 0

    log(f"[info] Total pending conclusions: {len(all_conclusions)}")

    # Filter existing if requested
    if args.skip_existing and not args.force_all:
        existing_ids = get_existing_ids()
        filtered = [c for c in all_conclusions if c["id"] not in existing_ids]
        skipped = len(all_conclusions) - len(filtered)
        if skipped > 0:
            log(f"[info] Skipping {skipped} already-existing conclusions")
        all_conclusions = filtered

    if not all_conclusions:
        log("[info] All pending conclusions already exist. Nothing to do.")
        return 0

    log(f"[info] Will process {len(all_conclusions)} conclusions")

    # Apply --start-from filter
    if args.start_from:
        start_id = args.start_from.upper()
        filtered = []
        found = False
        for c in all_conclusions:
            if c["id"] == start_id:
                found = True
            if found:
                filtered.append(c)
        if not found:
            log(f"[warn] --start-from {start_id} not found, processing all")
        else:
            all_conclusions = filtered
            log(f"[info] Resuming from {start_id}, {len(all_conclusions)} remaining")

    # Process each conclusion
    success = 0
    fail = 0
    total = len(all_conclusions)

    for i, conclusion in enumerate(all_conclusions):
        log(f"\n{'='*60}")
        log(f"[progress] {i + 1}/{total}: {conclusion['id']} {conclusion['title'][:60]}")
        log(f"{'='*60}")

        ok = process_one_conclusion(
            conclusion,
            api_config,
            model_config,
            args.python_exe,
            args.dry_run,
            skip_git_commit=args.skip_git_commit,
            no_deploy=args.no_deploy,
        )
        if ok:
            success += 1
        else:
            fail += 1

        # Small delay between conclusions to avoid API rate limits
        if not args.dry_run and i < total - 1:
            time.sleep(3)

    log(f"\n{'='*60}")
    log(f"[summary] Done! Success: {success}, Failed: {fail}, Total: {total}")
    log(f"{'='*60}")

    return 0 if fail == 0 else 1


ROW_ID_PATTERN = re.compile(r"^\|\s*([A-Z]\d{3})\s*\|", re.IGNORECASE)
STAR_RATING_CELL_PATTERN = re.compile(
    r"^(?P<head>\|.*)\|\s*(?P<rating>[^|]*[\u2b50\u2605\u2606][^|]*)\|\s*$"
)

MODULE_NAME_MAP = {
    "00_set": "集合与逻辑",
    "01_function": "函数与导数",
    "02_sequence": "数列",
    "03_conic": "圆锥曲线",
    "04_vector": "平面向量",
    "05_geometry-solid": "立体几何",
    "06_probability-stat": "概率与统计",
    "07_inequality": "不等式",
    "08_trigonometry": "三角函数",
    "09_geometry-plane": "平面几何",
    "10_junior_basics": "初中基础",
}


def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    encoding = sys.stdout.encoding or "utf-8"
    print(line.encode(encoding, errors="replace").decode(encoding, errors="replace"))
    if not DRY_RUN_MODE:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_text_file(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode file with supported encodings: {path}")


def normalize_timeout(value: int) -> int | None:
    if value < 0:
        raise ValueError("--timeout must be >= 0")
    return None if value == 0 else value


def describe_timeout(timeout_seconds: int | None) -> str:
    if timeout_seconds is None:
        return "disabled"
    return f"{timeout_seconds}s"


def describe_sequence(values: Iterable[Any], empty: str = "(none)") -> str:
    items = [str(value) for value in values if str(value)]
    return ", ".join(items) if items else empty


def log_config_snapshot(
    phase: str,
    args: argparse.Namespace,
    *,
    timeout_seconds: int | None,
    modules: list[str],
    selected_ids: list[str],
    total_before_filters: int,
    selected_total: int,
    skipped_existing: int,
    resume_publish: int,
    api_config: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
    backup_path: Path | None = None,
    result: dict[str, Any] | None = None,
) -> None:
    """Log the effective run configuration without leaking secrets."""
    api_config = api_config or {}
    model_config = model_config or {}
    latex_model = model_config.get(
        "pro",
        model_config.get("flash", model_config.get("default", "(not loaded)")),
    )

    log(f"[config:{phase}] ------------------------------------------------------------")
    log(f"[config:{phase}] project_root={PROJECT_ROOT}")
    log(f"[config:{phase}] app_config={APP_CONFIG_PATH.relative_to(PROJECT_ROOT)}")
    log(f"[config:{phase}] module_prefix_map={MODULE_PREFIX_MAP_PATH.relative_to(PROJECT_ROOT)}")
    log(
        f"[config:{phase}] dry_run={args.dry_run}, python_exe={args.python_exe}, "
        f"timeout={describe_timeout(timeout_seconds)}"
    )
    log(
        f"[config:{phase}] module_arg={args.module or '(all)'}, "
        f"resolved_modules={describe_sequence(modules)}"
    )
    log(
        f"[config:{phase}] ids={describe_sequence(selected_ids, '(all)')}, "
        f"start_from={args.start_from or '(none)'}"
    )
    log(
        f"[config:{phase}] skip_existing={args.skip_existing}, force_all={args.force_all}, "
        f"force_regenerate={args.force_regenerate}"
    )
    log(
        f"[config:{phase}] continue_on_error={args.continue_on_error}, "
        f"skip_git_commit={args.skip_git_commit}, no_deploy={args.no_deploy}, "
        f"allow_id_mismatch={args.allow_id_mismatch}"
    )
    log(
        f"[config:{phase}] rows_before_filters={total_before_filters}, "
        f"selected_rows={selected_total}, skipped_existing={skipped_existing}, "
        f"resume_publish={resume_publish}"
    )
    log(
        f"[config:{phase}] state_path={STATE_PATH.relative_to(PROJECT_ROOT)}, "
        f"generated_source_dir={GENERATED_SOURCE_DIR.relative_to(PROJECT_ROOT)}"
    )
    if args.dry_run:
        log(f"[config:{phase}] api_provider=(not loaded: dry-run), latex_model=(not loaded: dry-run)")
    else:
        log(
            f"[config:{phase}] api_provider={api_config.get('provider', '(missing)')}, "
            f"base_url={api_config.get('base_url', '(missing)')}, latex_model={latex_model}"
        )
        log(f"[config:{phase}] source_backup={backup_path.relative_to(PROJECT_ROOT) if backup_path else '(none)'}")
    if result:
        result_text = ", ".join(f"{key}={value}" for key, value in result.items())
        log(f"[config:{phase}] result={result_text}")
    log(f"[config:{phase}] ------------------------------------------------------------")


def timeout_error(label: str, timeout_seconds: int | None) -> str:
    if timeout_seconds is None:
        return f"{label} timed out"
    return f"{label} timed out (>{timeout_seconds}s)"


def is_pdf_compile_failure(error: str | None) -> bool:
    if not error:
        return False
    markers = (
        "PDF_COMPILE_FAILED",
        "PDF_COMPILE_FAILED_LOG=",
        "Step 5/7 build PDF failed",
        "Step 5/7 build PDF",
        "PDF failure log:",
        "build_conclusion_pdfs.py",
    )
    return any(marker in error for marker in markers)


def extract_pdf_failure_log(error: str | None) -> str:
    if not error:
        return ""
    match = PDF_FAILURE_LOG_PATTERN.search(error)
    return match.group(1).replace("\\", "/") if match else ""


def compute_source_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def load_module_prefix_map() -> dict[str, str]:
    raw = load_json(MODULE_PREFIX_MAP_PATH)
    result: dict[str, str] = {}
    for module_dir, prefix in raw.items():
        module_text = str(module_dir).strip()
        prefix_text = str(prefix).strip().upper()
        if module_text and re.fullmatch(r"[A-Z]", prefix_text):
            result[module_text] = prefix_text
            continue
        raise ValueError(f"Invalid module prefix mapping: {module_dir!r} -> {prefix!r}")
    return result


def record_state(conclusion: dict[str, Any], status: str, **extra: Any) -> None:
    if DRY_RUN_MODE:
        return
    payload = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "id": conclusion.get("id"),
        "module_dir": conclusion.get("module_dir"),
        "line_number": conclusion.get("line_number"),
        "source_line": conclusion.get("source_line"),
        "llm_source_line": conclusion.get("llm_source_line"),
    }
    payload.update(extra)
    with open(STATE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def remember_failure(conclusion: dict[str, Any], stage: str, error: str) -> None:
    conclusion["_last_failure_stage"] = stage
    conclusion["_last_error"] = error


def collapse_for_log(text: str, limit: int = 90) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


def strip_star_rating_cell(row: str) -> str:
    """Remove the trailing value/rating cell before sending a row to the LLM."""
    text = row.strip()
    match = STAR_RATING_CELL_PATTERN.match(text)
    if match:
        return match.group("head").rstrip() + " |"
    return re.sub(r"[\u2b50\u2605\u2606]+", "", text).strip()


def parse_readme(module_dir: str) -> list[dict[str, Any]]:
    """
    Extract one pending conclusion per table row.

    Keep the whole row as source text. Formula text often contains markdown pipe
    characters such as |f(x)| or P(B|A), so splitting table columns is unsafe.
    """
    readme_path = PROJECT_ROOT / module_dir / "readme.md"
    if not readme_path.exists():
        log(f"[skip] No readme.md in {module_dir}")
        return []

    content = read_text_file(readme_path)
    pending_conclusions: list[dict[str, Any]] = []
    in_pending_section = False

    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        if stripped.startswith("## "):
            in_pending_section = PENDING_MARKER in stripped
            continue

        if not in_pending_section:
            continue

        match = ROW_ID_PATTERN.match(stripped)
        if not match:
            continue

        pending_conclusions.append(
            {
                "id": match.group(1).upper(),
                "module_dir": module_dir,
                "line_number": line_number,
                "source_line": stripped,
                "llm_source_line": strip_star_rating_cell(stripped),
            }
        )

    log(f"[parse] {module_dir}: found {len(pending_conclusions)} pending rows")
    return pending_conclusions


def get_module_name(module_dir: str) -> str:
    return MODULE_NAME_MAP.get(module_dir, module_dir)


def build_latex_prompt(
    source_line: str,
    module_name: str,
    feedback: str | None = None,
) -> str:
    prompt = (
        "你是高考数学二级结论的 LaTeX 源材料整理专家。请根据下面 readme.md "
        "中的一整行待整理结论，生成一个短而完整、信息密度高、可进入后续流水线处理的 LaTeX 片段。\n\n"
        "要求：\n"
        "1. 必须包含明确的数学公式，优先使用 \\[ ... \\] 展示核心公式。\n"
        "2. 必须按下面 6 个小节输出，且小节标题必须保留：\n"
        "   \\textbf{结论名称：}、\\textbf{适用条件：}、\\textbf{变量说明：}、"
        "\\textbf{核心公式：}、\\textbf{使用场景：}、\\textbf{简单例子：}。\n"
        "3. \\textbf{核心公式：} 中必须使用 \\boxed{} 框出主公式。\n"
        "4. \\textbf{简单例子：} 必须给一个可手算、可验证的小例子；若原结论不适合数值例子，给一个典型使用场景。\n"
        "5. 内容要短而完整，建议 12 到 28 行；不要写长证明，不要扩展成讲义。\n"
        "6. 不编造与该行无关的新结论；输入信息不足时，用保守表述。\n"
        "7. 不要使用 \\documentclass、\\begin{document}、\\end{document}。\n"
        "8. 不要输出 Markdown 代码围栏，只输出纯 LaTeX 内容。\n"
        "9. 行首编号只用于理解，不要把编号当作正文标题的一部分。\n"
        "10. 不要输出星级、来源价值评价或 emoji。\n"
    )
    if feedback:
        prompt += f"\n上一次输出存在问题：{feedback}\n请修正后重新输出。\n"

    prompt += (
        f"\n所属模块：{module_name}\n"
        "readme 原始行：\n"
        f"{source_line}\n\n"
        "请直接输出 LaTeX 代码："
    )
    return prompt


def clean_latex_response(content: str) -> str:
    text = content.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def ensure_formulas_in_latex(latex: str) -> bool:
    return bool(MATH_DELIMITER_PATTERN.search(latex))


def validate_latex_content(latex: str) -> list[str]:
    problems: list[str] = []
    if not latex.strip():
        problems.append("empty output")
    if "```" in latex:
        problems.append("contains markdown code fence")
    if "\\documentclass" in latex or "\\begin{document}" in latex or "\\end{document}" in latex:
        problems.append("contains document wrapper")
    if not ensure_formulas_in_latex(latex):
        problems.append("missing math formula delimiters")
    missing_labels = [label for label in SOURCE_REQUIRED_LABELS if label not in latex]
    if missing_labels:
        problems.append("missing required source labels: " + ", ".join(missing_labels))
    if "\\boxed" not in latex:
        problems.append("missing boxed core formula")
    return problems


def generate_latex_via_llm(
    conclusion: dict[str, Any],
    api_config: dict[str, Any],
    model_config: dict[str, Any],
    max_attempts: int = 3,
) -> tuple[str | None, str | None]:
    from openai import OpenAI

    module_name = get_module_name(str(conclusion["module_dir"]))
    model = model_config.get("pro", model_config.get("flash", model_config.get("default", "deepseek-v4-flash")))
    client = OpenAI(api_key=api_config["api_key"], base_url=api_config["base_url"])
    feedback: str | None = None

    for attempt in range(1, max_attempts + 1):
        prompt = build_latex_prompt(
            source_line=str(conclusion.get("llm_source_line") or conclusion["source_line"]),
            module_name=module_name,
            feedback=feedback,
        )
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=180,
            )
            raw_content = response.choices[0].message.content
            latex = clean_latex_response(raw_content if isinstance(raw_content, str) else "")
            problems = validate_latex_content(latex)
            if not problems:
                return latex, None

            feedback = "; ".join(problems)
            log(
                f"[llm] attempt {attempt}/{max_attempts} invalid for "
                f"{conclusion['id']}: {feedback}"
            )
        except Exception as exc:
            feedback = f"API error: {exc}"
            log(
                f"[llm] attempt {attempt}/{max_attempts} failed for "
                f"{conclusion['id']}: {exc}"
            )

        if attempt < max_attempts:
            time.sleep(2 ** (attempt - 1))

    return None, feedback or "LaTeX generation failed"


def backup_source_tex() -> Path | None:
    if not SOURCE_TEX.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = SOURCE_TEX.with_name(f"source.tex.batch_backup.{timestamp}")
    shutil.copy2(SOURCE_TEX, backup_path)
    return backup_path


def save_generated_source(conclusion_id: str, latex_content: str) -> Path:
    GENERATED_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_SOURCE_DIR / f"{conclusion_id}.tex"
    path.write_text(latex_content, encoding="utf-8")
    return path


def run_pipeline(
    python_exe: str,
    module_dir: str,
    target_id: str,
    skip_git_commit: bool = False,
    timeout_seconds: int | None = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[str | None, str | None]:
    script = PIPELINE_DIR / "run_source_to_pdf.py"
    cmd = [python_exe, str(script), module_dir, "--target-id", target_id]
    if skip_git_commit:
        cmd.append("--skip-git-commit")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
        )
        output = result.stdout + result.stderr

        if result.returncode != 0:
            return None, f"Pipeline failed (rc={result.returncode}): {output[-3000:]}"

        match = NEW_ID_PATTERN.search(output)
        if not match:
            return None, f"Cannot parse NEW_ID from output: {output[-3000:]}"

        pdf_ready_match = PDF_READY_PATTERN.search(output)
        if not pdf_ready_match:
            return None, (
                "PDF_COMPILE_FAILED: Pipeline did not report PDF_READY; "
                f"deployment blocked. Output tail: {output[-3000:]}"
            )

        pdf_path = Path(pdf_ready_match.group(1).strip())
        if not pdf_path.is_file():
            return None, (
                "PDF_COMPILE_FAILED: Pipeline reported PDF_READY but the file "
                f"does not exist; deployment blocked: {pdf_path}"
            )

        return match.group(1).upper(), None
    except subprocess.TimeoutExpired:
        return None, timeout_error("Pipeline", timeout_seconds)
    except Exception as exc:
        return None, f"Pipeline error: {exc}"


def run_incremental_publish(
    python_exe: str,
    new_id: str,
    no_deploy: bool = False,
    timeout_seconds: int | None = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[bool, str | None]:
    script = PROJECT_ROOT / "scripts" / "incremental_publish.py"
    cmd = [python_exe, str(script), new_id]
    if no_deploy:
        cmd.append("--no-deploy")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            return False, f"incremental_publish.py failed (rc={result.returncode}): {output[-1000:]}"
        return True, None
    except subprocess.TimeoutExpired:
        return False, timeout_error("incremental_publish.py", timeout_seconds)
    except Exception as exc:
        return False, f"incremental_publish.py error: {exc}"


def load_state_index() -> dict[str, dict[str, Any]]:
    """Return the latest state record for each readme conclusion ID."""
    if not STATE_PATH.exists():
        return {}

    state_index: dict[str, dict[str, Any]] = {}
    for line in read_text_file(STATE_PATH).splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        item_id = str(record.get("id", "")).strip().upper()
        if item_id:
            state_index[item_id] = record
    return state_index


def generated_source_path(conclusion_id: str) -> Path:
    return GENERATED_SOURCE_DIR / f"{conclusion_id.upper()}.tex"


def read_cached_generated_source(conclusion_id: str) -> tuple[Path | None, str | None, list[str]]:
    path = generated_source_path(conclusion_id)
    if not path.is_file():
        return None, None, []

    content = read_text_file(path).strip()
    problems = validate_latex_content(content)
    return path, content, problems


def pipeline_output_status(item_id: str) -> tuple[bool, str]:
    item_id = item_id.upper()
    output_dir = PIPELINE_DIR / "output" / item_id
    if not output_dir.is_dir():
        return False, f"missing output directory {output_dir.relative_to(PROJECT_ROOT)}"

    missing: list[str] = []
    for filename in LECTURE_FILES:
        if not (output_dir / filename).is_file():
            missing.append(filename)

    if not (output_dir / "l5_meta.json").is_file():
        missing.append("l5_meta.json")

    cache_state_path = output_dir / "_pipeline_cache_state.json"
    if not cache_state_path.is_file():
        missing.append("_pipeline_cache_state.json")
    else:
        try:
            cache_state = load_json(cache_state_path)
            cached_hash = cache_state.get("source_hash")
            source_path = PIPELINE_DIR / "input" / item_id / "source.tex"
            if not source_path.is_file():
                missing.append(f"{source_path.relative_to(PROJECT_ROOT)}")
            elif cached_hash != compute_source_hash(read_text_file(source_path)):
                missing.append("matching source_hash")
        except Exception as exc:
            missing.append(f"readable cache state ({exc})")

    l6_pattern = re.compile(
        L6_DIRNAME_PATTERN_TEMPLATE.format(item_id=re.escape(item_id)),
        re.IGNORECASE,
    )
    has_l6_dirname = any(
        child.is_file() and l6_pattern.match(child.name)
        for child in output_dir.iterdir()
    )
    if not has_l6_dirname:
        missing.append("L6 dirname marker")

    if missing:
        return False, "missing " + ", ".join(missing)
    return True, f"output ready at {output_dir.relative_to(PROJECT_ROOT)}"


def wait_for_pipeline_output_ready(item_id: str) -> tuple[bool, str]:
    deadline = time.monotonic() + POST_TIMEOUT_RECOVERY_WAIT_SECONDS
    last_reason = ""

    while True:
        ready, reason = pipeline_output_status(item_id)
        if ready:
            return True, reason
        last_reason = reason

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False, last_reason

        time.sleep(min(POST_TIMEOUT_RECOVERY_POLL_SECONDS, remaining))


def recover_pipeline_timeout(
    python_exe: str,
    module_dir: str,
    target_id: str,
    skip_git_commit: bool,
    timeout_seconds: int | None,
) -> tuple[str | None, str | None]:
    log(
        f"[recover] {target_id}: pipeline timed out; waiting up to "
        f"{POST_TIMEOUT_RECOVERY_WAIT_SECONDS}s for completed output..."
    )
    ready, reason = wait_for_pipeline_output_ready(target_id)
    if not ready:
        return None, f"Pipeline timeout recovery failed: {reason}"

    log(
        f"[recover] {target_id}: {reason}; rerunning run_source_to_pdf.py "
        "to finish publish/PDF steps from cache"
    )
    return run_pipeline(
        python_exe,
        module_dir,
        target_id,
        skip_git_commit=skip_git_commit,
        timeout_seconds=timeout_seconds,
    )


def find_existing_conclusion_dir(module_dir: str, item_id: str) -> Path | None:
    module_path = PROJECT_ROOT / module_dir
    if not module_path.is_dir():
        return None

    prefix = item_id.upper()
    matches: list[Path] = []
    for child in module_path.iterdir():
        if not child.is_dir():
            continue
        upper_name = child.name.upper()
        if upper_name == prefix or upper_name.startswith(f"{prefix}_"):
            matches.append(child)

    if len(matches) == 1:
        return matches[0]
    return None


def publish_resume_id(
    conclusion: dict[str, Any],
    latest_state: dict[str, Any] | None,
) -> str | None:
    if not latest_state:
        return None
    if latest_state.get("status") != "failed" or latest_state.get("stage") != "publish":
        return None

    new_id = str(latest_state.get("new_id") or conclusion["id"]).strip().upper()
    if not re.fullmatch(r"[A-Z]\d{3}", new_id):
        return None
    if not find_existing_conclusion_dir(str(conclusion["module_dir"]), new_id):
        return None
    return new_id


def process_one_conclusion(
    conclusion: dict[str, Any],
    api_config: dict[str, Any],
    model_config: dict[str, Any],
    python_exe: str,
    dry_run: bool,
    skip_git_commit: bool = False,
    no_deploy: bool = False,
    allow_id_mismatch: bool = False,
    force_regenerate: bool = False,
    timeout_seconds: int | None = DEFAULT_TIMEOUT_SECONDS,
) -> bool:
    cid = str(conclusion["id"])
    module_dir = str(conclusion["module_dir"])
    source_line = str(conclusion.get("llm_source_line") or conclusion["source_line"])

    log(f"[start] {cid}: {module_dir}:{conclusion['line_number']} {collapse_for_log(source_line)}")
    record_state(conclusion, "start")

    resume_publish_id = str(conclusion.get("_resume_publish_id") or "").strip().upper()

    if dry_run:
        cached_path, _, cached_problems = read_cached_generated_source(cid)
        if resume_publish_id and not force_regenerate:
            log(f"[dry-run] {cid}: would resume by publishing {resume_publish_id} only")
        elif cached_path and not cached_problems and not force_regenerate:
            log(
                f"[dry-run] {cid}: would reuse {cached_path.relative_to(PROJECT_ROOT)}, "
                f"write source.tex, run pipeline with --target-id {cid}, publish"
            )
        elif force_regenerate:
            log(
                f"[dry-run] {cid}: would force-regenerate LaTeX, write source.tex, "
                f"run pipeline with --target-id {cid}, publish"
            )
        else:
            log(
                f"[dry-run] {cid}: would generate LaTeX, write source.tex, "
                f"run pipeline with --target-id {cid}, publish"
            )
        record_state(conclusion, "dry_run")
        return True

    if resume_publish_id and not force_regenerate:
        log(f"[resume] Previous run reached publish; re-running incremental_publish.py for {resume_publish_id}")
        published, publish_error = run_incremental_publish(
            python_exe,
            resume_publish_id,
            no_deploy=no_deploy,
            timeout_seconds=timeout_seconds,
        )
        if not published:
            error = publish_error or "incremental_publish.py failed"
            log(f"[fail] {cid} -> {resume_publish_id}: {error}")
            remember_failure(conclusion, "publish", error)
            record_state(conclusion, "failed", stage="publish", new_id=resume_publish_id, error=error)
            return False

        log(f"[done] {cid} -> {resume_publish_id}: publish resumed and complete")
        record_state(conclusion, "done", new_id=resume_publish_id, resumed_publish=True)
        return True

    generated_path: Path | None = None
    latex_content: str | None = None

    if not force_regenerate:
        cached_path, cached_content, cached_problems = read_cached_generated_source(cid)
        if cached_path and cached_content and not cached_problems:
            generated_path = cached_path
            latex_content = cached_content
            log(f"[latex] Reusing cached LaTeX: {cached_path.relative_to(PROJECT_ROOT)}")
        elif cached_path and cached_problems:
            log(
                f"[latex] Cached LaTeX invalid for {cid}, regenerating: "
                + "; ".join(cached_problems)
            )

    if latex_content is None:
        log(f"[latex] Generating LaTeX for {cid}...")
        latex_content, generation_error = generate_latex_via_llm(
            conclusion,
            api_config,
            model_config,
        )
        if not latex_content:
            error = generation_error or "LaTeX generation returned empty"
            log(f"[fail] {cid}: {error}")
            remember_failure(conclusion, "latex", error)
            record_state(conclusion, "failed", stage="latex", error=error)
            return False
        generated_path = save_generated_source(cid, latex_content)

    if generated_path is None:
        error = "Internal error: generated source path is missing"
        log(f"[fail] {cid}: {error}")
        remember_failure(conclusion, "latex", error)
        record_state(conclusion, "failed", stage="latex", error=error)
        return False

    SOURCE_TEX.write_text(latex_content, encoding="utf-8")
    log(
        f"[write] source.tex updated from {generated_path.relative_to(PROJECT_ROOT)} "
        f"({len(latex_content)} chars)"
    )

    log(f"[pipeline] Running run_source_to_pdf.py {module_dir} --target-id {cid}...")
    new_id, pipeline_error = run_pipeline(
        python_exe,
        module_dir,
        cid,
        skip_git_commit=skip_git_commit,
        timeout_seconds=timeout_seconds,
    )
    if pipeline_error:
        if pipeline_error.startswith("Pipeline timed out"):
            recovered_id, recovery_error = recover_pipeline_timeout(
                python_exe,
                module_dir,
                cid,
                skip_git_commit=skip_git_commit,
                timeout_seconds=timeout_seconds,
            )
            if not recovery_error and recovered_id:
                new_id = recovered_id
                pipeline_error = None
                log(f"[recover] {cid}: pipeline timeout recovered as {new_id}")
            else:
                pipeline_error = recovery_error or pipeline_error

    if pipeline_error:
        log(f"[fail] {cid}: {pipeline_error}")
        failure_stage = "pdf" if is_pdf_compile_failure(pipeline_error) else "pipeline"
        remember_failure(conclusion, failure_stage, pipeline_error)
        extra: dict[str, Any] = {"stage": failure_stage, "error": pipeline_error}
        pdf_log = extract_pdf_failure_log(pipeline_error)
        if pdf_log:
            extra["pdf_error_log"] = pdf_log
            log(f"[pdf] {cid}: compile failure log saved at {pdf_log}")
        record_state(conclusion, "failed", **extra)
        return False

    if not new_id:
        error = "Pipeline returned no NEW_ID"
        log(f"[fail] {cid}: {error}")
        remember_failure(conclusion, "pipeline", error)
        record_state(conclusion, "failed", stage="pipeline", error=error)
        return False

    if new_id != cid and not allow_id_mismatch:
        error = f"Expected ID {cid}, but pipeline produced {new_id}"
        log(f"[fail] {cid}: {error}")
        remember_failure(conclusion, "id_check", error)
        record_state(conclusion, "failed", stage="id_check", new_id=new_id, error=error)
        return False

    if new_id != cid:
        log(f"[warn] {cid}: expected ID {cid}, but pipeline produced {new_id}; continuing")

    log(f"[publish] PDF_READY confirmed for {new_id}; deployment is allowed")
    log(f"[publish] Running incremental_publish.py for {new_id}...")
    published, publish_error = run_incremental_publish(
        python_exe,
        new_id,
        no_deploy=no_deploy,
        timeout_seconds=timeout_seconds,
    )
    if not published:
        error = publish_error or "incremental_publish.py failed"
        log(f"[fail] {cid} -> {new_id}: {error}")
        remember_failure(conclusion, "publish", error)
        record_state(conclusion, "failed", stage="publish", new_id=new_id, error=error)
        return False

    log(f"[done] {cid} -> {new_id}: complete")
    record_state(conclusion, "done", new_id=new_id, generated_source=str(generated_path))
    return True


def get_existing_ids(module_dirs: Iterable[str]) -> set[str]:
    existing: set[str] = set()
    for module_dir in module_dirs:
        module_path = PROJECT_ROOT / module_dir
        if not module_path.is_dir():
            continue
        for item in module_path.iterdir():
            if not item.is_dir():
                continue
            match = re.match(r"^([A-Z]\d{3})(?:_|$)", item.name.upper())
            if match:
                existing.add(match.group(1))
    return existing


def resolve_module_selector(
    selector: str,
    module_dirs: list[str],
    prefix_map: dict[str, str],
) -> str:
    token = selector.strip()
    if not token:
        raise ValueError("Module selector cannot be empty.")

    exact_hits = [m for m in module_dirs if m.lower() == token.lower()]
    if len(exact_hits) == 1:
        return exact_hits[0]

    if re.fullmatch(r"\d{2}", token):
        index_hits = [m for m in module_dirs if re.match(rf"^{re.escape(token)}[_-]", m)]
        if len(index_hits) == 1:
            return index_hits[0]

    if re.fullmatch(r"[A-Za-z]", token):
        letter = token.upper()
        prefix_hits = [m for m in module_dirs if prefix_map.get(m, "").upper() == letter]
        if len(prefix_hits) == 1:
            return prefix_hits[0]

    normalized = re.sub(r"[-_\s]+", "-", token.lower())
    suffix_hits: list[str] = []
    for module_dir in module_dirs:
        match = re.match(r"^\d{2}[_-](.+)$", module_dir)
        suffix = match.group(1) if match else module_dir
        if re.sub(r"[-_\s]+", "-", suffix.lower()) == normalized:
            suffix_hits.append(module_dir)
    if len(suffix_hits) == 1:
        return suffix_hits[0]

    available = ", ".join(module_dirs)
    raise ValueError(f"Unknown module selector {selector!r}. Available: {available}")


def apply_start_from(
    conclusions: list[dict[str, Any]],
    start_from: str | None,
) -> list[dict[str, Any]]:
    if not start_from:
        return conclusions

    start_id = start_from.upper()
    filtered: list[dict[str, Any]] = []
    found = False
    for conclusion in conclusions:
        if conclusion["id"] == start_id:
            found = True
        if found:
            filtered.append(conclusion)

    if not found:
        log(f"[warn] --start-from {start_id} not found, processing all selected rows")
        return conclusions

    log(f"[info] Resuming from {start_id}, {len(filtered)} selected rows remain")
    return filtered


def normalize_id_filter(raw_values: list[str] | None) -> list[str]:
    if not raw_values:
        return []

    ids: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value).split(","):
            item_id = part.strip().upper()
            if not item_id:
                continue
            if not re.fullmatch(r"[A-Z]\d{3}", item_id):
                raise ValueError(f"Invalid ID in --ids: {part!r}")
            if item_id in seen:
                continue
            seen.add(item_id)
            ids.append(item_id)
    return ids


def apply_id_filter(
    conclusions: list[dict[str, Any]],
    selected_ids: list[str],
) -> list[dict[str, Any]]:
    if not selected_ids:
        return conclusions

    selected = set(selected_ids)
    filtered = [
        conclusion
        for conclusion in conclusions
        if str(conclusion.get("id", "")).upper() in selected
    ]
    found = {str(conclusion.get("id", "")).upper() for conclusion in filtered}
    missing = [item_id for item_id in selected_ids if item_id not in found]
    if missing:
        log(f"[warn] --ids not found in selected module/readme rows: {', '.join(missing)}")
    log(f"[info] Filtered by --ids: {len(filtered)} selected row(s)")
    return filtered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch generate pending conclusions from readme.md files"
    )
    parser.add_argument(
        "--module",
        "-m",
        default=None,
        help="Process one module, e.g. 07_inequality / 07 / inequality / I",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only parse and list planned rows; do not call API or write files.",
    )
    parser.add_argument(
        "--start-from",
        default=None,
        help="Resume from a specific readme conclusion ID, e.g. I043.",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help=(
            "Only process specific readme IDs. Supports spaces or commas, "
            "e.g. --ids S021 S024 or --ids S021,S024."
        ),
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable path.",
    )
    parser.add_argument(
        "--skip-existing",
        dest="skip_existing",
        action="store_true",
        default=True,
        help="Skip conclusions that already have directories (default).",
    )
    parser.add_argument(
        "--no-skip-existing",
        dest="skip_existing",
        action="store_false",
        help="Do not skip existing conclusion directories.",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Process all pending rows, even if directories already exist.",
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help=(
            "Ignore cached generated_sources and failed-publish resume records; "
            "regenerate LaTeX and rerun the pipeline. Implies --force-all."
        ),
    )
    parser.add_argument(
        "--skip-git-commit",
        action="store_true",
        help="Pass --skip-git-commit to run_source_to_pdf.py.",
    )
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Pass --no-deploy to incremental_publish.py.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with the next row after a failure.",
    )
    parser.add_argument(
        "--allow-id-mismatch",
        action="store_true",
        help="Continue publishing if pipeline NEW_ID differs from the readme row ID.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "Timeout seconds for run_source_to_pdf.py and incremental_publish.py "
            f"(default: {DEFAULT_TIMEOUT_SECONDS}; 0 disables timeout)."
        ),
    )
    parser.add_argument(
        "--pipeline-timeout",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--publish-timeout",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    global DRY_RUN_MODE
    args = parse_args()
    DRY_RUN_MODE = bool(args.dry_run)
    if args.force_regenerate:
        args.force_all = True

    try:
        selected_ids = normalize_id_filter(args.ids)
    except ValueError as exc:
        log(f"[error] {exc}")
        return 1

    timeout_value = args.timeout
    legacy_timeout_values = [
        value
        for value in (args.pipeline_timeout, args.publish_timeout)
        if value is not None
    ]
    if legacy_timeout_values:
        timeout_value = max(legacy_timeout_values)
        log("[warn] --pipeline-timeout/--publish-timeout are deprecated; use --timeout instead")

    try:
        timeout_seconds = normalize_timeout(timeout_value)
    except ValueError as exc:
        log(f"[error] {exc}")
        return 1
    log(f"[info] Command timeout: {describe_timeout(timeout_seconds)}")

    try:
        prefix_map = load_module_prefix_map()
    except Exception as exc:
        log(f"[error] Cannot load module prefix map: {exc}")
        return 1

    module_dirs = [module for module in prefix_map if (PROJECT_ROOT / module).is_dir()]
    if not module_dirs:
        log("[error] No configured module directories found.")
        return 1

    if args.module:
        try:
            modules = [resolve_module_selector(args.module, module_dirs, prefix_map)]
        except ValueError as exc:
            log(f"[error] {exc}")
            return 1
    else:
        modules = module_dirs

    all_conclusions: list[dict[str, Any]] = []
    for module_dir in modules:
        all_conclusions.extend(parse_readme(module_dir))

    total_before_filters = len(all_conclusions)
    skipped_existing = 0
    resume_publish = 0

    if not all_conclusions:
        log_config_snapshot(
            "start",
            args,
            timeout_seconds=timeout_seconds,
            modules=modules,
            selected_ids=selected_ids,
            total_before_filters=total_before_filters,
            selected_total=0,
            skipped_existing=skipped_existing,
            resume_publish=resume_publish,
        )
        log("[info] No pending rows found.")
        log_config_snapshot(
            "end",
            args,
            timeout_seconds=timeout_seconds,
            modules=modules,
            selected_ids=selected_ids,
            total_before_filters=total_before_filters,
            selected_total=0,
            skipped_existing=skipped_existing,
            resume_publish=resume_publish,
            result={"success": 0, "failed": 0, "selected": 0, "exit_code": 0},
        )
        return 0

    log(f"[info] Total pending rows before filters: {total_before_filters}")
    all_conclusions = apply_id_filter(all_conclusions, selected_ids)
    all_conclusions = apply_start_from(all_conclusions, args.start_from)

    state_index = load_state_index()

    if args.skip_existing and not args.force_all:
        existing_ids = get_existing_ids(module_dirs)
        filtered: list[dict[str, Any]] = []
        for conclusion in all_conclusions:
            item_id = str(conclusion["id"]).upper()
            resume_id = publish_resume_id(conclusion, state_index.get(item_id))
            if resume_id:
                conclusion["_resume_publish_id"] = resume_id
                filtered.append(conclusion)
                resume_publish += 1
            elif item_id in existing_ids:
                skipped_existing += 1
            else:
                filtered.append(conclusion)
        if skipped_existing:
            log(f"[info] Skipping {skipped_existing} rows with existing conclusion directories")
        if resume_publish:
            log(f"[info] Resuming publish for {resume_publish} previously failed rows")
        all_conclusions = filtered

    if not all_conclusions:
        log_config_snapshot(
            "start",
            args,
            timeout_seconds=timeout_seconds,
            modules=modules,
            selected_ids=selected_ids,
            total_before_filters=total_before_filters,
            selected_total=0,
            skipped_existing=skipped_existing,
            resume_publish=resume_publish,
        )
        log("[info] Nothing to do after filters.")
        log_config_snapshot(
            "end",
            args,
            timeout_seconds=timeout_seconds,
            modules=modules,
            selected_ids=selected_ids,
            total_before_filters=total_before_filters,
            selected_total=0,
            skipped_existing=skipped_existing,
            resume_publish=resume_publish,
            result={"success": 0, "failed": 0, "selected": 0, "exit_code": 0},
        )
        return 0

    log(f"[info] Will process {len(all_conclusions)} rows")
    if args.force_regenerate:
        log(
            "[warn] --force-regenerate ignores cached LaTeX and existing-directory skips. "
            "The readme ID is still passed as --target-id, so existing published "
            "directories may cause later pipeline/publish steps to fail."
        )

    api_config: dict[str, Any] = {}
    model_config: dict[str, Any] = {}
    backup_path: Path | None = None
    if not args.dry_run:
        try:
            app_config = load_api_config()
            api_config = app_config["api"]
            model_config = app_config["model"]
        except Exception as exc:
            log(f"[error] Cannot load API config: {exc}")
            return 1

        backup_path = backup_source_tex()
        if backup_path:
            log(f"[backup] source.tex backed up to {backup_path.relative_to(PROJECT_ROOT)}")

    success = 0
    fail = 0
    total = len(all_conclusions)
    failed_items: list[dict[str, str]] = []

    log_config_snapshot(
        "start",
        args,
        timeout_seconds=timeout_seconds,
        modules=modules,
        selected_ids=selected_ids,
        total_before_filters=total_before_filters,
        selected_total=total,
        skipped_existing=skipped_existing,
        resume_publish=resume_publish,
        api_config=api_config,
        model_config=model_config,
        backup_path=backup_path,
    )

    for index, conclusion in enumerate(all_conclusions, start=1):
        log("")
        log("=" * 60)
        log(
            f"[progress] {index}/{total}: {conclusion['id']} "
            f"{collapse_for_log(str(conclusion.get('llm_source_line') or conclusion['source_line']), 70)}"
        )
        log("=" * 60)

        ok = process_one_conclusion(
            conclusion,
            api_config,
            model_config,
            args.python_exe,
            args.dry_run,
            skip_git_commit=args.skip_git_commit,
            no_deploy=args.no_deploy,
            allow_id_mismatch=args.allow_id_mismatch,
            force_regenerate=args.force_regenerate,
            timeout_seconds=timeout_seconds,
        )

        if ok:
            success += 1
        else:
            fail += 1
            failed_item = {
                "id": str(conclusion.get("id") or "").upper(),
                "stage": str(conclusion.get("_last_failure_stage") or "unknown"),
                "error": collapse_for_log(str(conclusion.get("_last_error") or ""), 180),
            }
            failed_items.append(failed_item)
            if conclusion.get("_last_failure_stage") == "pdf":
                log(
                    f"[skip] {conclusion['id']}: PDF compile failed; "
                    "recorded and continuing with next row."
                )
                continue
            if not args.continue_on_error:
                log("[abort] Stopping at first failure. Use --continue-on-error to keep going.")
                break

        if not args.dry_run and index < total:
            time.sleep(3)

    log("")
    log("=" * 60)
    log(f"[summary] Done. Success: {success}, Failed: {fail}, Selected: {total}")
    if failed_items:
        failed_ids = [item["id"] for item in failed_items if item["id"]]
        log(f"[summary] Failed IDs: {' '.join(failed_ids)}")
        for item in failed_items:
            detail = f"[summary]   - {item['id']}: stage={item['stage']}"
            if item["error"]:
                detail += f", error={item['error']}"
            log(detail)
        module_arg = f" --module {args.module}" if args.module else ""
        log(
            "[summary] Retry command:"
            f" python -B 12_pipeline\\batch_generate_conclusions.py{module_arg} "
            f"--ids {' '.join(failed_ids)} --force-regenerate --timeout {args.timeout} "
            "--continue-on-error --no-deploy --skip-git-commit"
        )
    exit_code = 0 if fail == 0 else 1
    log_config_snapshot(
        "end",
        args,
        timeout_seconds=timeout_seconds,
        modules=modules,
        selected_ids=selected_ids,
        total_before_filters=total_before_filters,
        selected_total=total,
        skipped_existing=skipped_existing,
        resume_publish=resume_publish,
        api_config=api_config,
        model_config=model_config,
        backup_path=backup_path,
        result={"success": success, "failed": fail, "selected": total, "exit_code": exit_code},
    )
    log("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
