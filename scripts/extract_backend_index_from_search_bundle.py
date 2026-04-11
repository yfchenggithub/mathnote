#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
脚本名称: extract_backend_index_from_search_bundle.py
===============================================================================

用途
----
把微信小程序前端使用的 CommonJS 搜索 bundle（`search_bundle.js`）提取为
后端可直接加载的标准 JSON 索引文件。

适用场景
--------
`search_bundle.js` 不是纯 JSON，而是类似：

const searchBundle = { ... };
module.exports = searchBundle;

这类 JS 对象字面量可能包含：
1. 行注释/块注释
2. 未加引号的对象 key（包含 Unicode 标识符，如中文）
3. 单引号字符串
4. 尾逗号

因此不能直接 `json.load()`，也不应使用脆弱的全局正则替换。

输入/输出
---------
输入:
- `--input`: JS bundle 文件路径（默认 `data/search_engine/search_bundle.js`）

输出:
- `--output`: 后端 JSON 文件路径（默认 `data/search_engine/backend_search_index.json`）

核心设计
--------
1. 先用“状态机扫描”在整个 JS 文件中精准定位 `searchBundle = { ... }`。
   - 扫描时显式处理字符串、注释、模板字符串，避免把字符串内部的大括号误判。
2. 对对象字面量使用“零依赖递归下降解析器”做语法级解析，而不是字符串替换。
   - 支持对象/数组/字符串/数字/布尔/null
   - 支持注释与尾逗号
   - 支持未加引号 key（JS IdentifierName，含中文）
3. 转成 Python 对象后再标准化写成 JSON，供后端直接加载。

为什么这样设计
--------------
1. 稳健：规避“正则误伤字符串内容”的典型风险（LaTeX、反斜杠、中文、引号）。
2. 可维护：函数职责清晰，日志完整，校验可追踪。
3. 零依赖：默认只用 Python 标准库，便于 CI/CD 与离线环境执行。

与后端索引的关系
----------------
输出 JSON 结构默认保留原始索引字段（`docs`、`termIndex`、`prefixIndex`、
`suggestions` 等）不改语义、不改数值，可直接被后端服务加载。
可选附加轻量 `meta`（可通过 `--no-meta` 关闭）。

示例
----
python scripts/extract_backend_index_from_search_bundle.py ^
  --input data/search_engine/search_bundle.js ^
  --output data/search_engine/backend_search_index.json ^
  --pretty


python scripts/extract_backend_index_from_search_bundle.py ^
  --input data/search_engine/search_bundle.js ^
  --output data/search_engine/backend_search_index.json ^
  --compact ^
  --no-meta ^
  --fail-on-warning
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("extract_backend_index_from_search_bundle")

EXTRACTOR_VERSION = "1.0.0"
DEFAULT_INPUT = Path("data/search_engine/search_bundle.js")
DEFAULT_OUTPUT = Path("data/search_engine/backend_search_index.json")

EXPECTED_TOP_LEVEL_FIELDS: tuple[str, ...] = (
    "version",
    "generatedAt",
    "stats",
    "buildOptions",
    "fieldMaskLegend",
    "docs",
    "termIndex",
    "prefixIndex",
    "suggestions",
)

REQUIRED_CORE_FIELDS: tuple[str, ...] = (
    "docs",
    "termIndex",
    "prefixIndex",
    "suggestions",
)


class ExtractionError(RuntimeError):
    """对象字面量抽取失败。"""


class JsLiteralParseError(ValueError):
    """JS 字面量解析失败。"""


def read_text_file(path: Path, encoding: str = "utf-8") -> str:
    """读取文本文件并返回字符串。

    做什么:
    - 读取输入 JS 文件内容。

    为什么这样做:
    - 统一在入口做文件 I/O 与异常包装，方便日志与定位。

    输入:
    - path: 输入文件路径
    - encoding: 文本编码（建议 utf-8）

    输出:
    - 文件完整文本内容
    """

    try:
        return path.read_text(encoding=encoding)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"输入文件不存在: {path}") from exc
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding,
            exc.object,
            exc.start,
            exc.end,
            f"输入文件解码失败: {path}，请确认编码或通过 --encoding 指定 ({exc.reason})",
        ) from exc


