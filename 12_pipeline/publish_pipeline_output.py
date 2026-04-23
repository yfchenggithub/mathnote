#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
publish_pipeline_output.py

将 `12_pipeline/output/<ID>/` 的发布产物同步到模块目录，
并补齐可编译的二级结论结构（`main.tex`、`meta.json`、`source.tex`、`index.tex` 入口）。

------------------------------------------------------------
一、脚本定位
------------------------------------------------------------
本脚本是“发布层”工具，负责把 pipeline 产出的结构化内容落到项目真实目录。
它的目标不是生成内容本身，而是保证“目录结构正确、文件齐全、日志可追踪”。

------------------------------------------------------------
二、核心功能
------------------------------------------------------------
1) 自动识别要发布的 ID（支持全量扫描或 `--ids` 指定）
2) 自动定位目标模块目录（支持 `--module-dir` 强制指定）
3) 自动复用/创建二级结论目录
4) 发布 01~06 讲义文件
5) 发布 `meta.json`
6) 同步 `source.tex`（默认不覆盖非空目标，空文件会自动替换）
7) 生成 `main.tex`
8) 更新模块 `index.tex` 的 `\\input{.../main.tex}` 入口

------------------------------------------------------------
三、发布流程（单个 ID）
------------------------------------------------------------
1) 校验 `12_pipeline/output/<ID>/` 是否存在
2) 读取 `l5_meta.json`
3) 解析模块目录（`choose_module`）
4) 解析结论目录（`choose_conclusion_dir`）
5) 执行发布步骤（讲义、meta、source、main、index）
6) 汇总结果到结构化日志

------------------------------------------------------------
四、常用命令
------------------------------------------------------------
1) 发布全部：
   `python 12_pipeline/publish_pipeline_output.py`
2) 指定 ID：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 I005`
3) 强制模块：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --module-dir 07_inequality`
4) 只更新 main：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --only main`
5) 只更新 meta：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --only meta`
6) 跳过 source：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --skip source`
7) 预演：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --dry-run`
8) 显示详细文件级日志：
   `python 12_pipeline/publish_pipeline_output.py --ids I004 --verbose`

------------------------------------------------------------
五、日志设计说明
------------------------------------------------------------
- 默认日志：优先展示“每个 ID 的关键步骤 + 最终汇总”
- `--verbose`：展示文件级明细，适合排查路径问题
- 失败与警告在最后集中列出，便于快速定位异常
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

LECTURE_FILES = (
    "01_statement.tex",
    "02_explanation.tex",
    "03_proof.tex",
    "04_examples.tex",
    "05_traps.tex",
    "06_summary.tex",
)

ID_PATTERN = re.compile(r"^[A-Za-z]\d{3}$")
INDEX_FILENAME = "index.tex"
L6_DIRNAME_FILE_PATTERN_TEMPLATE = r"^{item_id}_[a-z0-9]+(?:_[a-z0-9]+)*$"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# =========================================================
# 参数解析
# =========================================================


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数。

    为什么需要此函数：
    - 将 CLI 入口集中管理，便于未来扩展参数而不污染主流程。
    - 统一默认路径策略，确保脚本在仓库任意位置调用都能正确定位。

    Returns:
        argparse.Namespace:
            解析结果对象，例如：
            - `ids`: `["I004", "I005"]`
            - `dry_run`: `True`
            - `only`: `"main"`
            - `verbose`: `False`

    Example:
        `python 12_pipeline/publish_pipeline_output.py --ids I004 --dry-run --verbose`
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

    parser.add_argument("--ids", nargs="*", help="指定要发布的 ID")
    parser.add_argument(
        "positional_ids",
        nargs="*",
        help="位置参数 ID，等价于 --ids（示例：I004 I005）",
    )
    parser.add_argument("--module-dir", help="强制指定模块目录")

    parser.add_argument("--dry-run", action="store_true", help="只演示，不落盘")
    parser.add_argument("--verbose", action="store_true", help="显示详细文件级日志")

    parser.add_argument("--only", choices=["main", "meta"], help="只执行某一步")
    parser.add_argument("--skip", choices=["source"], help="跳过某一步")

    return parser.parse_args()


