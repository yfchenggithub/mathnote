# meta.json 叙述字段公式未生成 PNG 排查记录

## 背景

2026-06-24 排查 `C052` 时发现：

- `data/content/canonical_content_v2.json` 中 `C052.content.conditions[0].content` 是纯 `text`
- 文本里包含裸 LaTeX：`\\frac{x^2}{a^2}+\\frac{y^2}{b^2}=1`
- 该公式没有生成 `/static/formulas/C052/...@3x.png`

## 本质原因

源文件 `03_conic/C052_ellipse_focal_chord_length/meta.json` 的 `math.conditions` 把公式直接写在中文句子里，没有用 `$...$` 包起来。

错误写法：

```json
"conditions": "椭圆标准方程为\\frac{x^2}{a^2}+\\frac{y^2}{b^2}=1（a>b>0），焦点在x轴上..."
```

正确写法：

```json
"conditions": "椭圆标准方程为$\\frac{x^2}{a^2}+\\frac{y^2}{b^2}=1$（$a>b>0$），焦点在$x$轴上..."
```

## 构建链路表现

`build_detail_page_js.py` 主要识别 `$...$`、`\\(...\\)`、`\\[...\\]` 这类显式数学模式。裸 `\\frac` 混在中文句子里时，会被当作普通文本处理。

迁移到 canonical v2 后，普通文本会变成：

```json
{
  "type": "text",
  "text": "椭圆标准方程为\\frac{x^2}{a^2}+\\frac{y^2}{b^2}=1..."
}
```

`render_math_assets.mjs` 只处理 `math_inline` / `math_block`，不会从 `text` 中猜公式。因此不会生成 PNG。

## 排查方法

1. 查源头 `meta.json`：

```powershell
rg -n "\\\\frac|\\\\sqrt|\\\\theta|θ|L=|a>b" 03_conic\\C052_ellipse_focal_chord_length\\meta.json
```

2. 临时重建详情 JS：

```powershell
python -B scripts\\build_detail_page_js.py --module 03_conic --item C052 --output-dir .tmp\\c052_probe_detail
```

3. 临时迁移 canonical：

```powershell
python -B scripts\\migrate_detail_js_to_content_v2.py --input .tmp\\c052_probe_detail\\03_conic.js --output .tmp\\c052_probe_detail\\canonical_content_v2.json --report .tmp\\c052_probe_detail\\conversion_report.json --skip-validation
```

4. 看结构是否出现 `math_inline`：

```powershell
node -e "const fs=require('fs'); const d=JSON.parse(fs.readFileSync('.tmp/c052_probe_detail/canonical_content_v2.json','utf8')).C052; console.log(JSON.stringify(d.content.conditions,null,2));"
```

## 修复规范

- `math.conditions`、`math.conclusions`、`content.statement`、`content.common_tricks` 等中文叙述字段，只要夹带公式、变量、不等式或 LaTeX 命令，都要用 `$...$`。
- JSON 字符串中 LaTeX 命令仍然只转义一次：源 LaTeX `\frac` 写成 `"\\frac"`。
- 数学环境中不要放中文解释和中文标点。
- 变量也建议显式数学模式，例如 `$x$` 轴、倾斜角 `$\\theta$`、弦长 `$L$`。

## 预防措施

已在 `12_pipeline/prompts/P05_SearchMetaBuilder.pt` 增加硬约束：生成 `meta.json` 时，中文叙述字段里的公式必须使用 `$...$`，避免后续被迁移成纯 `text`。

同时在 `scripts/migrate_detail_js_to_content_v2.py` 中补充了显式数学模式拆分：顶层 `content.conditions` / `content.conclusions` 遇到 `$...$`、`\\(...\\)`、`\\[...\\]` 会迁移成 `math_inline` / `math_display` token。注意这不是裸公式猜测器，源头仍必须写数学模式。