def _is_js_identifier_start(ch: str) -> bool:
    """判断字符是否可作为 JS IdentifierName 的首字符（简化实现，含 Unicode）。"""

    if not ch:
        return False
    if ch in {"$", "_"}:
        return True
    return unicodedata.category(ch) in {"Lu", "Ll", "Lt", "Lm", "Lo", "Nl"}


def _is_js_identifier_part(ch: str) -> bool:
    """判断字符是否可作为 JS IdentifierName 的后续字符（简化实现，含 Unicode）。"""

    if _is_js_identifier_start(ch):
        return True
    if ch in {"\u200c", "\u200d"}:
        return True
    return unicodedata.category(ch) in {"Mn", "Mc", "Nd", "Pc"}


def _line_col(text: str, index: int) -> tuple[int, int]:
    """根据字符偏移返回行列号（1-based）。"""

    line = text.count("\n", 0, index) + 1
    last_newline = text.rfind("\n", 0, index)
    if last_newline < 0:
        col = index + 1
    else:
        col = index - last_newline
    return line, col


def _scan_skip_line_comment(text: str, index: int) -> int:
    """跳过 `//` 行注释，返回下一位置。"""

    pos = index + 2
    while pos < len(text) and text[pos] not in "\r\n":
        pos += 1
    return pos


def _scan_skip_block_comment(text: str, index: int) -> int:
    """跳过 `/* ... */` 块注释，返回下一位置。"""

    end = text.find("*/", index + 2)
    if end < 0:
        line, col = _line_col(text, index)
        raise ExtractionError(f"块注释未闭合，位置 line={line}, col={col}")
    return end + 2


def _scan_skip_string(text: str, index: int) -> int:
    """跳过普通字符串（单引号/双引号）。"""

    quote = text[index]
    pos = index + 1
    while pos < len(text):
        ch = text[pos]
        if ch == "\\":
            pos += 2
            continue
        if ch == quote:
            return pos + 1
        if ch in "\r\n":
            line, col = _line_col(text, pos)
            raise ExtractionError(
                f"字符串中出现未转义换行，位置 line={line}, col={col}"
            )
        pos += 1
    line, col = _line_col(text, index)
    raise ExtractionError(f"字符串未闭合，位置 line={line}, col={col}")


def _scan_skip_template_expr(text: str, index: int) -> int:
    """跳过模板字符串中的 `${ ... }` 表达式。"""

    depth = 1
    pos = index
    while pos < len(text):
        ch = text[pos]
        if ch in {"'", '"'}:
            pos = _scan_skip_string(text, pos)
            continue
        if ch == "`":
            pos = _scan_skip_template(text, pos)
            continue
        if ch == "/" and pos + 1 < len(text):
            nxt = text[pos + 1]
            if nxt == "/":
                pos = _scan_skip_line_comment(text, pos)
                continue
            if nxt == "*":
                pos = _scan_skip_block_comment(text, pos)
                continue
        if ch == "{":
            depth += 1
            pos += 1
            continue
        if ch == "}":
            depth -= 1
            pos += 1
            if depth == 0:
                return pos
            continue
        pos += 1

    line, col = _line_col(text, index)
    raise ExtractionError(f"模板字符串插值表达式未闭合，位置 line={line}, col={col}")


def _scan_skip_template(text: str, index: int) -> int:
    """跳过模板字符串（反引号），支持跳过插值表达式。"""

    pos = index + 1
    while pos < len(text):
        ch = text[pos]
        if ch == "\\":
            pos += 2
            continue
        if ch == "`":
            return pos + 1
        if ch == "$" and pos + 1 < len(text) and text[pos + 1] == "{":
            pos = _scan_skip_template_expr(text, pos + 2)
            continue
        pos += 1

    line, col = _line_col(text, index)
    raise ExtractionError(f"模板字符串未闭合，位置 line={line}, col={col}")


def _scan_skip_ignored(text: str, index: int) -> int:
    """跳过空白与注释，返回新的位置。"""

    pos = index
    while pos < len(text):
        ch = text[pos]
        if ch.isspace():
            pos += 1
            continue
        if ch == "/" and pos + 1 < len(text):
            nxt = text[pos + 1]
            if nxt == "/":
                pos = _scan_skip_line_comment(text, pos)
                continue
            if nxt == "*":
                pos = _scan_skip_block_comment(text, pos)
                continue
        break
    return pos


