#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run the end-to-end pipeline from 12_pipeline/source.tex to final PDF.

Usage:
    python 12_pipeline/run_source_to_pdf.py
    python 12_pipeline/run_source_to_pdf.py 03
    python 12_pipeline/run_source_to_pdf.py conic
    python 12_pipeline/run_source_to_pdf.py 03_conic --dry-run
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from config.config_loader import get_api_config, get_model_config, get_performance
from utils.prompt_loader import load_prompt

NEW_ID_PATTERN = re.compile(r"^NEW_ID=([A-Za-z]\d{3})\s*$", re.MULTILINE)
ALLOWED_MODULES: tuple[str, ...] = (
    "set",
    "function",
    "sequence",
    "conic",
    "vector",
    "geometry-solid",
    "probability-stat",
    "inequality",
    "trigonometry",
    "geometry-plane",
)
ALLOWED_MODULE_SET = set(ALLOWED_MODULES)
MODULE_ORDER = {name: idx for idx, name in enumerate(ALLOWED_MODULES)}
MODULE_ALIASES = {
    "集合": "set",
    "函数": "function",
    "数列": "sequence",
    "圆锥曲线": "conic",
    "解析几何": "conic",
    "向量": "vector",
    "立体几何": "geometry-solid",
    "概率统计": "probability-stat",
    "概率与统计": "probability-stat",
    "不等式": "inequality",
    "三角函数": "trigonometry",
    "平面几何": "geometry-plane",
    "trig": "trigonometry",
    "conics": "conic",
    "sequence-series": "sequence",
    "series": "sequence",
    "stat": "probability-stat",
    "probability": "probability-stat",
    "probability-statistics": "probability-stat",
    "prob-stat": "probability-stat",
    "solid": "geometry-solid",
    "solid-geometry": "geometry-solid",
    "stereometry": "geometry-solid",
    "plane": "geometry-plane",
    "plane-geometry": "geometry-plane",
    "analytic-geometry": "conic",
}
MODULE_KEYWORDS: dict[str, list[tuple[str, int]]] = {
    "set": [
        ("集合", 6),
        ("并集", 5),
        ("交集", 5),
        ("补集", 5),
        ("空集", 5),
        ("全集", 4),
        ("\\in", 4),
        ("\\notin", 4),
        ("\\subset", 4),
        ("\\cup", 4),
        ("\\cap", 4),
    ],
    "function": [
        ("函数", 4),
        ("f(x)", 4),
        ("定义域", 5),
        ("值域", 5),
        ("单调", 4),
        ("奇偶", 4),
        ("周期", 3),
        ("最值", 3),
        ("图像", 3),
    ],
    "sequence": [
        ("数列", 6),
        ("a_n", 5),
        ("a_{n", 5),
        ("s_n", 5),
        ("s_{n", 5),
        ("通项", 5),
        ("递推", 5),
        ("前n项和", 5),
        ("等差", 5),
        ("等比", 5),
    ],
    "conic": [
        ("解析几何", 6),
        ("圆锥曲线", 6),
        ("椭圆", 6),
        ("双曲线", 6),
        ("抛物线", 6),
        ("焦点", 5),
        ("离心率", 5),
        ("准线", 5),
        ("切线", 4),
        ("轨迹", 4),
    ],
    "vector": [
        ("向量", 6),
        ("\\vec", 6),
        ("\\overrightarrow", 6),
        ("数量积", 6),
        ("点积", 6),
        ("模长", 4),
        ("夹角", 4),
    ],
    "geometry-solid": [
        ("立体几何", 7),
        ("空间", 4),
        ("二面角", 6),
        ("棱柱", 5),
        ("棱锥", 5),
        ("球", 4),
        ("体积", 5),
        ("表面积", 5),
    ],
    "probability-stat": [
        ("概率", 7),
        ("随机变量", 7),
        ("分布", 6),
        ("期望", 6),
        ("方差", 6),
        ("统计", 6),
        ("抽样", 5),
        ("条件概率", 6),
        ("独立", 4),
    ],
    "inequality": [
        ("不等式", 7),
        ("均值不等式", 7),
        ("柯西", 6),
        ("放缩", 5),
        ("取等", 4),
        ("绝对值", 4),
        ("\\le", 3),
        ("\\ge", 3),
    ],
    "trigonometry": [
        ("三角", 6),
        ("\\sin", 8),
        ("\\cos", 8),
        ("\\tan", 8),
        ("\\cot", 7),
        ("\\sec", 7),
        ("\\csc", 7),
        ("同角", 5),
        ("诱导公式", 6),
        ("和差化积", 6),
        ("积化和差", 6),
        ("降幂", 6),
    ],
    "geometry-plane": [
        ("平面几何", 7),
        ("三角形", 5),
        ("四边形", 5),
        ("圆", 4),
        ("内接", 5),
        ("外接", 5),
        ("全等", 5),
        ("相似", 5),
        ("角平分线", 5),
    ],
}
MODULE_REPAIR_PROMPT = """你是模块纠偏器。

你必须从下面 10 个模块中选择 1 个最接近且最合适的模块：
set / function / sequence / conic / vector / geometry-solid / probability-stat / inequality / trigonometry / geometry-plane

要求：
1. 只能输出一个模块。
2. 不得输出枚举之外的值。
3. 若信息不足，也必须选最接近的一项。
4. 只输出严格 JSON，不要解释。

输出格式：
{{"module":"trigonometry"}}

输入 source.tex：
{source_text}

上一次模型原始输出：
{raw_output}
"""

