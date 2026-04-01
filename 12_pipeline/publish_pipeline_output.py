#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
publish_pipeline_output.py

========================================================
📦 Pipeline 发布脚本（工程级 · 强可维护版本）
========================================================

【一、脚本定位】

该脚本用于：
👉 将 pipeline 生成的结构化内容（output/<ID>/）发布到项目模块目录中
👉 构建最终可编译的 LaTeX 二级结论结构

----------------------------------------
【二、核心功能】

✔ 自动识别待发布 ID
✔ 自动推断目标模块目录（4级策略）
✔ 自动创建 / 复用二级结论目录
✔ 发布讲义文件（01~06）
✔ 同步 meta.json
✔ 补充 source.tex（可跳过）
✔ 自动生成 main.tex（可单独执行）

----------------------------------------
【三、发布流程（Pipeline）】

对每个 ID：

    1️⃣ 校验 output/<ID> 是否存在
    2️⃣ 加载 l5_meta.json
    3️⃣ 解析目标模块目录（resolve_module）
    4️⃣ 解析目标结论目录（resolve_conclusion_dir）
    5️⃣ 发布讲义文件（01~06）
    6️⃣ 发布 meta.json
    7️⃣ 同步 source.tex（可选）
    8️⃣ 生成 main.tex

👉 特点：每一步都是独立函数，可单独调试

----------------------------------------
【四、CLI 使用方式】

# 发布全部
python publish_pipeline_output.py

# 指定 ID
python publish_pipeline_output.py --ids I001 I002

# 强制模块
python publish_pipeline_output.py --module-dir 07_inequality

# 仅生成 main.tex
python publish_pipeline_output.py --only main

# 仅更新 meta.json
python publish_pipeline_output.py --only meta

# 跳过 source.tex
python publish_pipeline_output.py --skip source

# 预演（不写入）
python publish_pipeline_output.py --dry-run

----------------------------------------
【五、设计原则】

✔ 可读性：结构 = pipeline
✔ 可维护：函数职责单一
✔ 可调试：每一步都有日志
✔ 可扩展：未来可接 Web / API / 小程序
✔ 安全性：不覆盖已有 source.tex

"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
from pathlib import Path


# =========================================================
# 全局配置
# =========================================================

# 需要发布的讲义文件（严格顺序）
LECTURE_FILES = (
    "01_statement.tex",
    "02_explanation.tex",
    "03_proof.tex",
    "04_examples.tex",
    "05_traps.tex",
    "06_summary.tex",
)

# ID 格式校验（如 I001）
ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")

# 日志系统（可扩展为文件输出）
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# =========================================================
# 参数解析
# =========================================================


def parse_args() -> argparse.Namespace:
    """
    解析 CLI 参数

    👉 所有路径都支持覆盖（方便未来接 API / CI）
    👉 新增 only / skip 控制发布粒度
    """
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[1]

    parser = argparse.ArgumentParser(description="Pipeline 发布脚本")

    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument(
        "--input-root", type=Path, default=project_root / "12_pipeline/input"
    )
    parser.add_argument(
        "--output-root", type=Path, default=project_root / "12_pipeline/output"
    )

    parser.add_argument("--ids", nargs="*", help="指定 ID")
    parser.add_argument("--module-dir", help="强制模块目录")

    parser.add_argument("--dry-run", action="store_true", help="仅预演")

    # 👉 发布粒度控制
    parser.add_argument("--only", choices=["main", "meta"])
    parser.add_argument("--skip", choices=["source"])

    return parser.parse_args()


# =========================================================
# 基础工具函数
# =========================================================