def _extract_balanced_object_literal(text: str, brace_start: int) -> str:
    """从 `{` 起始位置提取完整对象字面量（平衡大括号）。"""

    if brace_start >= len(text) or text[brace_start] != "{":
        raise ExtractionError("内部错误：对象提取起点不是 '{'")

    depth = 0
    pos = brace_start
    while pos < len(text):
        ch = text[pos]
        if ch == "{":
            depth += 1
            pos += 1
            continue
        if ch == "}":
            depth -= 1
            pos += 1
            if depth == 0:
                return text[brace_start:pos]
            continue
        if ch in {"'", '"'}:
            pos = _scan_skip_string(text, pos)
            continue
        if ch == "`":
            pos = _scan_skip_template(text, pos)
            continue
        if ch == "/" and pos + 1 < len(text):
            nxt = text[pos + 1]
            if nxt == "/":
                pos = _scan_skip_line_comment(text, pos)
                continue
            if nxt == "*":
                pos = _scan_skip_block_comment(text, pos)
                continue
        pos += 1

    line, col = _line_col(text, brace_start)
    raise ExtractionError(f"对象字面量未闭合，起点 line={line}, col={col}")


def extract_search_bundle_object_literal(
    js_text: str, variable_name: str = "searchBundle"
) -> str:
    """从整个 JS 文件中精准提取 `searchBundle = { ... }` 对象字面量。

    做什么:
    - 在忽略字符串/注释的前提下扫描标识符。
    - 找到 `searchBundle` 后匹配 `=` 和后续 `{...}`。

    为什么这样做:
    - 不能用脆弱正则直接匹配整个大对象，容易误伤字符串和注释中的符号。

    输入:
    - js_text: JS 文件全文
    - variable_name: 变量名，默认 `searchBundle`

    输出:
    - 精确截取的对象字面量文本（含最外层 `{...}`）
    """

    pos = 0
    length = len(js_text)
    while pos < length:
        ch = js_text[pos]

        if ch in {"'", '"'}:
            pos = _scan_skip_string(js_text, pos)
            continue
        if ch == "`":
            pos = _scan_skip_template(js_text, pos)
            continue
        if ch == "/" and pos + 1 < length:
            nxt = js_text[pos + 1]
            if nxt == "/":
                pos = _scan_skip_line_comment(js_text, pos)
                continue
            if nxt == "*":
                pos = _scan_skip_block_comment(js_text, pos)
                continue
        if _is_js_identifier_start(ch):
            start = pos
            pos += 1
            while pos < length and _is_js_identifier_part(js_text[pos]):
                pos += 1
            ident = js_text[start:pos]
            if ident != variable_name:
                continue

            cursor = _scan_skip_ignored(js_text, pos)
            if cursor >= length or js_text[cursor] != "=":
                continue
            cursor = _scan_skip_ignored(js_text, cursor + 1)
            if cursor >= length or js_text[cursor] != "{":
                continue
            return _extract_balanced_object_literal(js_text, cursor)
        else:
            pos += 1

    raise ExtractionError(f"未找到 `{variable_name} = {{...}}` 对象字面量")


