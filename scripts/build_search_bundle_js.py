# -*- coding: utf-8 -*-
"""
===============================================================================
build_search_bundle_js.py
===============================================================================

作用
----
从项目中的 `meta.json` 构建一个“单文件搜索包” JS 模块，供小程序端直接
`require` 使用。

这个脚本的核心目标
------------------
1. 更快：
   把运行时需要做的“文本拆词、前缀扩展、候选建议、静态排序”尽量前移到构建期。
2. 更准：
   不同来源字段有不同权重，并支持中文、拼音、拼音首字母、公式归一化和标题子串。
3. 可扩展：
   通过 `FieldSpec` 描述字段来源、权重和索引策略，新加字段时尽量只改一处。
4. 可调试：
   支持 `--dry-run`、`--debug-doc`、`--debug-term`、`--embed-debug`，方便定位召回和排序问题。
5. 可维护：
   文件头、数据结构、函数职责都写清楚，让后续维护者不需要先读业务代码才能改索引。

为什么改成一个文件
-------------------
旧版脚本输出 `core_index.js / rank_index.js / suggest_index.js` 三个文件。
现在统一输出 `data/search_engine/search_bundle.js`，这样做有几个直接收益：

1. 小程序端只需要加载一次，减少 I/O 和模块协调成本。
2. 索引、排序、补全一定来自同一批构建数据，避免版本错位。
3. 调试时只需要检查一个产物，定位更直接。
4. 后续如果继续压缩、分模块、分包，也可以以 bundle 为唯一事实来源。

常见用法
--------
1. 全量自动发现模块并构建：
   `python scripts/build_search_bundle_js.py`
2. 只构建一个模块：
   `python scripts/build_search_bundle_js.py --module 07_inequality`
3. 只构建某个条目并查看它的索引展开结果：
   `python scripts/build_search_bundle_js.py --item I005 --debug-doc I005 --dry-run`
4. 检查某个查询词最终会命中哪些倒排项：
   `python scripts/build_search_bundle_js.py --debug-term 柯西不等式 --dry-run`
5. 输出更易读的 JS，并把调试信息嵌入 bundle：
   `python scripts/build_search_bundle_js.py --pretty --embed-debug`

兼容入口
--------
如果你历史上一直在用旧命令，也可以继续用：
`python scripts/build_core_index.py ...`
它会转发到本脚本。

命令行参数说明
--------------
`--base-dir`
  项目根目录。默认是脚本上一级目录。需要它是因为模块自动发现依赖项目目录结构。
`--output-file`
  输出文件位置。默认写到 `data/search_engine/search_bundle.js`。
`--module`
  只构建指定模块，可重复传入。用来缩小构建范围和调试成本。
`--item`
  只构建指定条目目录名或文档 id，可重复传入。用来精确调试单题召回。
`--dry-run`
  只构建内存数据并打印统计，不落盘。适合先验证规则再真正写文件。
`--debug`
  打开更详细日志，方便排查扫描流程和跳过原因。
`--strict`
  遇到缺失文件、非法 JSON、重复 id 等问题时直接失败，而不是 warning 后继续。
`--pretty`
  让输出 JS 使用缩进格式，方便人工检查 bundle 内容。
`--embed-debug`
  在最终 bundle 里附带 debug 数据，便于端上或离线分析索引来源。
`--debug-doc`
  输出指定 doc 的字段展开详情，看每个字段如何变成 exact/prefix/suggest 候选。
`--debug-term`
  输出指定查询词在 `termIndex` 和 `prefixIndex` 中的命中情况。
`--prefix-doc-limit`
  每个前缀词最多保留多少条 posting。这个字段存在是为了控制包体积。
`--suggestion-limit`
  最终建议词数量上限。这个字段存在是为了限制低价值候选侵占空间。

输出结构
--------
module.exports = {
  version,
  generatedAt,
  stats,
  buildOptions,
  fieldMaskLegend,
  docs,
  termIndex,
  prefixIndex,
  suggestions,
  debug?,
}

输出字段说明
------------
`version`
  产物结构版本号。后续如果改 bundle 格式，端上可以据此兼容处理。
`generatedAt`
  构建时间。排查线上 bundle 是否过期时很有用。
`stats`
  文档数、倒排词数、前缀数、建议词数和模块统计。用于验收构建结果是否异常。
`buildOptions`
  构建时的关键参数快照。出现“为什么这个包这么大/这么小”时可快速对照。
`fieldMaskLegend`
  字段名到 bit mask 的映射。posting 里只存 int，节省体积，同时还能还原命中来源。
`docs`
  端上展示和排序需要的文档概要信息。查询只返回 docId 时，要靠它补足标题和摘要。
`termIndex`
  精确倒排索引。负责高精度召回，是搜索结果“准”的主干。
`prefixIndex`
  前缀倒排索引。负责增量输入场景，如用户只输入标题前半段或拼音前缀。
`suggestions`
  搜索联想列表。提前构建比端上临时生成更稳定，也更容易做质量控制。
`debug`
  可选调试信息。默认不输出，避免无意义增大包体。

索引格式（关键）
----------------
`termIndex` / `prefixIndex` 的 value 都是 posting 列表，格式为：
`[docId, score, fieldMask]`

注意：`termIndex` / `prefixIndex` 的 key 都是“构建期归一化后的字符串”。
端上查询时需要对用户输入做同样的归一化（NFKC、转小写、清理空白；公式字段还会做 LaTeX 符号替换并去空格）。

`docId`
  文档 id，对应 `docs[docId]`。
`score`
  命中分数（整数）。构建时按“字段权重 × 变体系数”计算。
  - exact 命中：同一个 `(term, docId)` 如果来自多个字段/多种变体，会累加分数。
  - prefix 命中：prefix 侧还会额外乘一个折扣系数 `prefix_ratio`（默认 0.70）；同一个 `(prefix, docId)` 取最大分（而不是累加），用于抑制噪声与体积膨胀。
`fieldMask`
  命中字段来源位图（整数）。按位或累积，可用 `fieldMaskLegend` 反解命中来源字段。

posting 列表在构建期已经排序：
1. score 降序
2. docs[docId].rank 降序
3. docId 升序（稳定）

`prefixIndex` 的 posting 列表还会被截断到 `buildOptions.prefixDocLimit`，用来控制包体大小。

`suggestions` 的每一行格式为：
`[displayText, docId, score]`

`displayText`
  展示给用户的联想文本（尽量保持原始可读形式）。
`docId`
  推荐跳转/联想命中的主文档。
`score`
  联想排序分（整数），用于把更重要的候选排在前面。
  当前实现是 `score = field_weight + docs[docId].rank`。

端上推荐流程
------------
1. 标准化用户输入。
2. 先查 `termIndex` 做高精度召回。
3. 再查 `prefixIndex` 兜底做增量召回。
4. 汇总命中分数，并根据 `fieldMask` 保留命中来源。
5. 叠加 `docs[docId].rank` 做静态排序微调。
6. 最终输出标题、摘要、标签等展示信息。

维护入口
--------
优先修改：
- `FIELD_SPECS`
- `build_feature_variants`
- `compute_rank_score`

如果你要做这些改动，优先参考这里：
- 新增一个可被搜索的业务字段：先改 `FIELD_SPECS`，必要时补一个 extractor。
- 调整召回形态：改 `build_feature_variants`。
- 调整排序偏好：改 `compute_rank_score`。
- 调整输出包结构：改 `build_doc_record` 和 `run_build` 里的 bundle 组装段。

Last Updated: 2026-04-05
===============================================================================
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, DefaultDict

try:
    from pypinyin import lazy_pinyin
except ImportError:  # pragma: no cover
    lazy_pinyin = None


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "data" / "search_engine" / "search_bundle.js"
META_FILENAME = "meta.json"
DEFAULT_TARGET_MODULES: tuple[str, ...] = ()
DEFAULT_PREFIX_DOC_LIMIT = 32
DEFAULT_SUGGESTION_LIMIT = 500
IGNORED_TOP_LEVEL_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "assets",
    "data",
    "misc",
    "node_modules",
    "scripts",
    "search_engine",
    "templates",
}
DEFAULT_SEARCHMETA_WEIGHTS = {
    "titleWeight": 10,
    "keywordWeight": 8,
    "synonymWeight": 6,
    "ocrWeight": 9,
    "formulaWeight": 7,
}

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]+")
LATIN_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._/+\\-]*")
WHITESPACE_RE = re.compile(r"\s+")
FRAGMENT_SPLIT_RE = re.compile(r"[，。；;、,:：!?！？\n\r\t]+")
ALT_NODE_SPLIT_RE = re.compile(r"[,，;；、/|]+")
FORMULA_REPLACEMENTS = (
    (r"\geqslant", ">="),
    (r"\geq", ">="),
    (r"\leqslant", "<="),
    (r"\leq", "<="),
    (r"\neq", "!="),
    (r"\times", "*"),
    (r"\cdot", "*"),
    (r"\left", ""),
    (r"\right", ""),
)

LOGGER = logging.getLogger("build_search_bundle_js")


class BuildError(RuntimeError):
    """表示构建阶段的可解释错误。"""


@dataclass(frozen=True)
class BuildConfig:
    """构建流程的只读配置。

    之所以集中成一个 dataclass，而不是把参数散落在函数签名里，是为了：
    1. 让 `run_build` 及其子流程更容易测试。
    2. 让 CLI 参数和构建语义之间有明确的一次转换。
    3. 后续如果增加配置项，只需要在一个对象里扩展。
    """

    project_root: Path
    output_file: Path
    target_modules: tuple[str, ...]
    target_items: tuple[str, ...]
    dry_run: bool
    debug: bool
    strict: bool
    pretty: bool
    embed_debug: bool
    prefix_doc_limit: int
    suggestion_limit: int
    debug_docs: tuple[str, ...]
    debug_terms: tuple[str, ...]


@dataclass(frozen=True)
class FieldSpec:
    """描述“一个搜索字段该如何被抽取和索引”。

    这个结构是脚本可扩展性的核心。新增字段时，优先新增 extractor 再补一条
    `FieldSpec`，而不是把逻辑直接散落到主循环里。

    Attributes
    ----------
    name:
        字段名。会写入 `fieldMaskLegend`，也会出现在 debug 输出里。
        需要它，是为了知道某条 posting 究竟来自标题、同义词还是公式。
    extractor:
        从 meta 中提取原始文本的函数。
        需要它，是为了把“数据来源”从“索引策略”中解耦。
    base_weight:
        该字段的基础权重。
        需要它，是为了让标题、关键词、同义词、正文片段天然有不同优先级。
    searchmeta_key:
        对应 `searchmeta` 中的动态调权键。
        需要它，是为了允许内容侧在不改脚本的前提下微调字段重要性。
    include_prefix:
        是否给该字段生成前缀召回。
        需要它，是因为不是所有字段都适合前缀匹配，例如长摘要做前缀会噪声过大。
    include_suggest:
        是否把该字段作为联想候选展示文本。
        需要它，是为了把“适合召回”和“适合展示”的字段区分开。
    include_pinyin:
        是否为中文文本额外生成拼音与拼音首字母。
        需要它，是为了支持小程序常见的拼音搜索习惯。
    include_ngrams:
        是否生成中文 n-gram 子串。
        需要它，是为了支持标题/短词被用户截断输入时仍能命中。
    treat_as_formula:
        是否按公式规则归一化。
        需要它，是为了让 `\\leq`、`<=`、空格差异等公式写法尽量对齐。
    prefix_ratio:
        前缀 posting 相对 exact posting 的分数折扣。
        需要它，是为了让前缀召回能出现，但默认排在精确命中之后。
    """

    name: str
    extractor: Callable[[Mapping[str, object]], list[str]]
    base_weight: int
    searchmeta_key: str | None = None
    include_prefix: bool = False
    include_suggest: bool = False
    include_pinyin: bool = False
    include_ngrams: bool = False
    treat_as_formula: bool = False
    prefix_ratio: float = 0.70


@dataclass
class ModuleStats:
    """记录单个模块的构建统计。

    这些数字存在不是为了“好看”，而是为了快速发现问题，例如：
    - 某模块 scanned 很多但 built 很少，说明元数据可能大量缺失。
    - filtered 很多，说明调试命令的筛选条件可能不对。
    - skipped 很多，说明需要检查 JSON 质量。
    """

    module_name: str
    scanned_items: int = 0
    built_items: int = 0
    filtered_items: int = 0
    skipped_items: int = 0


@dataclass
class PostingAccumulator:
    """内存中的 posting 聚合器。

    倒排在构建过程中会多次命中同一 `(term, doc)`，这里先把分数和字段位图累加，
    最后再序列化成紧凑的数组，减少中间逻辑复杂度。
    """

    score: int = 0
    field_mask: int = 0


def configure_console_encoding() -> None:
    """尽量把控制台输出编码切到 UTF-8。

    需要这个函数，是因为构建和调试日志里大量包含中文、公式和拼音，若控制台
    编码不统一，`--debug-doc` / `--debug-term` 的结果会很难看甚至不可读。
    """

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def configure_logging(debug: bool) -> None:
    """初始化日志格式和级别。"""

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    这个函数只负责“拿到原始 CLI 输入”，不负责校验和解释业务含义；校验和
    转换统一交给 `build_config`，这样职责更清晰。
    """

    parser = argparse.ArgumentParser(
        prog="build_search_bundle_js.py",
        description=(
            "Build a single-file JS search bundle from meta.json files.\n"
            "The generated bundle is optimized for mini-program search, suggestion,\n"
            "and incremental prefix matching."
        ),
        epilog=(
            "Examples:\n"
            "  python scripts/build_search_bundle_js.py\n"
            "  python scripts/build_search_bundle_js.py --module 07_inequality\n"
            "  python scripts/build_search_bundle_js.py --item I005 --debug-doc I005 --dry-run\n"
            "  python scripts/build_search_bundle_js.py --debug-term 柯西不等式 --dry-run"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--base-dir",
        default=str(PROJECT_ROOT),
        help="Project root used for module discovery. Defaults to the repo root beside this script.",
    )
    parser.add_argument(
        "--output-file",
        default=str(DEFAULT_OUTPUT_FILE),
        help="Output JS bundle path. Defaults to data/search_engine/search_bundle.js.",
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        help="Only build the specified module directory. Can be passed multiple times.",
    )
    parser.add_argument(
        "--item",
        dest="items",
        action="append",
        help="Only build the specified item directory name or document id. Can be repeated.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build everything in memory and print stats, but do not write the output file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose logging for scan, filter, and skip decisions.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail fast on invalid JSON, missing meta.json, duplicate ids, and similar data issues.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the output bundle to make manual inspection easier.",
    )
    parser.add_argument(
        "--embed-debug",
        action="store_true",
        help="Embed debug payloads into the generated bundle. Useful for offline inspection, but increases file size.",
    )
    parser.add_argument(
        "--debug-doc",
        dest="debug_docs",
        action="append",
        help="Print the feature expansion report for a document id. Can be repeated.",
    )
    parser.add_argument(
        "--debug-term",
        dest="debug_terms",
        action="append",
        help="Print the exact/prefix posting report for a query term. Can be repeated.",
    )
    parser.add_argument(
        "--prefix-doc-limit",
        type=int,
        default=DEFAULT_PREFIX_DOC_LIMIT,
        help=f"Maximum number of documents stored under one prefix term. Default: {DEFAULT_PREFIX_DOC_LIMIT}.",
    )
    parser.add_argument(
        "--suggestion-limit",
        type=int,
        default=DEFAULT_SUGGESTION_LIMIT,
        help=f"Maximum number of suggestion rows stored in the bundle. Default: {DEFAULT_SUGGESTION_LIMIT}.",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> BuildConfig:
    """把 argparse 结果转换成结构化配置并做基础校验。

    需要这个步骤，是为了把字符串形式的 CLI 参数尽早变成强约束对象，避免主流
    程里到处处理默认值、路径解析和正整数校验。
    """

    if args.prefix_doc_limit <= 0:
        raise BuildError("--prefix-doc-limit must be > 0")
    if args.suggestion_limit <= 0:
        raise BuildError("--suggestion-limit must be > 0")
    return BuildConfig(
        project_root=Path(args.base_dir).resolve(),
        output_file=Path(args.output_file).resolve(),
        target_modules=tuple(args.modules or DEFAULT_TARGET_MODULES),
        target_items=tuple(args.items or ()),
        dry_run=bool(args.dry_run),
        debug=bool(args.debug),
        strict=bool(args.strict),
        pretty=bool(args.pretty),
        embed_debug=bool(args.embed_debug),
        prefix_doc_limit=int(args.prefix_doc_limit),
        suggestion_limit=int(args.suggestion_limit),
        debug_docs=tuple(args.debug_docs or ()),
        debug_terms=tuple(args.debug_terms or ()),
    )


def get_path(data: Mapping[str, object], path: str) -> object | None:
    """按 `a.b.c` 形式读取嵌套字典。

    需要这个函数，是因为 meta 字段分布并不完全统一，用统一路径读取能减少
    大量重复的 `if isinstance(..., Mapping)` 判断。
    """

    current: object = data
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def flatten_strings(value: object) -> list[str]:
    """把字符串、列表、字典中的可读文本递归拍平成字符串列表。

    需要它，是因为内容元数据有时是字符串，有时是对象数组，字段结构不完全稳定。
    统一拍平之后，提取器就能用同一种方式处理多种来源。
    """

    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if isinstance(value, Mapping):
        result: list[str] = []
        for key in ("name", "title", "label", "description", "content", "text"):
            if key in value:
                result.extend(flatten_strings(value[key]))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        result: list[str] = []
        for item in value:
            result.extend(flatten_strings(item))
        return result
    return []


def dedupe(values: Sequence[str]) -> list[str]:
    """按出现顺序去重。

    需要保序去重，而不是直接转 `set`，因为前面的值通常更接近人工配置的主表达，
    后续构建摘要和建议词时保留这个顺序更符合直觉。
    """

    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result

def get_strings(data: Mapping[str, object], *paths: str) -> list[str]:
    """从多个候选路径读取文本并做递归拍平与去重。

    需要它，是因为同一业务字段经常同时兼容旧路径和新路径，例如
    `search.query_templates` 与 `search.queryTemplates`。
    """

    result: list[str] = []
    for path in paths:
        result.extend(flatten_strings(get_path(data, path)))
    return dedupe(result)


def read_json_file(path: Path, strict: bool) -> dict[str, object]:
    """读取并校验 `meta.json`。

    返回空字典表示“这条内容应被跳过”。之所以不总是抛错，是为了让脚本在全量
    构建时对局部坏数据更有韧性；而 `strict=True` 时再切换到强失败模式。
    """

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as exc:
        if strict:
            raise BuildError(f"Failed to read JSON: {path}") from exc
        LOGGER.warning("Failed to read JSON: %s", path)
        return {}
    if not isinstance(data, dict):
        if strict:
            raise BuildError(f"JSON root must be an object: {path}")
        LOGGER.warning("JSON root is not an object: %s", path)
        return {}
    return data


def normalize_display(text: str) -> str:
    """做面向展示的轻量归一化。

    这个版本保留空格分隔，只统一 Unicode 形态和连续空白，适合用于 suggestion
    展示文本、debug 输出和 doc 摘要。
    """

    return WHITESPACE_RE.sub(" ", unicodedata.normalize("NFKC", text)).strip()


def normalize_text(text: str) -> str:
    """做通用搜索归一化。

    在 `normalize_display` 基础上转小写，并统一常见中英文引号。需要这个函数，
    是为了减少看起来不同、实际语义相同的输入造成的索引碎片。
    """

    text = normalize_display(text).lower()
    return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")


def normalize_compact(text: str) -> str:
    """移除所有空白，生成更紧凑的匹配形式。

    需要它，是因为很多用户输入会忽略空格，例如 `a+b`、`均值不等式`、拼音连写。
    """

    return WHITESPACE_RE.sub("", text)


def normalize_formula(text: str) -> str:
    """按公式搜索场景归一化文本。

    需要它，是为了把 LaTeX 写法、空格差异和部分符号变体映射到更稳定的统一形式，
    让 `\\leq`、`<=`、`\\cdot`、`*` 更容易命中同一条内容。
    """

    text = normalize_text(text)
    for old, new in FORMULA_REPLACEMENTS:
        text = text.replace(old, new)
    return text.replace(" ", "")


def split_fragments(text: str, max_fragments: int = 8, max_length: int = 28) -> list[str]:
    """把长句拆成适合索引的短片段。

    需要它，是因为定理陈述和说明文字通常很长，整句建索引噪声太高；拆成短片段后，
    可以保留局部关键词，同时避免把整段自然语言直接塞进前缀索引。
    """

    text = normalize_display(text)
    parts = [part.strip() for part in FRAGMENT_SPLIT_RE.split(text)]
    parts = [part for part in parts if 2 <= len(part) <= max_length]
    return parts[:max_fragments]


def contains_cjk(text: str) -> bool:
    """判断文本中是否包含中日韩统一表意文字。"""

    return bool(CJK_RE.search(text))


def to_pinyin(text: str) -> str:
    """把中文部分转成全拼。

    需要它，是为了支持用户输入 `keshi` 这类拼音检索。如果环境没有安装
    `pypinyin`，这里会安全返回空字符串。
    """

    if lazy_pinyin is None:
        return ""
    raw = "".join(CJK_RE.findall(text))
    return "".join(lazy_pinyin(raw)) if raw else ""


def to_pinyin_abbr(text: str) -> str:
    """把中文部分转成拼音首字母缩写。

    需要它，是为了支持 `ksbdds` 这类更激进的缩写输入。
    """

    if lazy_pinyin is None:
        return ""
    raw = "".join(CJK_RE.findall(text))
    if not raw:
        return ""
    return "".join(item[0] for item in lazy_pinyin(raw) if item)


def word_tokens(text: str) -> list[str]:
    """从文本里抽取较稳定的中文片段和拉丁 token。

    需要它，是为了把完整标题进一步拆成更可复用的召回单元，例如：
    - `柯西不等式` 可以独立命中
    - `am-gm` / `a_n` / `x2` 这类拉丁式 token 也能参与搜索
    """

    tokens: list[str] = []
    for segment in CJK_RE.findall(text):
        if 2 <= len(segment) <= 24:
            tokens.append(segment)
    for token in LATIN_TOKEN_RE.findall(text):
        token = token.strip("._/+\\-")
        if token and (len(token) >= 2 or any(ch.isdigit() for ch in token)):
            tokens.append(token)
    return dedupe(tokens)


def cjk_ngrams(text: str, min_n: int = 2, max_n: int = 6) -> list[str]:
    """为短中文串生成 n-gram 子串。

    需要它，是因为用户常常只记得标题的一部分。对标题、标签、知识点等短文本生成
    n-gram 能显著提升“半截输入”命中的概率，但不适合对所有长文本都开启。
    """

    result: list[str] = []
    for segment in CJK_RE.findall(text):
        if len(segment) < min_n or len(segment) > 18:
            continue
        for size in range(min_n, min(max_n, len(segment)) + 1):
            for start in range(0, len(segment) - size + 1):
                result.append(segment[start:start + size])
    return dedupe(result)


def is_formula_like(text: str) -> bool:
    """粗略判断一段文本是否更像公式而不是自然语言。"""

    return any(ch in text for ch in "^=<>/*()[]{}\\")


def informative_exact(term: str) -> bool:
    """判断一个词是否值得进入精确倒排。

    需要这个过滤，是为了剔除只有符号、过短且无信息量的项，避免索引膨胀和误召回。
    """

    bad = {"+", "-", "*", "/", "=", "<", ">", "<=", ">=", "!="}
    return bool(term and term not in bad and (len(term) > 1 or contains_cjk(term) or is_formula_like(term)))


def informative_prefix(term: str) -> bool:
    """判断一个词是否值得生成前缀。

    前缀索引比精确索引更容易膨胀，所以这里比 `informative_exact` 更保守。
    """

    return informative_exact(term) and not (len(term) == 1 and not contains_cjk(term))


def prefix_terms(term: str) -> list[str]:
    """生成一个词可用于前缀倒排的前缀集合。

    中文允许从 1 个字开始前缀命中，因为单字前缀在标题搜索里常见；英文和拼音从
    2 个字符起步，以减少噪声。上限存在是为了控制 bundle 体积。
    """

    if not informative_prefix(term):
        return []
    min_len = 1 if contains_cjk(term) else 2
    max_len = min(len(term), 12 if contains_cjk(term) else 16)
    return [term[:i] for i in range(min_len, max_len + 1)]


def extract_title(meta: Mapping[str, object]) -> list[str]:
    """提取标题字段。

    标题通常是搜索最强信号，因此会赋予最高权重，并参与前缀、建议词、拼音和 n-gram。
    """

    return get_strings(meta, "core.title", "title")


def extract_alias(meta: Mapping[str, object]) -> list[str]:
    """提取别名。

    需要它，是因为很多知识点存在教材叫法、竞赛叫法、课堂叫法不一致的问题。
    """

    return get_strings(meta, "core.alias", "alias")


def extract_keyword(meta: Mapping[str, object]) -> list[str]:
    """提取关键词。

    关键词通常是人工整理后的高价值召回入口，因此权重仅次于标题和别名。
    """

    return get_strings(meta, "search.keywords", "keywords")


def extract_synonym(meta: Mapping[str, object]) -> list[str]:
    """提取同义词或近义表达。"""

    return get_strings(meta, "search.synonyms", "synonyms")


def extract_intent(meta: Mapping[str, object]) -> list[str]:
    """提取搜索意图短语。

    例如“证明均值不等式”“求最值”这类表达，适合做召回，但通常不适合直接做展示联想。
    """

    return get_strings(meta, "search.intents")


def extract_query(meta: Mapping[str, object]) -> list[str]:
    """提取更接近用户原始搜索句式的模板。

    这个字段存在是为了服务自然语言查询，但因为噪声可能更高，默认不开 suggestion。
    """

    return get_strings(meta, "search.query_templates", "search.queryTemplates")


def extract_ocr(meta: Mapping[str, object]) -> list[str]:
    """提取 OCR 关键词。

    需要它，是为了让拍照识别、截图识别后得到的碎片化文本也能召回对应内容。
    """

    return get_strings(meta, "search.ocrKeywords", "ocrKeywords")


def extract_category(meta: Mapping[str, object]) -> list[str]:
    """提取分类名。

    分类不是最强信号，但它有助于用户输入“均值不等式”“代数不等式”这种类目词时
    快速召回相关条目。
    """

    return get_strings(meta, "core.category", "category", "chapter", "section")


def extract_tag(meta: Mapping[str, object]) -> list[str]:
    """提取标签。标签通常较短，适合做前缀和建议词。"""

    return get_strings(meta, "core.tags", "tags")


def extract_formula_token(meta: Mapping[str, object]) -> list[str]:
    """提取公式关键 token。

    它和完整公式的区别在于：这里偏向人工挑选的“最值得搜的符号串”，适合提升公式搜索精度。
    """

    return get_strings(meta, "search.formulaTokens", "search.formula_tokens", "formulaTokens")


def extract_formula(meta: Mapping[str, object]) -> list[str]:
    """提取完整或半完整公式表达。"""

    return get_strings(meta, "search.latex_patterns", "search.latexPatterns", "math.core_formula", "math.related_formulas", "formulas")


def extract_summary(meta: Mapping[str, object]) -> list[str]:
    """提取摘要或直觉说明。

    这个字段主要用于补充召回覆盖率和生成 doc 摘要，不宜赋予过高权重。
    """

    return get_strings(meta, "core.summary", "summary", "preview", "content.intuition")


def extract_statement(meta: Mapping[str, object]) -> list[str]:
    """提取陈述文本中的短片段。

    定理全文通常过长，这里先切成片段再建索引，目的是让关键短句可命中，同时控制噪声。
    """

    result: list[str] = []
    for text in get_strings(meta, "content.statement", "statement"):
        result.extend(split_fragments(text))
    return dedupe(result)


def extract_usage(meta: Mapping[str, object]) -> list[str]:
    """提取适用题型和使用场景。

    用户很多时候搜的是“什么时候用”，不是“它叫什么”，所以这个字段很有价值。
    """

    return get_strings(meta, "usage.problem_types", "usage.scenarios")


def extract_node(meta: Mapping[str, object]) -> list[str]:
    """提取知识节点及其备用节点名。

    需要这个字段，是为了把知识图谱、目录体系里的节点命名也纳入搜索入口。
    """

    result = get_strings(meta, "knowledgeNode")
    for text in get_strings(meta, "altNodes"):
        result.extend([part.strip() for part in ALT_NODE_SPLIT_RE.split(text) if part.strip()])
    return dedupe(result)


def extract_pinyin_field(meta: Mapping[str, object]) -> list[str]:
    """提取人工维护的全拼字段。

    优先保留内容侧手工提供的拼音，因为它比自动转换更可控，也能覆盖专有名词。
    """

    return get_strings(meta, "search.pinyin", "pinyin")


def extract_pinyin_abbr_field(meta: Mapping[str, object]) -> list[str]:
    """提取人工维护的拼音首字母字段。"""

    return get_strings(meta, "search.pinyinAbbr", "search.pinyin_abbr", "pinyinAbbr")


# `FIELD_SPECS` 是搜索索引的“配置中心”。
# 每一项回答 4 个问题：
# 1. 数据从哪里来？
# 2. 这类数据有多重要？
# 3. 是否应该支持前缀、联想、拼音、n-gram？
# 4. 是否需要按公式规则做归一化？
FIELD_SPECS = (
    # 标题：最重要的主召回字段。
    # 需要 suggestion，是因为标题通常最适合直接展示给用户。
    FieldSpec("title", extract_title, 120, "titleWeight", True, True, True, True),
    # 别名：解决同一知识点多种叫法的问题。
    FieldSpec("alias", extract_alias, 96, None, True, True, True, True),
    # 关键词：人工整理的高价值检索入口。
    FieldSpec("keyword", extract_keyword, 84, "keywordWeight", True, True, True, True),
    # 同义词：覆盖不同表述，但比标题和关键词稍弱。
    FieldSpec("synonym", extract_synonym, 68, "synonymWeight", True, True, True, True),
    # 搜索意图：服务“我想解决什么问题”的搜索方式。
    FieldSpec("intent", extract_intent, 56, None, True, False, True, False),
    # 查询模板：更像自然语言句子，适合召回，不适合联想展示。
    FieldSpec("query_template", extract_query, 38, None, False, False, True, False),
    # OCR 关键词：主要用于图片识别、截图识别后的碎片文本。
    FieldSpec("ocr_keyword", extract_ocr, 42, "ocrWeight", True, False, True, False),
    # 分类名：帮助按章节、知识类目检索。
    FieldSpec("category", extract_category, 48, None, True, True, True, True),
    # 标签：短而稳，适合做补充召回和建议词。
    FieldSpec("tag", extract_tag, 44, None, True, True, True, True),
    # 公式 token：人工挑选过的关键符号表达，精度高于完整公式。
    FieldSpec("formula_token", extract_formula_token, 78, "formulaWeight", True, False, False, False, True),
    # 完整公式：扩大公式检索覆盖面，但展示价值一般，不做 suggestion。
    FieldSpec("formula", extract_formula, 66, "formulaWeight", True, False, False, False, True),
    # 摘要：补充召回覆盖率，同时也会写入 docs 作为结果摘要。
    FieldSpec("summary", extract_summary, 30, None, False, False, True, False),
    # 陈述片段：让用户输入定理中的局部短句时仍可命中。
    FieldSpec("statement_fragment", extract_statement, 18, None, False, False, False, False),
    # 使用场景：服务“解某类题该用什么”这一类意图搜索。
    FieldSpec("usage", extract_usage, 28, None, True, False, True, False),
    # 知识节点：兼容知识图谱、目录系统中的节点命名。
    FieldSpec("knowledge_node", extract_node, 40, None, True, False, True, True),
    # 手工全拼：优先级高于自动拼音派生，因为可控性更强。
    FieldSpec("pinyin", extract_pinyin_field, 72, None, True, False, False, False),
    # 手工拼音缩写：服务首字母搜索。
    FieldSpec("pinyin_abbr", extract_pinyin_abbr_field, 64, None, True, False, False, False),
)
# posting 里只存一个整数位图，而不重复存字段字符串。
# 需要这个映射，是因为它在体积和可调试性之间做了比较好的平衡。
FIELD_MASK_LEGEND = {spec.name: 1 << index for index, spec in enumerate(FIELD_SPECS)}

def searchmeta_dict(meta: Mapping[str, object]) -> Mapping[str, object]:
    """提取 `searchmeta/searchMeta` 配置块。

    历史数据可能大小写不一致，这里统一兜底，避免上层逻辑重复兼容。
    """

    value = get_path(meta, "searchmeta")
    if isinstance(value, Mapping):
        return value
    value = get_path(meta, "searchMeta")
    return value if isinstance(value, Mapping) else {}


def to_float(value: object, default: float = 0.0) -> float:
    """尽量把任意值转换成 float，失败则回退默认值。

    需要它，是因为元数据来源复杂，数值可能是字符串、整数、浮点数，甚至为空。
    """

    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_field_weight(meta: Mapping[str, object], spec: FieldSpec) -> int:
    """计算某个字段在当前文档上的最终权重。

    基础权重来自 `FieldSpec.base_weight`，若内容侧在 `searchmeta` 中配置了动态权重，
    则按默认权重比例进行缩放。这样可以做到“字段级规则稳定、内容级微调灵活”。
    """

    if not spec.searchmeta_key:
        return spec.base_weight
    raw = searchmeta_dict(meta).get(spec.searchmeta_key)
    if raw is None:
        return spec.base_weight
    configured = to_float(raw, float(DEFAULT_SEARCHMETA_WEIGHTS[spec.searchmeta_key]))
    base = float(DEFAULT_SEARCHMETA_WEIGHTS[spec.searchmeta_key])
    return max(1, int(round(spec.base_weight * (configured / base))))


def compute_rank_score(meta: Mapping[str, object]) -> int:
    """计算文档的静态排序分。

    这个分数不参与召回，只在多个候选都命中时作为排序加权使用。之所以单独保留
    一个 `rank` 字段，是为了把“能不能召回”和“排在前还是后”拆开处理。
    """

    ranking = get_path(meta, "ranking") if isinstance(get_path(meta, "ranking"), Mapping) else {}
    usage = get_path(meta, "usage") if isinstance(get_path(meta, "usage"), Mapping) else {}
    core = get_path(meta, "core") if isinstance(get_path(meta, "core"), Mapping) else {}
    score = (
        to_float(ranking.get("search_boost", ranking.get("searchBoost")), 0.0) * 100
        + to_float(ranking.get("hot_score", ranking.get("hotScore")), 0.0)
        + to_float(ranking.get("click_rate", ranking.get("clickRate")), 0.0) * 30
        + to_float(ranking.get("success_rate", ranking.get("successRate")), 0.0) * 40
        + to_float(usage.get("exam_frequency", usage.get("examFrequency")), to_float(meta.get("examFrequency"), 0.0)) * 20
        + to_float(usage.get("exam_score", usage.get("examScore")), to_float(meta.get("examScore"), 0.0)) * 5
        + to_float(core.get("difficulty", meta.get("difficulty")), 0.0) * 2
    )
    return int(round(score))


def module_contains_content(module_dir: Path) -> bool:
    """判断某目录是否像一个内容模块。

    需要这个预判，是为了在自动发现模块时跳过脚本目录、资源目录等无关路径。
    """

    try:
        children = list(module_dir.iterdir())
    except OSError:
        return False
    for child in children:
        if child.is_dir() and (child / META_FILENAME).exists():
            return True
    return False


def discover_module_dirs(project_root: Path) -> list[Path]:
    """自动发现项目下所有可构建的模块目录。"""

    result: list[Path] = []
    for path in sorted(project_root.iterdir()):
        if not path.is_dir() or path.name in IGNORED_TOP_LEVEL_DIRS:
            continue
        if module_contains_content(path):
            result.append(path)
    return result


def resolve_module_dirs(config: BuildConfig) -> list[Path]:
    """根据配置解析最终需要构建的模块目录列表。

    未显式传 `--module` 时走自动发现；显式指定时按名称查找并对缺失模块给出提示。
    """

    if not config.target_modules:
        return discover_module_dirs(config.project_root)
    result: list[Path] = []
    missing: list[str] = []
    for module_name in config.target_modules:
        path = config.project_root / module_name
        if path.is_dir():
            result.append(path)
        else:
            missing.append(module_name)
    if missing:
        message = "Module directory not found: " + ", ".join(missing)
        if config.strict:
            raise BuildError(message)
        LOGGER.warning(message)
    return result


def resolve_item_identity(meta: Mapping[str, object], item_dir: Path) -> tuple[str, str]:
    """解析文档 id 和标题。

    需要这个函数，是为了把“文档身份”提取逻辑集中起来，避免后续多处重复 fallback。
    """

    doc_id = (get_strings(meta, "id") or [item_dir.name])[0]
    title = (extract_title(meta) or [item_dir.name])[0]
    return doc_id, title


def matches_item_filter(item_dir: Path, doc_id: str, target_items: Sequence[str]) -> bool:
    """判断某条内容是否满足 `--item` 过滤条件。"""

    if not target_items:
        return True
    targets = set(target_items)
    return item_dir.name in targets or doc_id in targets


def build_doc_record(meta: Mapping[str, object], doc_id: str, module_dir_name: str, source_path: Path) -> dict[str, object]:
    """构建写入 `docs` 的轻量文档记录。

    `docs` 不是原始 meta 的镜像，而是端上搜索结果真正需要的最小展示/排序信息。
    各字段存在的原因如下：

    `id`
        文档主键。倒排最终都回指到它。
    `module`
        业务上的模块名，方便端上做分组或跳转。
    `moduleDir`
        真实目录名。保留它，是为了构建结果与文件系统更容易互相定位。
    `title`
        搜索结果的主展示文本。
    `summary`
        搜索结果副文案。没有摘要时退回陈述片段，避免结果卡片过空。
    `category`
        结果补充信息，也可用于端上筛选标签。
    `tags`
        结果卡片的附加标签，限制数量是为了控制包体。
    `coreFormula`
        便于公式类内容在结果页直接展示核心表达式。
    `rank`
        静态排序分，避免每次查询都重新计算。
    `difficulty` / `searchBoost` / `hotScore` / `examFrequency` / `examScore`
        这些值既能帮助调试排序，也为未来端上二次排序预留空间。
    """

    ranking = get_path(meta, "ranking") if isinstance(get_path(meta, "ranking"), Mapping) else {}
    usage = get_path(meta, "usage") if isinstance(get_path(meta, "usage"), Mapping) else {}
    core = get_path(meta, "core") if isinstance(get_path(meta, "core"), Mapping) else {}
    summary_candidates = extract_summary(meta) or extract_statement(meta)
    formula_candidates = extract_formula(meta)
    return {
        # 文档主键，倒排 posting 最终只回指到这个 id。
        "id": doc_id,
        # 业务模块名，优先使用 meta 中显式声明的 module。
        "module": str(meta.get("module") or module_dir_name),
        # 保留目录名是为了日志、调试和文件系统定位更直接。
        "moduleDir": module_dir_name,
        # 标题是端上搜索结果的主展示字段。
        "title": (extract_title(meta) or [source_path.parent.name])[0],
        # 摘要优先用人工摘要，没有再回退到陈述片段。
        "summary": summary_candidates[0] if summary_candidates else "",
        # 分类有助于端上展示和分组。
        "category": (extract_category(meta) or [""])[0],
        # 标签控制在 8 个以内，避免 doc 记录无限膨胀。
        "tags": extract_tag(meta)[:8],
        # 公式类内容保留一个核心公式，便于结果页快速识别。
        "coreFormula": formula_candidates[0] if formula_candidates else "",
        # 预先计算静态排序分，端上不用重复做同样的聚合。
        "rank": compute_rank_score(meta),
        "difficulty": to_float(core.get("difficulty", meta.get("difficulty")), 0.0),
        "searchBoost": to_float(ranking.get("search_boost", ranking.get("searchBoost")), 0.0),
        "hotScore": to_float(ranking.get("hot_score", ranking.get("hotScore")), 0.0),
        "examFrequency": to_float(usage.get("exam_frequency", usage.get("examFrequency")), to_float(meta.get("examFrequency"), 0.0)),
        "examScore": to_float(usage.get("exam_score", usage.get("examScore")), to_float(meta.get("examScore"), 0.0)),
    }


def build_feature_variants(text: str, spec: FieldSpec) -> dict[str, object]:
    """把一段原始字段文本展开成可索引特征。

    返回结构中的字段含义如下：

    `source`
        原始展示文本，主要用于 debug 和 suggestion。
    `exact`
        精确倒排项列表，每项是 `(term, score_multiplier, kind)`。
        需要它，是因为同一个字段会派生出原词、紧凑词、token、拼音等多种召回入口。
    `prefix`
        前缀候选列表，结构同 `exact`。
        需要它，是因为端上输入通常是增量式的。
    `suggest`
        可直接展示给用户的联想文本。
        需要它，是因为不是每个可召回项都适合拿来展示。
    """

    display_text = normalize_display(text)
    if not display_text:
        return {"source": "", "exact": [], "prefix": [], "suggest": []}
    base = normalize_formula(display_text) if spec.treat_as_formula else normalize_text(display_text)
    exact: list[tuple[str, float, str]] = []
    prefix: list[tuple[str, float, str]] = []
    seen_exact: set[str] = set()
    seen_prefix: set[str] = set()

    def add_exact(term: str, mult: float, kind: str) -> None:
        if informative_exact(term) and term not in seen_exact:
            seen_exact.add(term)
            exact.append((term, mult, kind))

    def add_prefix(term: str, mult: float, kind: str) -> None:
        if informative_prefix(term) and term not in seen_prefix:
            seen_prefix.add(term)
            prefix.append((term, mult, kind))

    add_exact(base, 1.0, "full")
    if spec.include_prefix:
        add_prefix(base, 1.0, "full")

    compact = normalize_compact(base)
    if compact and compact != base:
        add_exact(compact, 0.96, "compact")
        if spec.include_prefix:
            add_prefix(compact, 0.96, "compact")

    for token in word_tokens(base):
        add_exact(token, 0.72, "token")
        if spec.include_prefix:
            add_prefix(token, 0.72, "token")

    if spec.include_ngrams:
        for token in cjk_ngrams(base):
            add_exact(token, 0.58, "ngram")

    if spec.include_pinyin and contains_cjk(display_text):
        py = normalize_compact(to_pinyin(display_text))
        abbr = normalize_compact(to_pinyin_abbr(display_text))
        if py:
            add_exact(py, 0.72, "pinyin")
            if spec.include_prefix:
                add_prefix(py, 0.72, "pinyin")
        if abbr and abbr != py:
            add_exact(abbr, 0.62, "pinyin_abbr")
            if spec.include_prefix:
                add_prefix(abbr, 0.62, "pinyin_abbr")

    suggest = [display_text] if spec.include_suggest and 2 <= len(display_text) <= 32 and not is_formula_like(display_text) else []
    return {"source": display_text, "exact": exact, "prefix": prefix, "suggest": suggest}


def add_exact_posting(index_map: DefaultDict[str, dict[str, PostingAccumulator]], term: str, doc_id: str, score: int, field_mask: int) -> None:
    """把一条 exact 倒排命中累加到内存索引中。

    exact posting 采用“分数累加”策略，因为同一文档同一词可能从多个字段重复命中，
    这通常意味着相关性更强。
    """

    doc_map = index_map[term]
    posting = doc_map.get(doc_id)
    if posting is None:
        doc_map[doc_id] = PostingAccumulator(score=score, field_mask=field_mask)
        return
    posting.score += score
    posting.field_mask |= field_mask


def add_prefix_posting(index_map: DefaultDict[str, dict[str, PostingAccumulator]], term: str, doc_id: str, score: int, field_mask: int) -> None:
    """把一条 prefix 倒排命中展开并写入内存索引。

    prefix posting 采用“同词取最大分”而不是累加，目的是抑制前缀索引过度放大带来的噪声。
    """

    for prefix in prefix_terms(term):
        doc_map = index_map[prefix]
        posting = doc_map.get(doc_id)
        if posting is None:
            doc_map[doc_id] = PostingAccumulator(score=score, field_mask=field_mask)
            continue
        posting.score = max(posting.score, score)
        posting.field_mask |= field_mask


def serialize_postings(postings: dict[str, PostingAccumulator], docs: Mapping[str, Mapping[str, object]], limit: int | None = None) -> list[list[int | str]]:
    """把 posting 映射压缩成最终写入 JS 的数组结构。

    输出格式为 `[docId, score, fieldMask]`。之所以不用对象，是为了显著减小产物体积。
    排序时先看 posting 分，再看文档静态 `rank`，最后按 docId 稳定排序。
    """

    items = sorted(
        postings.items(),
        key=lambda item: (-item[1].score, -int(docs.get(item[0], {}).get("rank", 0)), item[0]),
    )
    if limit is not None:
        items = items[:limit]
    return [[doc_id, acc.score, acc.field_mask] for doc_id, acc in items]


def build_debug_term_candidates(raw_term: str) -> list[str]:
    """为 `--debug-term` 生成应该检查的标准化候选词。

    一个用户输入在索引侧可能对应普通归一化、去空格归一化和公式归一化三种形式，
    这里统一生成出来，方便一次看全。
    """

    display = normalize_display(raw_term)
    return dedupe([
        candidate
        for candidate in (normalize_text(display), normalize_compact(normalize_text(display)), normalize_formula(display))
        if candidate
    ])

def write_bundle(bundle: Mapping[str, object], config: BuildConfig) -> None:
    """把 bundle 写成 JS 模块文件。

    这里保留了一个简短文件头，原因有两个：
    1. 让打开产物的人第一眼就知道来源和统计信息。
    2. 让 bundle 即使脱离构建日志，也能自解释。
    """

    config.output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        bundle,
        ensure_ascii=False,
        indent=2 if config.pretty else None,
        separators=None if config.pretty else (",", ":"),
    )
    header = [
        "// Auto-generated by scripts/build_search_bundle_js.py",
        "// Single-file search bundle for mini-program search.",
        "// DO NOT EDIT DIRECTLY.",
        f"// Generated at: {bundle['generatedAt']}",
        (
            "// Stats: "
            f"docs={bundle['stats']['documents']}, "
            f"terms={bundle['stats']['terms']}, "
            f"prefixes={bundle['stats']['prefixes']}, "
            f"suggestions={bundle['stats']['suggestions']}"
        ),
        "//",
        "// Bundle schema (v1):",
        "// - docs: { [docId: string]: DocRecord }",
        "// - termIndex: { [term: string]: Posting[] }",
        "// - prefixIndex: { [prefix: string]: Posting[] } (per key limited by buildOptions.prefixDocLimit)",
        "// - suggestions: SuggestionRow[] (limited by buildOptions.suggestionLimit)",
        "// - fieldMaskLegend: { [fieldName: string]: number }",
        "// - term/prefix keys are normalized at build time (NFKC, lower-case; formula variants apply LaTeX replacements and remove spaces)",
        "//",
        "// Posting = [docId: string, score: number, fieldMask: number]",
        "// - score: relevance score aggregated at build time",
        "// - fieldMask: bitmask of contributing fields (decode via fieldMaskLegend)",
        "// - postings are sorted by score desc, then docs[docId].rank desc",
        "//",
        "// SuggestionRow = [displayText: string, docId: string, score: number]",
        "// - suggestion score mixes field weight and docs[docId].rank (higher first)",
        "",
    ]
    content = "\n".join(header) + "const searchBundle = " + payload + "\n\nmodule.exports = searchBundle;\n"
    config.output_file.write_text(content, encoding="utf-8")
    LOGGER.info("Search bundle written: %s", config.output_file)


def run_build(config: BuildConfig) -> dict[str, object]:
    """执行完整构建流程并返回 bundle 对象。

    这是脚本的主工作函数，负责：
    1. 解析模块范围。
    2. 读取每个 `meta.json`。
    3. 生成 `docs / termIndex / prefixIndex / suggestions`。
    4. 输出调试报告。
    5. 视配置决定落盘还是 dry-run。
    """

    if lazy_pinyin is None:
        LOGGER.warning("Dependency status | pypinyin is not installed, so dynamic pinyin expansion will be skipped.")
    else:
        LOGGER.info("Dependency status | pypinyin is available, dynamic pinyin expansion is enabled.")

    LOGGER.info("Step 1/5 | Resolve build scope")
    module_dirs = resolve_module_dirs(config)
    if not module_dirs:
        message = "No module directories matched the current configuration."
        if config.strict:
            raise BuildError(message)
        LOGGER.warning(message)
        return {}

    docs: dict[str, dict[str, object]] = {}
    term_index: DefaultDict[str, dict[str, PostingAccumulator]] = defaultdict(dict)
    prefix_index: DefaultDict[str, dict[str, PostingAccumulator]] = defaultdict(dict)
    suggestions: dict[str, dict[str, object]] = {}
    debug_docs: dict[str, dict[str, object]] = {}
    module_stats: list[ModuleStats] = []

    LOGGER.info("Build target | project_root=%s", config.project_root)
    LOGGER.info("Build target | output_file=%s", config.output_file)
    LOGGER.info("Build target | target_modules=%s", ", ".join(config.target_modules) if config.target_modules else "auto discover")
    if config.target_items:
        LOGGER.info("Build target | target_items=%s", ", ".join(config.target_items))
    LOGGER.info("Step 1/5 done | matched_modules=%d | modules=%s", len(module_dirs), ", ".join(path.name for path in module_dirs))

    LOGGER.info("Step 2/5 | Scan modules and collect searchable records")
    for module_dir in module_dirs:
        stats = ModuleStats(module_name=module_dir.name)
        item_dirs = sorted(path for path in module_dir.iterdir() if path.is_dir())
        LOGGER.info("Module start | module=%s | candidate_items=%d", module_dir.name, len(item_dirs))

        for item_dir in item_dirs:
            stats.scanned_items += 1
            meta_path = item_dir / META_FILENAME
            if not meta_path.exists():
                stats.skipped_items += 1
                if config.strict:
                    raise BuildError(f"Missing meta.json: {meta_path}")
                LOGGER.warning("Item skipped | reason=missing_meta | item_dir=%s", item_dir)
                continue

            try:
                meta = read_json_file(meta_path, config.strict)
                if not meta:
                    stats.skipped_items += 1
                    LOGGER.warning("Item skipped | reason=invalid_or_empty_json | meta_path=%s", meta_path)
                    continue

                doc_id, _ = resolve_item_identity(meta, item_dir)
                if not matches_item_filter(item_dir, doc_id, config.target_items):
                    stats.filtered_items += 1
                    LOGGER.debug("Item filtered | module=%s | item=%s | doc_id=%s", module_dir.name, item_dir.name, doc_id)
                    continue
                if doc_id in docs:
                    raise BuildError(f"Duplicate document id detected: {doc_id}")

                doc_record = build_doc_record(meta, doc_id, module_dir.name, meta_path)
                docs[doc_id] = doc_record
                capture_debug = config.embed_debug or doc_id in set(config.debug_docs)
                if capture_debug:
                    debug_docs[doc_id] = {"source": str(meta_path), "record": doc_record, "features": []}

                field_feature_count = 0
                exact_term_count = 0
                prefix_term_count = 0
                suggestion_count = 0

                for spec in FIELD_SPECS:
                    field_mask = FIELD_MASK_LEGEND[spec.name]
                    field_weight = compute_field_weight(meta, spec)
                    for raw in dedupe(spec.extractor(meta)):
                        feature = build_feature_variants(raw, spec)
                        if not feature["source"]:
                            continue
                        if capture_debug:
                            debug_docs[doc_id]["features"].append(
                                {
                                    "field": spec.name,
                                    "sourceText": feature["source"],
                                    "weight": field_weight,
                                    "exact": [{"term": term, "kind": kind, "score": max(1, int(round(field_weight * mult)))} for term, mult, kind in feature["exact"]],
                                    "prefix": [{"term": term, "kind": kind, "score": max(1, int(round(field_weight * spec.prefix_ratio * mult)))} for term, mult, kind in feature["prefix"]],
                                    "suggest": feature["suggest"],
                                }
                            )
                        field_feature_count += 1
                        exact_term_count += len(feature["exact"])
                        prefix_term_count += len(feature["prefix"])
                        suggestion_count += len(feature["suggest"])
                        for term, mult, _kind in feature["exact"]:
                            add_exact_posting(term_index, term, doc_id, max(1, int(round(field_weight * mult))), field_mask)
                        for term, mult, _kind in feature["prefix"]:
                            add_prefix_posting(prefix_index, term, doc_id, max(1, int(round(field_weight * spec.prefix_ratio * mult))), field_mask)
                        for display_text in feature["suggest"]:
                            key = normalize_text(display_text)
                            score = field_weight + int(doc_record["rank"])
                            current = suggestions.get(key)
                            if current is None or score > current["score"]:
                                suggestions[key] = {"display": display_text, "docId": doc_id, "score": score}

                stats.built_items += 1
                LOGGER.debug(
                    "Item built | module=%s | item=%s | doc_id=%s | fields=%d | exact_terms=%d | prefix_terms=%d | suggestions=%d | rank=%d",
                    module_dir.name,
                    item_dir.name,
                    doc_id,
                    field_feature_count,
                    exact_term_count,
                    prefix_term_count,
                    suggestion_count,
                    int(doc_record["rank"]),
                )
            except Exception as exc:
                stats.skipped_items += 1
                if config.strict:
                    raise
                LOGGER.warning("Item skipped | module=%s | item=%s | reason=%s", module_dir.name, item_dir.name, exc)

        module_stats.append(stats)
        LOGGER.info(
            "Module done | module=%s | scanned=%d | built=%d | filtered=%d | skipped=%d",
            stats.module_name,
            stats.scanned_items,
            stats.built_items,
            stats.filtered_items,
            stats.skipped_items,
        )

    LOGGER.info(
        "Step 2/5 done | documents=%d | term_keys=%d | prefix_keys=%d | suggestion_candidates=%d",
        len(docs),
        len(term_index),
        len(prefix_index),
        len(suggestions),
    )
    LOGGER.info("Step 3/5 | Assemble bundle payload")
    bundle: dict[str, object] = {
        # 结构版本。端上如果以后需要兼容旧 bundle，可以先检查它。
        "version": 1,
        # 生成时间，方便确认是否使用了最新产物。
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "stats": {
            "documents": len(docs),
            "terms": len(term_index),
            "prefixes": len(prefix_index),
            "suggestions": min(len(suggestions), config.suggestion_limit),
            "modules": len(module_dirs),
            "moduleStats": [
                {
                    "module": item.module_name,
                    "scanned": item.scanned_items,
                    "built": item.built_items,
                    "filtered": item.filtered_items,
                    "skipped": item.skipped_items,
                }
                for item in module_stats
            ],
        },
        "buildOptions": {
            "prefixDocLimit": config.prefix_doc_limit,
            "suggestionLimit": config.suggestion_limit,
            "targetModules": list(config.target_modules),
            "targetItems": list(config.target_items),
        },
        # 记录每个字段对应的 bit 位。posting 里只存整数，更省空间。
        "fieldMaskLegend": FIELD_MASK_LEGEND,
        # 文档主表：倒排只存 docId，真实展示信息在这里补齐。
        "docs": {doc_id: docs[doc_id] for doc_id in sorted(docs)},
        # 精确倒排：高精度召回主入口。
        "termIndex": {term: serialize_postings(postings, docs) for term, postings in sorted(term_index.items())},
        # 前缀倒排：服务增量输入和半截输入。
        "prefixIndex": {term: serialize_postings(postings, docs, config.prefix_doc_limit) for term, postings in sorted(prefix_index.items())},
        # 联想建议，结构为 [display, docId, score]。
        "suggestions": [
            [item["display"], item["docId"], item["score"]]
            for item in sorted(suggestions.values(), key=lambda item: (-item["score"], item["display"], item["docId"]))[: config.suggestion_limit]
        ],
    }
    if config.embed_debug:
        bundle["debug"] = {"docs": debug_docs}
    LOGGER.info(
        "Step 3/5 done | bundle_stats docs=%d terms=%d prefixes=%d suggestions=%d",
        bundle["stats"]["documents"],
        bundle["stats"]["terms"],
        bundle["stats"]["prefixes"],
        bundle["stats"]["suggestions"],
    )

    LOGGER.info("Step 4/5 | Emit debug reports")
    if config.debug_docs:
        for doc_id in config.debug_docs:
            payload = debug_docs.get(doc_id)
            if payload is None:
                LOGGER.warning("No debug payload found for doc: %s", doc_id)
                continue
            LOGGER.info("Debug doc report | doc=%s\n%s", doc_id, json.dumps(payload, ensure_ascii=False, indent=2))

    if config.debug_terms:
        for raw_term in config.debug_terms:
            report = {"rawTerm": raw_term, "candidates": []}
            for candidate in build_debug_term_candidates(raw_term):
                report["candidates"].append(
                    {
                        "candidate": candidate,
                        "termIndex": serialize_postings(term_index.get(candidate, {}), docs),
                        "prefixIndex": serialize_postings(prefix_index.get(candidate, {}), docs, config.prefix_doc_limit),
                    }
                )
            LOGGER.info("Debug term report\n%s", json.dumps(report, ensure_ascii=False, indent=2))
    LOGGER.info("Step 4/5 done")

    LOGGER.info("Step 5/5 | Finalize output")
    if config.dry_run:
        LOGGER.info(
            "[dry-run] Bundle ready | docs=%d | terms=%d | prefixes=%d | suggestions=%d",
            bundle["stats"]["documents"],
            bundle["stats"]["terms"],
            bundle["stats"]["prefixes"],
            bundle["stats"]["suggestions"],
        )
    else:
        write_bundle(bundle, config)
        exists = config.output_file.exists()
        size = config.output_file.stat().st_size if exists else 0
        LOGGER.info(
            "Step 5/5 done | output_exists=%s | output_size_bytes=%d | output_file=%s",
            exists,
            size,
            config.output_file,
        )

    return bundle


def main() -> int:
    """脚本命令行入口。"""

    configure_console_encoding()
    args = parse_args()
    configure_logging(args.debug)
    try:
        config = build_config(args)
        bundle = run_build(config)
        return 0 if bundle else 1
    except BuildError as exc:
        LOGGER.error("%s", exc)
        return 1
    except Exception:
        LOGGER.exception("Unexpected build failure")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