def load_json(path: Path) -> dict:
    """
    加载 JSON（兼容 utf-8 / utf-8-sig）
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_key(text: str) -> str:
    """
    标准化字符串（用于模块匹配）
    """
    return re.sub(r"[-\s_]+", "-", text.strip().lower())


def ensure_dir(path: Path, dry_run: bool):
    """确保目录存在"""
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, dry_run: bool):
    """复制文件（覆盖）"""
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_text(path: Path, text: str, dry_run: bool):
    """写入文本文件"""
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


# =========================================================
# 模块解析（核心逻辑）
# =========================================================


def list_module_dirs(project_root: Path):
    """
    扫描模块目录（如 00_set / 07_inequality）
    """
    return [
        p
        for p in project_root.iterdir()
        if p.is_dir() and re.match(r"^\d{2}[_-].+", p.name)
    ]


def build_module_alias_map(module_dirs):
    """
    构建模块别名映射：

    支持：
    - 07_inequality
    - inequality
    """
    mapping = {}
    for d in module_dirs:
        mapping[normalize_key(d.name)] = d

        m = re.match(r"^\d{2}[_-](.+)$", d.name)
        if m:
            mapping[normalize_key(m.group(1))] = d

    return mapping


def choose_module(item_id, meta, module_dirs, alias_map, forced):
    """
    决策目标模块目录（核心路由逻辑）

    优先级：

    1️⃣ CLI 强制指定
    2️⃣ 扫描已有目录
    3️⃣ meta.module
    4️⃣ ID 前缀推断

    👉 若冲突 → 抛异常（必须人工处理）
    """

    if forced:
        key = normalize_key(forced)
        if key in alias_map:
            return alias_map[key]
        raise ValueError(f"无法识别模块：{forced}")

    # 已存在目录
    hits = []
    for d in module_dirs:
        for c in d.iterdir():
            if c.is_dir() and c.name.upper().startswith(item_id):
                hits.append(c)

    if len(hits) == 1:
        return hits[0].parent
    if len(hits) > 1:
        raise ValueError(f"{item_id} 存在多个模块匹配")

    # meta
    m = meta.get("module", "")
    if m:
        key = normalize_key(m)
        if key in alias_map:
            return alias_map[key]

    # 推断
    letter = item_id[0]
    mapping = {}
    for d in module_dirs:
        for c in d.iterdir():
            m = re.match(r"^([A-Za-z])\d{3}", c.name)
            if m:
                mapping.setdefault(m.group(1), set()).add(d)

    s = mapping.get(letter, set())
    if len(s) == 1:
        return next(iter(s))

    raise ValueError(f"{item_id} 无法推断模块")


def choose_conclusion_dir(module_dir, item_id, meta):
    """
    决定二级结论目录：

    ✔ 已存在 → 复用
    ✔ 不存在 → 自动创建
    ✔ 冲突 → 自动编号
    """
    hits = [
        p
        for p in module_dir.iterdir()
        if p.is_dir() and p.name.upper().startswith(item_id)
    ]

    if len(hits) == 1:
        return hits[0]

    slug = normalize_key(meta.get("module", "")).replace("-", "_") or "generated"
    base = module_dir / f"{item_id}_{slug}"

    if not base.exists():
        return base

    i = 2
    while True:
        p = module_dir / f"{base.name}_{i}"
        if not p.exists():
            return p
        i += 1


# =========================================================
# 发布步骤（Pipeline 原子操作）
# =========================================================


def publish_lecture_files(output_dir, target_dir, dry_run):
    """发布 01~06 讲义文件"""
    for f in LECTURE_FILES:
        src = output_dir / f
        if not src.exists():
            raise FileNotFoundError(src)

        dst = target_dir / f
        logger.info(f"COPY {src} -> {dst}")
        copy_file(src, dst, dry_run)


def publish_meta(meta_src, target_dir, dry_run):
    """发布 meta.json"""
    dst = target_dir / "meta.json"
    logger.info(f"COPY {meta_src} -> {dst}")
    copy_file(meta_src, dst, dry_run)


def sync_source(input_root, item_id, target_dir, dry_run, skip):
    """
    同步 source.tex（只补，不覆盖）
    """
    if skip:
        logger.info("SKIP source.tex")
        return

    dst = target_dir / "source.tex"
    if dst.exists():
        return

    src = input_root / item_id / "source.tex"
    if src.exists():
        logger.info(f"COPY {src} -> {dst}")
        copy_file(src, dst, dry_run)


def build_main(module_name, dir_name, title):
    """构建 main.tex 内容"""
    prefix = f"{module_name}/{dir_name}"
    title = title.replace("_", r"\_")

    return "\n".join(
        [
            "% =========================",
            f"% {title}",
            "% =========================",
            r"\Conclusion",
            rf"\subsection{{{title}}}",
            rf"\input{{{prefix}/01_statement}}",
            rf"\input{{{prefix}/02_explanation}}",
            rf"\input{{{prefix}/03_proof}}",
            rf"\input{{{prefix}/04_examples}}",
            rf"\input{{{prefix}/05_traps}}",
            rf"\input{{{prefix}/06_summary}}",
            "",
        ]
    )


def publish_main(meta, module_dir, target_dir, dry_run):
    """生成 main.tex"""
    title = meta.get("title") or meta.get("core", {}).get("title") or "Untitled"
    text = build_main(module_dir.name, target_dir.name, title)

    dst = target_dir / "main.tex"
    logger.info(f"WRITE {dst}")
    write_text(dst, text, dry_run)


# =========================================================
# 主流程（调度器）
# =========================================================


def publish_one(item_id, args, module_dirs, alias_map):
    """
    发布单个 ID（流程调度）

    👉 只做 orchestration，不做具体逻辑
    """

    output_dir = args.output_root / item_id
    meta_src = output_dir / "l5_meta.json"

    if not output_dir.exists():
        raise FileNotFoundError(output_dir)

    meta = load_json(meta_src)

    module_dir = choose_module(item_id, meta, module_dirs, alias_map, args.module_dir)
    target_dir = choose_conclusion_dir(module_dir, item_id, meta)

    ensure_dir(target_dir, args.dry_run)

    # 👉 only 控制
    if args.only == "main":
        publish_main(meta, module_dir, target_dir, args.dry_run)
        return

    if args.only == "meta":
        publish_meta(meta_src, target_dir, args.dry_run)
        return

    # 👉 正常流程
    publish_lecture_files(output_dir, target_dir, args.dry_run)
    publish_meta(meta_src, target_dir, args.dry_run)
    sync_source(
        args.input_root, item_id, target_dir, args.dry_run, args.skip == "source"
    )
    publish_main(meta, module_dir, target_dir, args.dry_run)


def detect_ids(output_root, ids):
    """检测 ID 列表"""
    if ids:
        return ids
    return [
        p.name for p in output_root.iterdir() if p.is_dir() and ID_PATTERN.match(p.name)
    ]


def main():
    """
    程序入口

    👉 负责：
    - 初始化
    - 遍历 ID
    - 错误隔离（单个失败不影响整体）
    """
    args = parse_args()

    module_dirs = list_module_dirs(args.project_root)
    alias_map = build_module_alias_map(module_dirs)

    ids = detect_ids(args.output_root, args.ids)

    logger.info("========== Pipeline Publish ==========")
    logger.info(f"IDs: {ids}")
    logger.info("=====================================")

    success = 0
    failed = 0

    for item_id in ids:
        try:
            publish_one(item_id, args, module_dirs, alias_map)
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"[{item_id}] ERROR: {e}")

    logger.info("=====================================")
    logger.info(f"SUCCESS: {success}, FAILED: {failed}")
    logger.info("=====================================")


if __name__ == "__main__":
    main()