class JsObjectLiteralParser:
    """零依赖 JS 字面量解析器（面向对象字面量场景）。"""

    NUMBER_RE = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?")
    SIMPLE_ESCAPES: dict[str, str] = {
        '"': '"',
        "'": "'",
        "\\": "\\",
        "/": "/",
        "`": "`",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "0": "\0",
    }

    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)
        self.pos = 0

    def parse(self) -> Any:
        """解析入口。"""

        self._skip_ignored()
        value = self._parse_value()
        self._skip_ignored()
        if self.pos != self.length:
            raise self._error("对象字面量后存在额外内容")
        return value

    def _peek(self) -> str:
        if self.pos >= self.length:
            return ""
        return self.text[self.pos]

    def _error(self, message: str) -> JsLiteralParseError:
        line, col = _line_col(self.text, self.pos)
        snippet = self.text[self.pos : self.pos + 80].replace("\n", "\\n")
        return JsLiteralParseError(
            f"{message} (line={line}, col={col}, near={snippet!r})"
        )

    def _skip_ignored(self) -> None:
        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch.isspace():
                self.pos += 1
                continue
            if ch == "/" and self.pos + 1 < self.length:
                nxt = self.text[self.pos + 1]
                if nxt == "/":
                    self.pos = _scan_skip_line_comment(self.text, self.pos)
                    continue
                if nxt == "*":
                    self.pos = _scan_skip_block_comment(self.text, self.pos)
                    continue
            break

    def _consume(self, token: str) -> None:
        if not self.text.startswith(token, self.pos):
            raise self._error(f"期望 {token!r}")
        self.pos += len(token)

    def _parse_value(self) -> Any:
        self._skip_ignored()
        ch = self._peek()
        if not ch:
            raise self._error("意外到达输入末尾")

        if ch == "{":
            return self._parse_object()
        if ch == "[":
            return self._parse_array()
        if ch in {'"', "'", "`"}:
            return self._parse_string()
        if ch == "-" or ch.isdigit():
            return self._parse_number()
        if _is_js_identifier_start(ch):
            ident = self._parse_identifier()
            if ident == "true":
                return True
            if ident == "false":
                return False
            if ident == "null":
                return None
            raise self._error(f"不支持的裸标识符值: {ident!r}")

        raise self._error(f"不支持的值起始字符: {ch!r}")

    def _parse_object(self) -> dict[str, Any]:
        self._consume("{")
        self._skip_ignored()
        result: dict[str, Any] = {}
        if self._peek() == "}":
            self.pos += 1
            return result

        while True:
            self._skip_ignored()
            key = self._parse_object_key()

            self._skip_ignored()
            self._consume(":")
            value = self._parse_value()
            result[key] = value

            self._skip_ignored()
            ch = self._peek()
            if ch == ",":
                self.pos += 1
                self._skip_ignored()
                if self._peek() == "}":
                    self.pos += 1
                    break
                continue
            if ch == "}":
                self.pos += 1
                break
            raise self._error("对象属性之间缺少逗号或右花括号")

        return result

    def _parse_object_key(self) -> str:
        ch = self._peek()
        if not ch:
            raise self._error("对象 key 缺失")
        if ch in {'"', "'", "`"}:
            return self._parse_string()
        if _is_js_identifier_start(ch):
            return self._parse_identifier()
        if ch == "-" or ch.isdigit():
            token = self._consume_number_token()
            return self._normalize_number_key(token)
        raise self._error(f"不支持的对象 key 起始字符: {ch!r}")

    def _parse_array(self) -> list[Any]:
        self._consume("[")
        self._skip_ignored()
        result: list[Any] = []
        if self._peek() == "]":
            self.pos += 1
            return result

        while True:
            result.append(self._parse_value())
            self._skip_ignored()
            ch = self._peek()
            if ch == ",":
                self.pos += 1
                self._skip_ignored()
                if self._peek() == "]":
                    self.pos += 1
                    break
                continue
            if ch == "]":
                self.pos += 1
                break
            raise self._error("数组元素之间缺少逗号或右中括号")

        return result

    def _parse_number(self) -> int | float:
        token = self._consume_number_token()
        if "." in token or "e" in token or "E" in token:
            return float(token)
        return int(token)

    def _consume_number_token(self) -> str:
        match = self.NUMBER_RE.match(self.text, self.pos)
        if not match:
            raise self._error("非法数字字面量")
        token = match.group(0)
        self.pos = match.end()
        return token

    @staticmethod
    def _normalize_number_key(token: str) -> str:
        """把 JS 数字 key 规范成字符串 key。"""

        try:
            if "." in token or "e" in token or "E" in token:
                number = float(token)
                if number == 0.0:
                    return "0"
                if number.is_integer():
                    return str(int(number))
                return format(number, ".15g")
            return str(int(token))
        except ValueError:
            return token

    def _parse_identifier(self) -> str:
        ch = self._peek()
        if not _is_js_identifier_start(ch):
            raise self._error(f"非法标识符起始字符: {ch!r}")
        start = self.pos
        self.pos += 1
        while self.pos < self.length and _is_js_identifier_part(self.text[self.pos]):
            self.pos += 1
        return self.text[start : self.pos]

    def _parse_hex_digits(self, count: int) -> str:
        if self.pos + count > self.length:
            raise self._error("Unicode/Hex 转义序列长度不足")
        digits = self.text[self.pos : self.pos + count]
        if any(ch not in "0123456789abcdefABCDEF" for ch in digits):
            raise self._error(f"非法 Hex 数字: {digits!r}")
        self.pos += count
        return digits

    def _parse_string(self) -> str:
        quote = self._peek()
        if quote not in {'"', "'", "`"}:
            raise self._error("内部错误：当前不是字符串起始")
        self.pos += 1

        chars: list[str] = []
        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch == quote:
                self.pos += 1
                return "".join(chars)

            if quote == "`" and ch == "$" and self.pos + 1 < self.length:
                if self.text[self.pos + 1] == "{":
                    raise self._error("不支持包含插值表达式 `${...}` 的模板字符串")

            if ch == "\\":
                self.pos += 1
                if self.pos >= self.length:
                    raise self._error("反斜杠转义不完整")
                esc = self.text[self.pos]
                self.pos += 1

                if esc in self.SIMPLE_ESCAPES:
                    chars.append(self.SIMPLE_ESCAPES[esc])
                    continue
                if esc in {"\n", "\r"}:
                    # JS 行继续：反斜杠 + 换行不产生字符。
                    if esc == "\r" and self.pos < self.length and self.text[self.pos] == "\n":
                        self.pos += 1
                    continue
                if esc == "x":
                    digits = self._parse_hex_digits(2)
                    chars.append(chr(int(digits, 16)))
                    continue
                if esc == "u":
                    if self._peek() == "{":
                        self.pos += 1
                        start = self.pos
                        while self.pos < self.length and self.text[self.pos] != "}":
                            self.pos += 1
                        if self.pos >= self.length:
                            raise self._error("Unicode 转义 `\\u{...}` 未闭合")
                        code = self.text[start : self.pos]
                        if not code or any(
                            c not in "0123456789abcdefABCDEF" for c in code
                        ):
                            raise self._error(f"非法 Unicode 转义: {code!r}")
                        self.pos += 1
                        code_point = int(code, 16)
                        if code_point > 0x10FFFF:
                            raise self._error(f"Unicode 码点超范围: U+{code_point:04X}")
                        chars.append(chr(code_point))
                        continue
                    digits = self._parse_hex_digits(4)
                    chars.append(chr(int(digits, 16)))
                    continue

                # 非标准转义保守处理：保留被转义字符本身。
                chars.append(esc)
                continue

            if ch in {"\n", "\r"} and quote != "`":
                raise self._error("普通字符串中出现未转义换行")

            chars.append(ch)
            self.pos += 1

        raise self._error("字符串未闭合")


