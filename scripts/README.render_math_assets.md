# render_math_assets.mjs

## 1. 这个脚本做什么

`scripts/render_math_assets.mjs` 是「公式图片生成流水线」的**第二步：渲染层**。

它会递归扫描输入 JSON，只处理满足以下条件的节点：

- `type === "math_block"`
- `need_image === "true"`
- `latex` 非空

然后把这些公式渲染为图片资源（PNG + WebP），并把节点改写为 `math_image`，写回新的内容 JSON。

---

## 2. 为什么要做这一步

第一步（标记层）已经决定“哪些公式需要图片化”，渲染层只负责执行，不再做复杂判断。这样做的好处：

- 决策与执行解耦，便于回溯
- 渲染逻辑稳定，批处理可重复
- 单个公式失败不会拖垮整批处理

---

## 3. 怎么做的（处理流程）

整体流程：

1. 读取输入 JSON
2. 递归遍历整棵树，筛出待渲染节点
3. 对 `latex.trim()` 做 `sha1`，取前 16 位作为稳定 hash
4. 相同 hash 只渲染一次（去重复用）
5. 使用 MathJax（`input/tex + output/svg`，`fontCache:none`）把 LaTeX 转成 SVG
6. 使用 sharp 将 SVG 栅格化并输出透明背景 PNG/WebP
7. 如果目标文件已存在且 `force=false`：跳过重渲染，读取现有 PNG metadata 回写尺寸
8. 将成功节点改为 `type: "math_image"` 并写入 `asset`
9. 输出内容 JSON 和渲染报告

---

## 4. 关键规则

- **只处理** `math_block + need_image:"true" + latex 非空`
- 不处理 `math_inline`
- 不自动新增 `need_image`
- 不改动其他不匹配节点
- 保留原有字段（如 `title / align / meta / note` 等）
- 仅变更 `type` 并新增/更新 `asset`

---

## 5. 输入输出

脚本当前默认值（以代码为准）：

- 输入：`data/canonical_content_v2.json`
- 输出 JSON：`data/canonical_content_v2.with_formula_assets.json`
- 图片目录：`public/static/formulas`
- 报告：`reports/render_math_assets_report.json`
- 公网前缀：`https://ok-shuxue.icu/static/formulas`
- `scale`：`3`

---

## 6. 文件命名与复用

对每个公式：

- `hash = sha1(latex.trim()).slice(0, 16)`
- 文件名：
  - `<hash>@<scale>x.png`
  - `<hash>@<scale>x.webp`

例如 `scale=3` 时：`92957e7d5dc6abfb@3x.png`

相同 LaTeX（去首尾空白后）会复用同一份图片，不重复渲染。

---

## 7. 节点改写示例

原节点：

```json
{
  "type": "math_block",
  "latex": "\\sqrt{x^2+1}",
  "need_image": "true"
}
```

改写后（示意）：

```json
{
  "type": "math_image",
  "latex": "\\sqrt{x^2+1}",
  "need_image": "true",
  "asset": {
    "png": "https://.../<hash>@3x.png",
    "webp": "https://.../<hash>@3x.webp",
    "width_px": 960,
    "height_px": 360,
    "display_width_px": 320,
    "display_height_px": 120,
    "scale": 3
  }
}
```

---

## 8. 报告结构（render_math_assets_report.json）

报告包含：

- 运行参数快照：`input/output/outDir/publicBase/scale`
- 统计项：`totalMarked/rendered/reused/failed/skipped`
- 逐公式明细：`items[]`（状态、产物 URL、尺寸、错误信息）

状态含义：

- `rendered`：本次新渲染
- `reused`：复用已有文件
- `failed`：渲染失败
- `dry_run`：仅扫描，不落盘

---

## 9. CLI 参数

```bash
node scripts/render_math_assets.mjs [options]
```

可用参数：

- `--input <path>`：输入 JSON
- `--output <path>`：输出 JSON
- `--in-place`：原地覆盖输入 JSON（直接修改源文件）
- `--out-dir <path>`：图片输出目录
- `--public-base <url>`：图片公网前缀
- `--scale <number>`：图片倍率（正整数）
- `--force [true|false]`：是否强制重渲染
- `--dry-run [true|false]`：仅扫描不生成文件
- `--limit <number>`：最多处理多少个唯一公式
- `--help`：查看帮助

---

## 10. 使用示例

1) 常规渲染：

```bash
npm run formula:render
```

2) 强制重渲染：

```bash
npm run formula:render:force
```

3) 原地覆盖输入文件：

```bash
node scripts/render_math_assets.mjs --in-place
```

4) 只扫描，不落盘：

```bash
node scripts/render_math_assets.mjs --dry-run true
```

5) 限量试跑（前 20 个唯一公式）：

```bash
node scripts/render_math_assets.mjs --limit 20
```

6) 自定义输入输出：

```bash
node scripts/render_math_assets.mjs ^
  --input data/canonical_content_v2.marked.json ^
  --output data/canonical_content_v2.with_formula_assets.json ^
  --out-dir public/static/formulas ^
  --public-base https://ok-shuxue.cloud/static/formulas ^
  --scale 3
```

注意：
- `--in-place` 与 `--output` 同时使用时，`--output` 必须与 `--input` 为同一路径，否则脚本会报错退出（防误覆盖）。

---

## 11. 错误处理策略

- 单个公式失败：记录到 `report.items[].error`，继续处理后续公式
- 失败节点：保持原 `math_block`，不会误改成 `math_image`
- 整体流程只在关键错误（如输入文件不可读、JSON 解析失败）时退出

---

## 12. 与技术约束的一致性

本脚本采用：

- MathJax：LaTeX -> SVG
- sharp：SVG -> PNG/WebP

且未使用：

- Playwright
- Chromium
- 浏览器截图
