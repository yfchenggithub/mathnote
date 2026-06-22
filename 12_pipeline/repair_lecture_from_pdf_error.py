#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Repair or regenerate L4 lecture snippets after PDF compilation fails.

This script is intentionally narrow: it only updates output/<ID>/L4 checked
lecture JSON and the exported 01_statement.tex ... 06_summary.tex snippets.
Publishing back to the module directory is still handled by
publish_pipeline_output.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_pipeline as pipeline  # noqa: E402


MAX_ERROR_LOG_CHARS = 14000
MAX_SOURCE_CHARS = 12000
MAX_TEX_FILE_CHARS = 10000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use the pro L4 checker to repair lecture snippets from a PDF error log."
    )
    parser.add_argument("item_id", help="Conclusion ID, e.g. S017")
    parser.add_argument(
        "--mode",
        choices=("repair", "regenerate"),
        required=True,
        help="repair = minimal fix; regenerate = rewrite all six snippets after repair failed.",
    )
    parser.add_argument(
        "--error-log",
        required=True,
        type=Path,
        help="Text log captured from the failed PDF build attempt.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=SCRIPT_DIR / "output",
        help="Pipeline output root. Default: 12_pipeline/output.",
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=SCRIPT_DIR / "input",
        help="Pipeline input root. Default: 12_pipeline/input.",
    )
    return parser.parse_args()


def clip_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def read_text_if_exists(path: Path, *, max_chars: int | None = None) -> str:
    if not path.is_file():
        return ""
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            text = path.read_text(encoding=encoding, errors="replace")
            return clip_text(text, max_chars) if max_chars else text
        except Exception as exc:
            last_error = exc
    raise last_error if last_error else FileNotFoundError(path)


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return pipeline.load_json_file(str(path))


def load_current_tex_files(item_output_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for key, filename in pipeline.LECTURE_TEX_FILE_MAP.items():
        files[key] = read_text_if_exists(
            item_output_dir / filename,
            max_chars=MAX_TEX_FILE_CHARS,
        )
    return files


def build_prompt(
    *,
    item_id: str,
    mode: str,
    payload: dict[str, Any],
) -> str:
    mode_rule = (
        "最小修复模式：只修复导致 PDF 编译失败的 LaTeX/结构问题，尽量保留原内容。"
        if mode == "repair"
        else "重新生成模式：上一轮最小修复后仍然失败，请基于 L2/L3/source 和错误日志完整重写六个片段。"
    )
    payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"""
你是高中数学二级结论讲义的 PDF 编译错误修复器。

当前结论 ID：{item_id}
当前模式：{mode}
模式要求：{mode_rule}

你的目标：
1. 修复 01_statement.tex 到 06_summary.tex，使其可以被现有 main.tex 正常编译成 PDF。
2. 数学内容必须忠于 L2 结论和 source.tex，不得为了修复而改变命题。
3. 如果错误日志指出具体文件、行号、命令、环境不匹配，优先修复这些位置。
4. 不要输出 documentclass、preamble、main.tex、\\input 命令。
5. 每个字段必须保留对应 box 环境：
   - 01_statement 使用 statementbox
   - 02_explanation 使用 explanationbox
   - 03_proof 使用 proofbox
   - 04_examples 使用 examplebox
   - 05_traps 使用 trapbox
   - 06_summary 使用 summarybox
6. 数学命令必须放在数学模式中；数学环境内部不要出现中文标点或中文解释文字。
7. 不要使用未定义环境；不要使用 emoji、带圈数字、装饰符号。
8. 输出必须是严格 JSON 对象，不要 Markdown 代码块，不要解释文字。

输出 JSON 的键必须且只能包含：
{{
  "status": "success",
  "01_statement": "...",
  "02_explanation": "...",
  "03_proof": "...",
  "04_examples": "...",
  "05_traps": "...",
  "06_summary": "..."
}}

输入数据如下：
{payload_text}
""".strip()


def repair_lecture(
    *,
    item_id: str,
    mode: str,
    item_output_dir: Path,
    input_root: Path,
    error_log_path: Path,
) -> dict[str, Any]:
    l2 = load_json_or_empty(item_output_dir / "l2_statement.json")
    if not l2:
        raise FileNotFoundError(f"Missing L2 output: {item_output_dir / 'l2_statement.json'}")

    l3 = load_json_or_empty(item_output_dir / "l3_eval.json")
    if not l3 and hasattr(pipeline, "build_disabled_l3_result"):
        l3 = pipeline.build_disabled_l3_result()

    current_l4 = load_json_or_empty(item_output_dir / "l4_lecture_checked.json")
    if not current_l4:
        current_l4 = load_json_or_empty(item_output_dir / "l4_lecture.json")
    if not current_l4:
        raise FileNotFoundError(
            f"Missing L4 output: {item_output_dir / 'l4_lecture_checked.json'}"
        )

    source_text = read_text_if_exists(
        input_root / item_id / "source.tex",
        max_chars=MAX_SOURCE_CHARS,
    )
    error_log = read_text_if_exists(error_log_path, max_chars=MAX_ERROR_LOG_CHARS)
    if not error_log.strip():
        raise ValueError(f"Error log is empty or missing: {error_log_path}")

    payload = {
        "item_id": item_id,
        "mode": mode,
        "source_tex": source_text,
        "l2_statement": l2,
        "l3_eval": l3,
        "current_l4_json": current_l4,
        "current_tex_files": load_current_tex_files(item_output_dir),
        "pdf_compile_error_log": error_log,
    }
    prompt = build_prompt(item_id=item_id, mode=mode, payload=payload)

    metrics: dict[str, Any] = {}
    token = pipeline.CURRENT_ITEM_ID.set(item_id)
    try:
        raw = pipeline.call_llm(
            prompt,
            step="l4_check",
            payload_chars=len(json.dumps(payload, ensure_ascii=False)),
            metrics=metrics,
        )
    finally:
        pipeline.CURRENT_ITEM_ID.reset(token)

    parsed = pipeline.safe_json_parse(raw, parse_metrics=metrics)
    validated = pipeline.validate_l4_lecture_result(parsed, f"pdf_{mode}")
    if not pipeline.is_step_success(validated):
        debug_path = item_output_dir / f"l4_pdf_{mode}_parse_error.json"
        pipeline.save_json(validated, str(debug_path))
        raise ValueError(
            f"PDF {mode} L4 result invalid: {pipeline.get_step_error(validated)}. "
            f"Debug saved to {debug_path}"
        )
    return validated


def main() -> int:
    args = parse_args()
    item_id = args.item_id.strip().upper()
    item_output_dir = args.output_root / item_id
    if not item_output_dir.is_dir():
        raise FileNotFoundError(f"Output directory not found: {item_output_dir}")

    repaired = repair_lecture(
        item_id=item_id,
        mode=args.mode,
        item_output_dir=item_output_dir,
        input_root=args.input_root,
        error_log_path=args.error_log,
    )

    checked_path = item_output_dir / "l4_lecture_checked.json"
    debug_path = item_output_dir / f"l4_pdf_{args.mode}.json"
    pipeline.save_json(repaired, str(checked_path))
    pipeline.save_json(repaired, str(debug_path))
    pipeline.export_lecture_tex_snippets(repaired, item_id, str(args.output_root))

    print(f"[ok] PDF {args.mode} updated {checked_path}")
    print(f"REPAIRED_ID={item_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