def convert_js_object_literal_to_json_text(object_literal: str) -> str:
    """把 JS 对象字面量转换为标准 JSON 文本。

    做什么:
    - 解析 JS 字面量到 Python 对象，再序列化为 JSON 文本。

    为什么这样做:
    - 避免“替换字符串”的脆弱转换方式，保证字符串内容与转义语义不被破坏。

    输入:
    - object_literal: 已截取的 `{ ... }` 文本

    输出:
    - 标准 JSON 文本（紧凑模式，UTF-8 语义）
    """

    parsed = JsObjectLiteralParser(object_literal).parse()
    return json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))


def load_bundle_to_python_obj(object_literal: str) -> dict[str, Any]:
    """把对象字面量加载为 Python 字典。

    做什么:
    - 调用转换函数得到 JSON 文本，再反序列化为 Python 对象。

    为什么这样做:
    - 强制走“JS 语义解析 -> 标准 JSON”路径，统一并可复用中间产物。

    输入:
    - object_literal: 已截取对象字面量文本

    输出:
    - Python 字典结构（对应 searchBundle 顶层对象）
    """

    json_text = convert_js_object_literal_to_json_text(object_literal)
    loaded = json.loads(json_text)
    if not isinstance(loaded, dict):
        raise TypeError(f"searchBundle 顶层必须是对象，实际得到: {type(loaded).__name__}")
    return loaded