api_config = get_api_config()
model_config = get_model_config()
perf_config = get_performance()
ROUTER_MODEL = model_config.get("default")
ROUTER_TEMPERATURE = float(perf_config.get("temperature", 0.2))
ROUTER_TIMEOUT_SECONDS = int(perf_config.get("api_timeout_seconds", 180))
ROUTER_RETRY_TIMES = max(1, int(perf_config.get("retry_times", 3)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "One-click flow: source.tex -> create input case -> run pipeline -> "
            "publish -> fix math punctuation -> build PDF."
        )
    )
    parser.add_argument(
        "module_selector",
        nargs="?",
        default=None,
        help=(
            "Module selector for create_next_input_case.py, e.g. 03 / conic / 03_conic. "
            "If omitted, module is auto-detected from source.tex via API."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands only; do not execute any step.",
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable path used to run sub-scripts. Default: current interpreter.",
    )
    return parser.parse_args()


def quoted_command(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def ensure_source_tex_ready(source_tex: Path) -> None:
    if not source_tex.is_file():
        raise FileNotFoundError(f"Missing source file: {source_tex}")
    if source_tex.stat().st_size == 0:
        raise ValueError(f"source.tex is empty: {source_tex}")


def read_text_file(path: Path) -> str:
    encodings = ("utf-8", "utf-8-sig", "gb18030")
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding).strip()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode file with supported encodings: {path}")


def render_prompt(step: str, input_data: Any) -> str:
    template = load_prompt(step)
    payload = (
        input_data
        if isinstance(input_data, str)
        else json.dumps(input_data, ensure_ascii=False, indent=2)
    )
    if "{{input}}" in template:
        return template.replace("{{input}}", payload)
    return f"{template}\n\n{payload}"


def call_router_llm(prompt: str) -> str:
    if not ROUTER_MODEL:
        raise ValueError("Missing model.default in app_config.json")

    last_error: Exception | None = None
    for attempt in range(ROUTER_RETRY_TIMES):
        try:
            client = OpenAI(
                api_key=api_config["api_key"],
                base_url=api_config["base_url"],
            )
            response = client.chat.completions.create(
                model=ROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=ROUTER_TEMPERATURE,
                timeout=ROUTER_TIMEOUT_SECONDS,
            )
            content = response.choices[0].message.content
            return content if isinstance(content, str) else str(content)
        except Exception as exc:  # pragma: no cover - network/API runtime
            last_error = exc
            if attempt >= ROUTER_RETRY_TIMES - 1:
                break
            sleep_s = (2**attempt) + random.random()
            print(
                f"[warn] module-router retry {attempt + 1}/{ROUTER_RETRY_TIMES} "
                f"after {sleep_s:.2f}s: {exc}"
            )
            time.sleep(sleep_s)

    raise RuntimeError(f"module-router api failed: {last_error}")


def extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def parse_json_like(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    cleaned = text.replace("```json", "").replace("```", "").strip()
    candidates: list[str] = []
    extracted = extract_first_json_object(cleaned)
    if extracted:
        candidates.append(extracted)
    if cleaned:
        candidates.append(cleaned)

    for candidate in candidates:
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            continue
    return {}


def normalize_module_name(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().lower().strip("`'\"")
    if not text:
        return None

    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"^\d{2}[_-]", "", text)
    text = text.replace("/", "-").replace("_", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")

    if text in ALLOWED_MODULE_SET:
        return text
    return MODULE_ALIASES.get(text)


def extract_module_candidate(raw_output: str | None) -> str | None:
    if not raw_output:
        return None

    parsed = parse_json_like(raw_output)
    for key in ("module", "selected_module", "best_module", "module_name", "result"):
        candidate = parsed.get(key)
        normalized = normalize_module_name(candidate if isinstance(candidate, str) else None)
        if normalized:
            return normalized

    lowered = raw_output.lower()
    for module in sorted(ALLOWED_MODULES, key=len, reverse=True):
        pattern = rf"(?<![a-z]){re.escape(module)}(?![a-z])"
        if re.search(pattern, lowered):
            return module

    module_dir_match = re.search(r"\b\d{2}[_-][a-z][a-z0-9_-]*\b", lowered)
    if module_dir_match:
        normalized = normalize_module_name(module_dir_match.group(0))
        if normalized:
            return normalized

    for alias, module in MODULE_ALIASES.items():
        if any(ord(ch) > 127 for ch in alias) and alias in raw_output:
            return module
    return None


def detect_module_by_keywords(source_text: str) -> tuple[str, int]:
    text = source_text.lower()
    scores = {module: 0 for module in ALLOWED_MODULES}

    for module, rules in MODULE_KEYWORDS.items():
        for token, weight in rules:
            if token.lower() in text:
                scores[module] += weight

    best_module = max(
        ALLOWED_MODULES,
        key=lambda module: (scores[module], -MODULE_ORDER[module]),
    )
    best_score = scores[best_module]
    if best_score <= 0:
        return "function", 0
    return best_module, best_score


def auto_detect_module_selector(source_tex: Path) -> tuple[str, str]:
    source_text = read_text_file(source_tex)

    primary_prompt = render_prompt(
        "module_router",
        {
            "source_tex": source_text,
            "allowed_modules": list(ALLOWED_MODULES),
        },
    )
    try:
        primary_output = call_router_llm(primary_prompt)
    except Exception as exc:  # pragma: no cover - network/API runtime
        fallback_module, score = detect_module_by_keywords(source_text)
        print(
            f"[warn] module-router api unavailable; fallback=keyword, "
            f"module={fallback_module}, score={score}, error={exc}"
        )
        return fallback_module, "keyword-fallback(api-error)"

    primary_module = extract_module_candidate(primary_output)
    if primary_module:
        return primary_module, "llm-primary"

    preview = re.sub(r"\s+", " ", primary_output).strip()
    if len(preview) > 160:
        preview = preview[:160] + "..."
    print(f"[warn] module-router out-of-enum output, trying repair. raw={preview}")

    repair_prompt = MODULE_REPAIR_PROMPT.format(
        source_text=source_text,
        raw_output=primary_output,
    )
    try:
        repair_output = call_router_llm(repair_prompt)
    except Exception as exc:  # pragma: no cover - network/API runtime
        fallback_module, score = detect_module_by_keywords(source_text)
        print(
            f"[warn] module-repair api unavailable; fallback=keyword, "
            f"module={fallback_module}, score={score}, error={exc}"
        )
        return fallback_module, "keyword-fallback(repair-api-error)"

    repair_module = extract_module_candidate(repair_output)
    if repair_module:
        return repair_module, "llm-repair"

    fallback_module, score = detect_module_by_keywords(source_text)
    print(
        f"[warn] module-repair still invalid; fallback=keyword, "
        f"module={fallback_module}, score={score}"
    )
    return fallback_module, "keyword-fallback(parse-error)"


def run_command(label: str, cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    print(f"[start] {label}")
    print(f"[cmd] {quoted_command(cmd)}")
    t0 = time.perf_counter()
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - t0

    if completed.returncode != 0:
        print(f"[fail] {label} ({elapsed:.2f}s)")
        if completed.stdout.strip():
            print("[stdout]")
            print(completed.stdout.rstrip())
        if completed.stderr.strip():
            print("[stderr]")
            print(completed.stderr.rstrip())
        raise RuntimeError(f"{label} failed with exit code {completed.returncode}")

    print(f"[ok]   {label} ({elapsed:.2f}s)")
    return completed


def parse_new_id(stdout: str) -> str:
    match = NEW_ID_PATTERN.search(stdout)
    if not match:
        raise ValueError("Cannot parse NEW_ID from create_next_input_case.py output.")
    return match.group(1).upper()


def run_flow(args: argparse.Namespace) -> int:
    script_path = Path(__file__).resolve()
    pipeline_dir = script_path.parent
    project_root = pipeline_dir.parent
    source_tex = pipeline_dir / "source.tex"

    ensure_source_tex_ready(source_tex)
    module_selector = args.module_selector
    module_selector_source = "manual"
    if not module_selector:
        print("[info] module_selector omitted; auto-detecting module from source.tex")
        module_selector, module_selector_source = auto_detect_module_selector(source_tex)
        print(
            f"[info] Auto-selected module={module_selector} "
            f"(source={module_selector_source})"
        )
    else:
        print(f"[info] Use manual module selector: {module_selector}")

    python_exe = str(Path(args.python_exe))
    create_script = pipeline_dir / "create_next_input_case.py"
    run_script = pipeline_dir / "run_pipeline.py"
    publish_script = pipeline_dir / "publish_pipeline_output.py"
    fix_script = project_root / "scripts" / "fix_math_punctuation.py"
    build_pdf_script = project_root / "scripts" / "build_conclusion_pdfs.py"

    if args.dry_run:
        planned_id = "<NEW_ID_FROM_STEP1>"
        plan = [
            ("Step 1/5 create next input case", [python_exe, str(create_script), module_selector]),
            ("Step 2/5 run pipeline", [python_exe, str(run_script), planned_id]),
            ("Step 3/5 publish output", [python_exe, str(publish_script), planned_id]),
            ("Step 4/5 fix math punctuation", [python_exe, str(fix_script), planned_id]),
            (
                "Step 5/5 build PDF",
                [python_exe, str(build_pdf_script), planned_id, "--pdf-name-mode", "id"],
            ),
        ]
        print(f"[info] Project root: {project_root}")
        print(f"[info] source.tex: {source_tex}")
        print(f"[info] module selector source: {module_selector_source}")
        print("[info] Mode: dry-run")
        for label, cmd in plan:
            print(f"[plan] {label}")
            print(f"       {quoted_command(cmd)}")
        return 0

    print(f"[info] Project root: {project_root}")
    print(f"[info] source.tex: {source_tex}")
    print(f"[info] module selector source: {module_selector_source}")
    print("[info] Mode: execute")

    create_cmd = [python_exe, str(create_script), module_selector]
    create_result = run_command("Step 1/5 create next input case", create_cmd, project_root)
    if create_result.stdout.strip():
        print("[stdout]")
        print(create_result.stdout.rstrip())

    new_id = parse_new_id(create_result.stdout)
    print(f"[info] Parsed NEW_ID={new_id}")

    run_command(
        "Step 2/5 run pipeline",
        [python_exe, str(run_script), new_id],
        project_root,
    )
    run_command(
        "Step 3/5 publish output",
        [python_exe, str(publish_script), new_id],
        project_root,
    )
    run_command(
        "Step 4/5 fix math punctuation",
        [python_exe, str(fix_script), new_id],
        project_root,
    )
    run_command(
        "Step 5/5 build PDF",
        [python_exe, str(build_pdf_script), new_id, "--pdf-name-mode", "id"],
        project_root,
    )

    pdf_path = project_root / "build" / "conclusion_pdfs" / f"{new_id}.pdf"
    print(f"NEW_ID={new_id}")
    print(f"PDF_EXPECTED={pdf_path}")
    if pdf_path.is_file():
        print(f"PDF_READY={pdf_path}")
    else:
        print(f"[warn] PDF file not found yet: {pdf_path}")

    return 0


def main() -> int:
    args = parse_args()
    try:
        return run_flow(args)
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"[error] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
