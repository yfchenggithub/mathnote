# Task 13G.1 — C051 static cards final freeze

Date: 2026-10-09 (Asia/Shanghai). Status: **TASK 13G.1 FINAL FREEZE — PASS**.
Scope: C051's three static PNG cards and the preview-only `scripts/static_cards.build`
interface used to produce them. This does not freeze Task 13G.0A, other UIDs,
Manim, Publisher, or the whole Task 13G series.

## Formal assets

UID: `C051`. Formal directory:
`03_conic/C051_parabola_focal_radius_coordinate/images/`.

| Card | File | SHA-256 |
| --- | --- | --- |
| 快记 | `001.png` | `b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0` |
| 快懂 | `002.png` | `736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9` |
| 快用 | `003.png` | `01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313` |

Each formal PNG matched the corresponding `.build/static_cards/C051/` preview
by SHA-256 after publication. The existing 001 and 002 were replaced only after
their prior hashes were recorded and backups were made under
`.build/static_cards/C051/publication_13g1b/old/`. Existing 003 already matched
the preview and was left byte-for-byte unchanged. No SVG, contact sheet, or
report was put in formal `images/`.

## Source and validation

C051-specific model, card definitions, and tests are in
`03_conic/C051_parabola_focal_radius_coordinate/static_cards/`. UID-neutral
canvas and preview builder are in `scripts/static_cards/`. Preview output remains
isolated in `.build/static_cards/C051/`; the builder never writes formal images.

- Mathematical and diagram checks: **8/8 PASS**. The cases cover positive
  parameters, vertex, upper/lower points, focus, directrix, foot, perpendicular
  construction, `PF=PH`, focal-radius formula, invalid points, exact curve
  samples beyond P, and label/line clearances.
- Rendering: **PASS**. All PNGs decoded at 1080×1440. The 001/002 PF labels
  were inspected at original size and in the 360-pixel-wide contact sheet;
  their padded text bounds do not intersect the PF segment or parabola.
  Chinese, formulas, clipping, directrix labels, and the 003 example were
  visually checked. The Task 13G.1B request explicitly authorized formal
  publication after the V2/PF previews had been delivered.
- Architecture boundary tests: **2/2 PASS** via
  `python -m unittest tests.test_rendering_boundaries`.
- Protected assets: **106/106 unchanged** in the before/after SHA-256 audit,
  including Task 13F files, three C001/C002 GIFs, 87 other-UID PNG/GIF files,
  and C051 formal TeX, PDF, and metadata.

## Publisher compatibility

The existing `scripts/zhishu/prepare_knowledge_images.mjs` processed only the
isolated C051 formal `images/` source into an isolated output directory. It
produced `images/C051/001.webp` through `003.webp` with 1080×1440 dimensions.
`verify_prepared_runtime_images` passed its source/output hash and freshness
checks. `map_runtime` returned exactly three unique C051 image assets with
`resources/images/C051/<number>.webp` URIs, no errors, and no warnings. The
worker's independent GIF branch was inspected; GIF source hashes and frozen
code remained unchanged. No app sync, package build, site deployment, or APK
build was performed.

## Reproduction

From `D:\mathnote`:

```powershell
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --validate-only
python -m unittest discover -s 03_conic/C051_parabola_focal_radius_coordinate/static_cards -p test_model.py
python -m unittest tests.test_rendering_boundaries
```

The complete preview builder is
`python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate`.
It requires `--replace-preview` when existing preview contents would change.
The exact preview, source, tool versions, and hashes are recorded in
`.build/static_cards/C051/build_report.json`; formal publication hashes and
backups are under `.build/static_cards/C051/publication_13g1b/`.
The preview report retains its preview-stage status; this manifest records the
separate publication and final freeze gate. Publisher was checked in isolation
with `node scripts/zhishu/prepare_knowledge_images.mjs --jobs
.build/static_cards/C051/publisher_final_jobs.json --output
.build/static_cards/C051/publisher_final_output`.

## Independent follow-up

Some formal C051 TeX calls `p/2` the semilatus rectum for `y²=2px`. Under the
usual terminology the semilatus rectum is `p`, while `p/2` is the focus's
horizontal coordinate. The cards use the correct formula and avoid that term.
The formal knowledge-source wording remains a separate review item.