def validate_bundle_payload(
    bundle: Mapping[str, Any], fail_on_warning: bool = False
) -> list[str]:
    """对解析结果做基础完整性校验。

    做什么:
    - 校验关键顶层字段是否存在/类型正确。
    - 如果存在 `stats`，做与 `docs/termIndex/prefixIndex/suggestions` 的数量交叉检查。

    为什么这样做:
    - 尽早发现迁移损坏或结构异常，保证后端索引可用性。

    输入:
    - bundle: 解析后的 searchBundle 对象
    - fail_on_warning: 是否把 warning 升级为失败

    输出:
    - warning 文本列表（便于日志或上层处理）
    """

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(bundle, Mapping):
        raise TypeError(f"bundle 顶层必须是 Mapping，实际得到: {type(bundle).__name__}")

    for field in EXPECTED_TOP_LEVEL_FIELDS:
        if field not in bundle:
            warnings.append(f"缺少预期顶层字段: {field}")

    expected_types: dict[str, type[Any]] = {
        "docs": dict,
        "termIndex": dict,
        "prefixIndex": dict,
        "suggestions": list,
    }
    for key in REQUIRED_CORE_FIELDS:
        if key not in bundle:
            errors.append(f"缺少核心字段: {key}")
            continue
        expected_type = expected_types[key]
        if not isinstance(bundle[key], expected_type):
            errors.append(
                f"核心字段类型不匹配: {key} 期望 {expected_type.__name__}，实际 {type(bundle[key]).__name__}"
            )

    stats = bundle.get("stats")
    if stats is not None:
        if not isinstance(stats, Mapping):
            warnings.append(f"`stats` 不是对象类型，实际为 {type(stats).__name__}")
        else:
            count_pairs = (
                ("documents", "docs"),
                ("terms", "termIndex"),
                ("prefixes", "prefixIndex"),
                ("suggestions", "suggestions"),
            )
            for stats_key, bundle_key in count_pairs:
                if bundle_key in bundle and isinstance(bundle[bundle_key], (dict, list)):
                    actual_count = len(bundle[bundle_key])
                else:
                    continue

                if stats_key not in stats:
                    warnings.append(f"`stats` 缺少字段: {stats_key}")
                    continue

                expected_count = stats[stats_key]
                if not isinstance(expected_count, int):
                    warnings.append(
                        f"`stats.{stats_key}` 不是整数，实际为 {type(expected_count).__name__}"
                    )
                    continue

                if expected_count != actual_count:
                    warnings.append(
                        f"统计不一致: stats.{stats_key}={expected_count}，实际 {bundle_key} 数量={actual_count}"
                    )

    if errors:
        message = "校验失败:\n- " + "\n- ".join(errors)
        raise ValueError(message)

    if warnings and fail_on_warning:
        message = "出现 warning 且启用了 --fail-on-warning:\n- " + "\n- ".join(warnings)
        raise ValueError(message)

    return warnings


def build_backend_json_payload(
    bundle: Mapping[str, Any], source_file: Path, include_meta: bool = True
) -> dict[str, Any]:
    """构造最终输出 JSON 载荷。

    做什么:
    - 默认在不改变原始字段语义的前提下，附加轻量 meta 信息。
    - `--no-meta` 时仅输出原始 bundle 字段。

    为什么这样做:
    - 后端可追踪数据来源与提取时间，同时保留原始索引字段完整性。

    输入:
    - bundle: 解析后的原始 searchBundle 对象
    - source_file: 源文件路径（写入 meta）
    - include_meta: 是否附加 meta

    输出:
    - 最终写盘的 JSON 对象
    """

    payload = dict(bundle)
    if not include_meta:
        return payload

    meta = {
        "source_file": str(source_file),
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "extractor_version": EXTRACTOR_VERSION,
    }

    if "meta" not in payload:
        return {"meta": meta, **payload}

    # 兜底：若原始 bundle 已含 meta，避免覆盖原始语义。
    payload["_extractor_meta"] = meta
    return payload


