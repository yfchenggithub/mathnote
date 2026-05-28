# scan_math_blocks.mjs

## What this script does

This script scans a full `canonical_content_v2.json` tree and converts only manually approved formula blocks:

- from: `type: "math_block"`
- to: `type: "math_image_pending"`

It is an offline content-cleaning step for formula image pipeline staging.

## Why this phase only converts `need_image: true`

Automatic rule-only conversion caused false positives before. In this phase, manual UX judgment is the hard gate:

- must be `node.type === "math_block"`
- must be `node.need_image === true` (strict boolean)
- must have non-empty `node.latex` string

Any other value is skipped, including:

- missing `need_image`
- `need_image: false`
- `need_image: "true"`
- `need_image: 1`

## Why rules are still kept

Rules are still useful, but only as metadata:

- record `matchedRules` on converted nodes
- produce rule-hit statistics for audits
- help build future "recommend adding need_image" tools

Rules are **not** the decision gate in this stage (`rulesAreDecisionGate: false`).

## Node conversion behavior

When a node is converted, it keeps original fields and adds image-pending fields:

```json
{
  "type": "math_image_pending",
  "need_image": true,
  "latex": "...",
  "imageKey": "formula_a1b2c3d4e5f6",
  "imageName": "formula_a1b2c3d4e5f6",
  "matchedRules": ["sqrt", "aligned"],
  "asset": null
}
```

Notes:

- original `latex` is preserved
- original fields like `id`, `align`, `style`, etc. are preserved
- `need_image` is preserved for traceability

## Hash and key generation

`imageKey` and `imageName` are derived from normalized LaTeX:

1. `trim()`
2. collapse spaces with `/\\s+/g` to one space
3. `sha1` hash
4. use first 12 hex chars
5. prefix with `formula_`

This makes near-identical whitespace variants share the same key.

## Files

- script: `tools/formula_image_pipeline/scan_math_blocks.mjs`
- rules example: `tools/formula_image_pipeline/formula_image_rules.example.json`

## CLI usage

```bash
node tools/formula_image_pipeline/scan_math_blocks.mjs \
  --input data/content/canonical_content_v2.json \
  --output data/content/canonical_content_v2.pending.json \
  --rules tools/formula_image_pipeline/formula_image_rules.example.json
```

### Required args

- `--input` is required

### Optional args

- `--output`: default is `<input>.pending.json`
- `--rules`: default is `tools/formula_image_pipeline/formula_image_rules.example.json`
- `--dry-run`: do not write file, print stats only
- `--in-place`: overwrite input file explicitly

### `--output` + `--in-place`

To avoid accidental overwrite:

- if both are set and paths differ, script exits with error
- if `--in-place` is set, output target is input path

## Dry run example

```bash
node tools/formula_image_pipeline/scan_math_blocks.mjs \
  --input data/content/canonical_content_v2.json \
  --dry-run
```

## In-place example

```bash
node tools/formula_image_pipeline/scan_math_blocks.mjs \
  --input data/content/canonical_content_v2.json \
  --in-place
```

## Summary output

The script prints JSON summary with key metrics:

- total scanned node count
- total `math_block` count
- manually marked count (`need_image === true`)
- converted `math_image_pending` count
- skipped `math_block` without manual flag count
- `need_image === true` but empty latex count
- unique `imageKey` count
- output path and dry-run status

It also prints:

- `ruleHits` summary
- converted sample entries (path, key, rules, latex preview)
- warnings for empty-latex manual marks

## Error handling

Script exits non-zero for critical errors:

- input file missing
- input JSON parse failure
- rules file missing
- rules JSON parse failure
- invalid regex in rules
- output write failure

`need_image: true` with empty latex is warning-only (skipped node), not fatal.

## Handoff to next pipeline phase

Output `*.pending.json` is the handoff artifact for the image generation phase.
That later phase should:

1. read `math_image_pending`
2. generate image assets
3. fill `asset` fields
4. convert node type to `math_image`

This scanning step intentionally does not generate PNG/WebP and does not change frontend/backend/runtime infrastructure.