# =========================================================
# 工具函数
# =========================================================


def load_json(path: Path) -> dict:
    """
    加载 JSON 文件，兼容 UTF-8 与 UTF-8-BOM。

    为什么需要此函数：
    - pipeline 产物可能来自不同环境，编码不完全一致。
    - 把编码兼容逻辑收敛到一个地方，避免主流程充满 `try/except`。

    Args:
        path (Path): JSON 文件路径。
            示例：`Path("12_pipeline/output/I004/l5_meta.json")`

    Returns:
        dict: 解析后的 JSON 对象。

    Raises:
        json.JSONDecodeError: 文件不是合法 JSON。
        FileNotFoundError: 文件不存在。
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_key(text: str) -> str:
    """
    标准化字符串，便于模块别名匹配。

    为什么需要此函数：
    - 外部输入（CLI、meta）可能出现大小写、下划线、空格差异。
    - 统一成稳定键值后，可以显著降低匹配歧义。

    Args:
        text (str): 原始文本。
            示例：`"07_inequality"`、`"Inequality"`、`"07-inequality"`

    Returns:
        str: 规范化后的键，例如 `07-inequality`。
    """
    return re.sub(r"[-\s_]+", "-", text.strip().lower())


def ensure_dir(path: Path, dry_run: bool):
    """
    确保目录存在（支持 dry-run）。

    为什么需要此函数：
    - 将“是否落盘”的判断统一处理，减少重复代码与误写风险。

    Args:
        path (Path): 目标目录。
            示例：`Path("07_inequality/I004_Cubic_Mean_Inequality")`
        dry_run (bool): `True` 时不执行实际创建。
    """
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, dry_run: bool):
    """
    复制文件到目标位置（覆盖同名文件，支持 dry-run）。

    为什么需要此函数：
    - 发布动作里“复制文件”非常高频，统一实现便于维护和扩展。

    Args:
        src (Path): 源文件路径。
            示例：`Path("12_pipeline/output/I004/01_statement.tex")`
        dst (Path): 目标文件路径。
            示例：`Path("07_inequality/I004_Cubic_Mean_Inequality/01_statement.tex")`
        dry_run (bool): `True` 时仅演示，不执行写入。
    """
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_text(path: Path, text: str, dry_run: bool):
    """
    写入文本文件（UTF-8，LF 换行，支持 dry-run）。

    为什么需要此函数：
    - `main.tex` 等文本输出需要统一编码和换行策略，避免平台差异。

    Args:
        path (Path): 目标文件路径。
            示例：`Path("07_inequality/I004_Cubic_Mean_Inequality/main.tex")`
        text (str): 待写入内容。
        dry_run (bool): `True` 时不实际写入。
    """
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


def rel_path(path: Path, project_root: Path) -> str:
    """
    将绝对路径转换为相对项目根路径，用于简洁日志展示。

    为什么需要此函数：
    - 完整绝对路径太长，会掩盖日志重点。

    Args:
        path (Path): 任意路径。
        project_root (Path): 项目根目录。
            示例：`Path("d:/mathnote")`

    Returns:
        str: 相对路径字符串；若失败则退化为原路径字符串。
    """
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def format_id_preview(ids, limit=10) -> str:
    """
    格式化 ID 预览文本，避免启动日志过长。

    为什么需要此函数：
    - 全量发布时 ID 可能很多，直接打印完整列表可读性差。

    Args:
        ids (list[str]): ID 列表。
            示例：`["I001", "I002", "I003"]`
        limit (int): 预览上限，默认 10。

    Returns:
        str: 用于日志的简短预览字符串。
    """
    if not ids:
        return "(none)"
    if len(ids) <= limit:
        return ", ".join(ids)
    head = ", ".join(ids[:limit])
    return f"{head}, ... (+{len(ids) - limit})"


def split_csv_tokens(values: list[str] | None) -> list[str]:
    """
    将命令行参数按逗号与空格规则拆分为扁平 token 列表。
    """
    if not values:
        return []
    tokens: list[str] = []
    for raw in values:
        for token in raw.split(","):
            piece = token.strip()
            if piece:
                tokens.append(piece)
    return tokens


def normalize_ids(raw_ids: list[str] | None) -> list[str]:
    """
    标准化并校验 ID，输出去重后的大写 ID 列表。
    """
    if not raw_ids:
        return []

    normalized: list[str] = []
    invalid: list[str] = []
    for raw in raw_ids:
        item_id = raw.strip().upper()
        if not item_id:
            continue
        if not ID_PATTERN.fullmatch(item_id):
            invalid.append(raw)
            continue
        normalized.append(item_id)

    if invalid:
        bad = ", ".join(invalid)
        raise ValueError(f"ID 格式非法: {bad}（期望格式如 I004）")

    return list(dict.fromkeys(normalized))


# =========================================================
# 模块解析
# =========================================================


def list_module_dirs(project_root: Path):
    """
    扫描项目中的模块目录（命名形如 `00_set`、`07_inequality`）。

    为什么需要此函数：
    - 后续模块识别依赖“可选模块集合”，先统一收集可避免重复遍历。

    Args:
        project_root (Path): 项目根目录。
            示例：`Path("d:/mathnote")`

    Returns:
        list[Path]: 模块目录列表。
    """
    return [
        p
        for p in project_root.iterdir()
        if p.is_dir() and re.match(r"^\d{2}[_-].+", p.name)
    ]


def build_module_alias_map(module_dirs):
    """
    构建模块别名字典，支持“全名”和“去前缀名”两种查找。

    为什么需要此函数：
    - 用户可能输入 `07_inequality`，也可能输入 `inequality`。
    - 统一映射后，`choose_module` 可直接 O(1) 查找。

    Args:
        module_dirs (list[Path]): 模块目录列表。
            示例：`[Path("07_inequality"), Path("00_set")]`

    Returns:
        dict[str, Path]: 规范化别名到目录的映射。
    """
    mapping = {}
    for module_dir in module_dirs:
        mapping[normalize_key(module_dir.name)] = module_dir

        m = re.match(r"^\d{2}[_-](.+)$", module_dir.name)
        if m:
            mapping[normalize_key(m.group(1))] = module_dir

    return mapping


def list_l6_dirname_files(output_dir: Path, item_id: str) -> list[Path]:
    """
    列出 output/<ID>/ 下所有符合 L6 命名规则的文件。
    """
    if not output_dir.exists() or not output_dir.is_dir():
        return []

    pattern = re.compile(
        L6_DIRNAME_FILE_PATTERN_TEMPLATE.format(item_id=re.escape(item_id)),
        re.IGNORECASE,
    )
    files = [p for p in output_dir.iterdir() if p.is_file() and pattern.match(p.name)]
    files.sort(key=lambda p: p.name.lower())
    return files


def pick_l6_dirname(output_dir: Path, item_id: str) -> tuple[str | None, list[str]]:
    """
    选择 L6 命名文件，返回 (目录名候选, warnings)。
    """
    warnings: list[str] = []
    files = list_l6_dirname_files(output_dir, item_id)
    if not files:
        return None, warnings

    if len(files) > 1:
        names = ", ".join(p.name for p in files)
        warnings.append(f"L6 命名文件存在多个，已按字典序使用第一个: {names}")

    return files[0].name, warnings


def choose_module(item_id, meta, module_dirs, alias_map, forced):
    """
    决策目标模块目录（发布路由核心）。

    优先级：
    1. CLI 强制指定
    2. 已有目录命中
    3. meta.module
    4. ID 前缀推断

    为什么需要此函数：
    - 在“自动化发布”与“可控覆盖”之间做平衡，尽量自动，必要时可强制。

    Args:
        item_id (str): 当前 ID。
            示例：`"I004"`
        meta (dict): `l5_meta.json` 内容。
            示例：`{"module": "07_inequality", ...}`
        module_dirs (list[Path]): 可选模块目录集合。
        alias_map (dict[str, Path]): 模块别名映射。
        forced (str | None): CLI 强制模块参数。
            示例：`"07_inequality"` 或 `None`

    Returns:
        Path: 命中的模块目录。

    Raises:
        ValueError: 无法唯一确定模块或模块不存在。
    """
    if forced:
        key = normalize_key(forced)
        if key in alias_map:
            return alias_map[key]
        raise ValueError(f"无法识别模块: {forced}")

    hits = []
    for module_dir in module_dirs:
        for child in module_dir.iterdir():
            if child.is_dir() and child.name.upper().startswith(item_id):
                hits.append(child)

    if len(hits) == 1:
        return hits[0].parent
    if len(hits) > 1:
        raise ValueError(f"{item_id} 存在多个模块匹配")

    module_name = meta.get("module", "")
    if module_name:
        key = normalize_key(module_name)
        if key in alias_map:
            return alias_map[key]

    letter = item_id[0]
    mapping = {}
    for module_dir in module_dirs:
        for child in module_dir.iterdir():
            m = re.match(r"^([A-Za-z])\d{3}", child.name)
            if m:
                mapping.setdefault(m.group(1), set()).add(module_dir)

    candidates = mapping.get(letter, set())
    if len(candidates) == 1:
        return next(iter(candidates))

    raise ValueError(f"{item_id} 无法推断模块")


def choose_conclusion_dir(module_dir, item_id, meta, output_dir):
    """
    决策二级结论目录路径。

    为什么需要此函数：
    - 要兼容“已有目录复用”与“首次发布创建”两种场景。
    - 命名冲突时自动追加序号，避免误覆盖。

    Args:
        module_dir (Path): 模块目录。
            示例：`Path("07_inequality")`
        item_id (str): 当前 ID，例如 `"I004"`。
        meta (dict): 元数据字典，用于生成默认 slug。

    Returns:
        tuple[Path, list[str]]: (目标二级结论目录路径, warnings)。
    """
    warnings: list[str] = []

    # 优先使用 L6 产物（文件名即目录名）。
    l6_dirname, l6_warnings = pick_l6_dirname(output_dir, item_id)
    warnings.extend(l6_warnings)
    if l6_dirname:
        candidate = module_dir / l6_dirname
        if candidate.exists() and not candidate.is_dir():
            raise ValueError(f"L6 目标已存在但不是目录: {candidate}")
        return candidate, warnings

    # 回退到历史逻辑：先复用已有同 ID 目录，再按 module slug 生成。
    hits = [
        p for p in module_dir.iterdir() if p.is_dir() and p.name.upper().startswith(item_id)
    ]
    if len(hits) == 1:
        return hits[0], warnings

    slug = normalize_key(meta.get("module", "")).replace("-", "_") or "generated"
    base = module_dir / f"{item_id}_{slug}"

    if not base.exists():
        return base, warnings

    i = 2
    while True:
        p = module_dir / f"{base.name}_{i}"
        if not p.exists():
            return p, warnings
        i += 1


# =========================================================
# 发布步骤
# =========================================================


def publish_lecture_files(output_dir, target_dir, dry_run, verbose=False, project_root=None):
    """
    发布 01~06 讲义文件。

    为什么需要此函数：
    - 讲义文件集合固定且顺序明确，独立函数可保证校验与复制逻辑一致。

    Args:
        output_dir (Path): pipeline 输出目录。
            示例：`Path("12_pipeline/output/I004")`
        target_dir (Path): 目标结论目录。
            示例：`Path("07_inequality/I004_Cubic_Mean_Inequality")`
        dry_run (bool): `True` 时仅演示。
        verbose (bool): `True` 时打印文件级明细日志。
        project_root (Path | None): 项目根目录，用于生成相对路径日志。

    Returns:
        list[str]: 实际处理的文件名列表。
            示例：`["01_statement.tex", ..., "06_summary.tex"]`

    Raises:
        FileNotFoundError: 任一讲义文件缺失。
    """
    copied = []
    for name in LECTURE_FILES:
        src = output_dir / name
        if not src.exists():
            raise FileNotFoundError(f"缺少讲义文件: {src}")

        dst = target_dir / name
        copy_file(src, dst, dry_run)
        copied.append(name)

    if verbose and copied and project_root:
        logger.info("    文件明细:")
        for name in copied:
            logger.info(f"    - {rel_path(target_dir / name, project_root)}")

    return copied


def publish_meta(meta_src, target_dir, dry_run):
    """
    发布 `l5_meta.json` 到目标目录并命名为 `meta.json`。

    为什么需要此函数：
    - 元数据发布是独立步骤，支持 `--only meta` 单独执行。

    Args:
        meta_src (Path): 源 meta 路径。
            示例：`Path("12_pipeline/output/I004/l5_meta.json")`
        target_dir (Path): 目标结论目录。
        dry_run (bool): `True` 时不写入文件。

    Raises:
        FileNotFoundError: 元数据文件不存在。
    """
    if not meta_src.exists():
        raise FileNotFoundError(f"缺少元数据文件: {meta_src}")
    dst = target_dir / "meta.json"
    copy_file(meta_src, dst, dry_run)


def sync_source(input_root, item_id, target_dir, dry_run, skip):
    """
    同步 `source.tex`，默认不覆盖非空目标文件。

    为什么需要此函数：
    - `source.tex` 常带人工修改，默认策略必须保守，防止误覆盖。
    - 目标为空文件时自动替换，可修复异常中断留下的残缺文件。

    Args:
        input_root (Path): pipeline 输入根目录。
            示例：`Path("12_pipeline/input")`
        item_id (str): 当前 ID，例如 `"I004"`。
        target_dir (Path): 目标结论目录。
        dry_run (bool): `True` 时仅演示，不写入。
        skip (bool): 是否跳过此步骤（由 `--skip source` 控制）。

    Returns:
        str: 面向日志的人类可读状态文本。
            示例：`"已保留（目标已存在且非空）"`、`"已拷贝（替换空文件）"`
    """
    if skip:
        return "已跳过（--skip source）"

    src = input_root / item_id / "source.tex"
    if not src.exists():
        return "已跳过（输入目录无 source.tex）"

    dst = target_dir / "source.tex"
    if dst.exists() and dst.stat().st_size > 0:
        return "已保留（目标已存在且非空）"

    replaced_empty = dst.exists() and dst.stat().st_size == 0
    copy_file(src, dst, dry_run)
    if replaced_empty:
        return "已拷贝（替换空文件）"
    return "已拷贝"


def build_main(module_name, dir_name, title):
    """
    构建 `main.tex` 的文本内容。

    为什么需要此函数：
    - 将模板拼装逻辑与文件写入分离，便于测试和后续模板调整。

    Args:
        module_name (str): 模块目录名。
            示例：`"07_inequality"`
        dir_name (str): 二级结论目录名。
            示例：`"I004_Cubic_Mean_Inequality"`
        title (str): 结论标题。
            示例：`"Cubic Mean Inequality"`

    Returns:
        str: 完整的 `main.tex` 文本。
    """
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
    """
    根据元数据生成并写入 `main.tex`。

    为什么需要此函数：
    - `main.tex` 依赖标题和路径规则，独立函数能隔离模板与写盘细节。

    Args:
        meta (dict): 元数据字典。
        module_dir (Path): 模块目录。
        target_dir (Path): 结论目录。
        dry_run (bool): `True` 时不实际写入。

    Returns:
        str: 选用的标题文本（用于潜在日志或调试）。
    """
    title = meta.get("title") or meta.get("core", {}).get("title") or "Untitled"
    text = build_main(module_dir.name, target_dir.name, title)

    dst = target_dir / "main.tex"
    write_text(dst, text, dry_run)
    return title


def update_module_index(module_dir: Path, target_dir: Path, dry_run: bool):
    """
    更新模块 `index.tex`，确保包含当前结论的 `\\input{.../main.tex}` 入口。

    为什么需要此函数：
    - 发布后的结论需要被模块索引收录，否则不会出现在最终汇总文档中。
    - 使用返回 `(level, message)` 的方式，让主流程可统一处理警告与摘要日志。

    Args:
        module_dir (Path): 模块目录。
            示例：`Path("07_inequality")`
        target_dir (Path): 当前结论目录。
            示例：`Path("07_inequality/I004_Cubic_Mean_Inequality")`
        dry_run (bool): `True` 时仅演示，不落盘。

    Returns:
        tuple[str, str]:
            - level: `"ok"` 或 `"warn"`
            - message: 日志文本，例如 `"index.tex: 已追加入口"`
    """
    index_file = module_dir / INDEX_FILENAME
    input_line = f"\\input{{{module_dir.name}/{target_dir.name}/main.tex}}"

    if not index_file.exists():
        if not dry_run:
            index_file.write_text(input_line + "\n", encoding="utf-8")
        return "ok", "index.tex: 已创建并写入入口"

    try:
        lines = index_file.read_text(encoding="utf-8").splitlines(keepends=True)
    except Exception as exc:
        return "warn", f"index.tex 读取失败: {exc}"

    pattern = rf"^\s*\\input\{{{re.escape(module_dir.name)}/{re.escape(target_dir.name)}/main\.tex\}}"

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        if re.search(pattern, line):
            return "ok", "index.tex: 已存在入口"

    if dry_run:
        return "ok", "index.tex: 将追加入口（dry-run）"

    with index_file.open("a", encoding="utf-8") as f:
        if lines and not lines[-1].endswith("\n"):
            f.write("\n")
        f.write(input_line + "\n")

    return "ok", "index.tex: 已追加入口"


# =========================================================
# 调度流程
# =========================================================


def publish_one(item_id, args, module_dirs, alias_map):
    """
    发布单个 ID（调度器核心函数）。

    为什么需要此函数：
    - 把“单 ID 的完整流程”封装成可复用单元，便于主循环做失败隔离。
    - 统一返回结构化结果，方便日志和后续扩展（如写入报告文件）。

    Args:
        item_id (str): 当前发布 ID。
            示例：`"I004"`
        args (argparse.Namespace): CLI 参数对象。
            示例：包含 `dry_run`、`only`、`skip`、`verbose` 等字段。
        module_dirs (list[Path]): 可选模块目录列表。
        alias_map (dict[str, Path]): 模块别名映射。

    Returns:
        dict: 发布结果摘要，例如：
            `{
                "item_id": "I004",
                "target": "07_inequality/I004_Cubic_Mean_Inequality",
                "steps": ["讲义文件: 已发布 6 个", ...],
                "warnings": []
            }`

    Raises:
        FileNotFoundError: 输出目录/关键文件缺失。
        ValueError: 模块无法唯一确定等业务异常。
    """
    output_dir = args.output_root / item_id
    meta_src = output_dir / "l5_meta.json"

    if not output_dir.exists():
        raise FileNotFoundError(f"输出目录不存在: {output_dir}")

    meta = load_json(meta_src)

    module_dir = choose_module(item_id, meta, module_dirs, alias_map, args.module_dir)
    target_dir, naming_warnings = choose_conclusion_dir(
        module_dir, item_id, meta, output_dir
    )

    ensure_dir(target_dir, args.dry_run)

    result = {
        "item_id": item_id,
        "target": rel_path(target_dir, args.project_root),
        "steps": [],
        "warnings": list(naming_warnings),
    }

    if naming_warnings:
        result["steps"].append("目录命名: 使用 L6 产物（检测到多个候选，已按字典序选取）")
    elif target_dir.name.upper().startswith(item_id):
        l6_name, _ = pick_l6_dirname(output_dir, item_id)
        if l6_name and target_dir.name == l6_name:
            result["steps"].append("目录命名: 使用 L6 产物")

    if args.only == "main":
        publish_main(meta, module_dir, target_dir, args.dry_run)
        result["steps"].append("main.tex: 已生成（only 模式）")
        return result

    if args.only == "meta":
        publish_meta(meta_src, target_dir, args.dry_run)
        result["steps"].append("meta.json: 已同步（only 模式）")
        return result

    copied = publish_lecture_files(
        output_dir,
        target_dir,
        args.dry_run,
        verbose=args.verbose,
        project_root=args.project_root,
    )
    result["steps"].append(f"讲义文件: 已发布 {len(copied)} 个")

    publish_meta(meta_src, target_dir, args.dry_run)
    result["steps"].append("meta.json: 已同步")

    source_status = sync_source(
        args.input_root,
        item_id,
        target_dir,
        args.dry_run,
        args.skip == "source",
    )
    result["steps"].append(f"source.tex: {source_status}")

    publish_main(meta, module_dir, target_dir, args.dry_run)
    result["steps"].append("main.tex: 已生成")

    level, index_msg = update_module_index(module_dir, target_dir, args.dry_run)
    if level == "warn":
        result["warnings"].append(index_msg)
        result["steps"].append(f"index.tex: 警告（{index_msg}）")
    else:
        result["steps"].append(index_msg)

    return result


def detect_ids(output_root, ids):
    """
    确定本次要处理的 ID 列表。

    为什么需要此函数：
    - 兼容“用户显式指定”与“自动扫描全部”两种入口。

    Args:
        output_root (Path): pipeline 输出根目录。
            示例：`Path("12_pipeline/output")`
        ids (list[str] | None): CLI 指定 ID 列表。
            示例：`["I004", "I005"]` 或 `None`

    Returns:
        list[str]: 按字典序排序的 ID 列表。
    """
    if ids:
        return ids
    return sorted(
        [p.name for p in output_root.iterdir() if p.is_dir() and ID_PATTERN.match(p.name)]
    )


def mode_text(args) -> str:
    """
    生成运行模式的简短文本描述。

    为什么需要此函数：
    - 避免主流程里散落模式判断，使启动日志更统一。

    Args:
        args (argparse.Namespace): CLI 参数对象。

    Returns:
        str: 例如 `full`、`only=main`、`full (skip=source)`。
    """
    if args.only:
        return f"only={args.only}"
    if args.skip:
        return f"full (skip={args.skip})"
    return "full"


def main():
    """
    程序入口。

    职责：
    - 初始化上下文（参数、模块、ID）
    - 遍历 ID 并调用 `publish_one`
    - 做错误隔离与最终汇总输出

    说明：
    - 任意单个 ID 失败不会中断整体批处理。
    - 最终会集中输出失败明细与警告明细，便于快速排查。
    """
    args = parse_args()

    module_dirs = list_module_dirs(args.project_root)
    alias_map = build_module_alias_map(module_dirs)
    raw_ids = split_csv_tokens(args.ids) + split_csv_tokens(args.positional_ids)
    try:
        requested_ids = normalize_ids(raw_ids)
    except ValueError as exc:
        raise SystemExit(f"[error] {exc}") from exc
    ids = detect_ids(args.output_root, requested_ids)

    logger.info("========== Pipeline 发布 ==========")
    logger.info(f"模式: {mode_text(args)}")
    logger.info(f"dry-run: {'yes' if args.dry_run else 'no'} | verbose: {'yes' if args.verbose else 'no'}")
    logger.info(f"ID 数量: {len(ids)}")
    logger.info(f"ID 预览: {format_id_preview(ids)}")
    logger.info("===================================")

    if not ids:
        logger.info("未检测到可发布 ID，流程结束。")
        return

    success = 0
    failed = 0
    failures = []
    warning_items = []

    for item_id in ids:
        logger.info("")
        logger.info(f"[{item_id}] 开始")
        try:
            result = publish_one(item_id, args, module_dirs, alias_map)
            success += 1

            logger.info(f"[{item_id}] 目标: {result['target']}")
            for step in result["steps"]:
                logger.info(f"[{item_id}] {step}")

            for warning in result["warnings"]:
                warning_items.append((item_id, warning))
                logger.warning(f"[{item_id}] 警告: {warning}")

            logger.info(f"[{item_id}] 完成")
        except Exception as exc:
            failed += 1
            failures.append((item_id, str(exc)))
            logger.error(f"[{item_id}] 失败: {exc}")

    logger.info("")
    logger.info("============= 发布汇总 =============")
    logger.info(f"总计: {len(ids)}")
    logger.info(f"成功: {success}")
    logger.info(f"失败: {failed}")
    logger.info(f"警告: {len(warning_items)}")

    if failures:
        logger.info("失败明细:")
        for item_id, reason in failures:
            logger.info(f"  - {item_id}: {reason}")

    if warning_items:
        logger.info("警告明细:")
        for item_id, warning in warning_items:
            logger.info(f"  - {item_id}: {warning}")

    logger.info("===================================")


if __name__ == "__main__":
    main()