def write_json_file(
    path: Path, data: Mapping[str, Any], pretty: bool = True, ensure_ascii: bool = False
) -> None:
    """把最终载荷写出为 JSON 文件。

    做什么:
    - 自动创建输出目录。
    - 以 UTF-8（无 BOM）写入。
    - 支持 pretty/compact 两种模式。

    为什么这样做:
    - 后端场景通常需要可控输出风格，以及稳定的编码行为。

    输入:
    - path: 输出文件路径
    - data: 要写出的 JSON 对象
    - pretty: True=缩进 2 空格，False=紧凑输出
    - ensure_ascii: 是否转义非 ASCII 字符

    输出:
    - 无（写文件）
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        if pretty:
            json.dump(data, file, ensure_ascii=ensure_ascii, indent=2)
            file.write("\n")
        else:
            json.dump(data, file, ensure_ascii=ensure_ascii, separators=(",", ":"))
            file.write("\n")


def _format_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KiB"
    return f"{num_bytes / (1024 * 1024):.2f} MiB"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="从 CommonJS search_bundle.js 中抽取后端可用 JSON 索引。"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"输入 JS bundle 路径，默认: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"输出 JSON 路径，默认: {DEFAULT_OUTPUT}",
    )
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--pretty",
        action="store_true",
        help="输出可读 JSON（缩进 2 空格）。默认即 pretty。",
    )
    format_group.add_argument(
        "--compact",
        action="store_true",
        help="输出紧凑 JSON（无额外空白）。",
    )
    parser.add_argument(
        "--ensure-ascii",
        action="store_true",
        help="启用 JSON ensure_ascii=True（非 ASCII 将转义）。",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="输入文件编码，默认 utf-8。",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="出现 warning（如统计不一致）时直接失败退出。",
    )
    parser.add_argument(
        "--no-meta",
        action="store_true",
        help="不写入新增 meta 字段，只输出原始 bundle 内容。",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="日志级别，默认 INFO。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """命令行入口。"""

    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        LOGGER.info("步骤 1/6: 读取输入文件 -> %s", args.input)
        js_text = read_text_file(args.input, encoding=args.encoding)

        LOGGER.info("步骤 2/6: 抽取 searchBundle 对象字面量")
        object_literal = extract_search_bundle_object_literal(js_text, "searchBundle")
        LOGGER.info("对象字面量抽取完成，长度=%d 字符", len(object_literal))

        LOGGER.info("步骤 3/6: 解析对象字面量为 Python 数据结构")
        bundle = load_bundle_to_python_obj(object_literal)
        LOGGER.info("解析完成，顶层字段数=%d", len(bundle))

        LOGGER.info("步骤 4/6: 执行结构与统计校验")
        warnings = validate_bundle_payload(bundle, fail_on_warning=args.fail_on_warning)
        if warnings:
            for item in warnings:
                LOGGER.warning(item)
        else:
            LOGGER.info("校验通过，无 warning")

        LOGGER.info("步骤 5/6: 构建后端 JSON 载荷")
        payload = build_backend_json_payload(
            bundle=bundle,
            source_file=args.input,
            include_meta=not args.no_meta,
        )

        LOGGER.info("步骤 6/6: 写出 JSON 文件 -> %s", args.output)
        pretty = not args.compact
        write_json_file(
            path=args.output,
            data=payload,
            pretty=pretty,
            ensure_ascii=args.ensure_ascii,
        )

        output_size = args.output.stat().st_size
        docs_count = len(bundle["docs"]) if isinstance(bundle.get("docs"), dict) else -1
        terms_count = (
            len(bundle["termIndex"]) if isinstance(bundle.get("termIndex"), dict) else -1
        )
        prefixes_count = (
            len(bundle["prefixIndex"])
            if isinstance(bundle.get("prefixIndex"), dict)
            else -1
        )
        suggestions_count = (
            len(bundle["suggestions"])
            if isinstance(bundle.get("suggestions"), list)
            else -1
        )

        LOGGER.info(
            "输出完成 | 文件大小=%s | docs=%d | terms=%d | prefixes=%d | suggestions=%d",
            _format_size(output_size),
            docs_count,
            terms_count,
            prefixes_count,
            suggestions_count,
        )
        return 0

    except Exception as exc:
        LOGGER.exception("执行失败: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
