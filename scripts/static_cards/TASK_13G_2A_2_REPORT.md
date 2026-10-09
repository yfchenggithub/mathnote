# Task 13G.2A.2 — label coverage and semantic association

Status: **VISUAL REVIEW PENDING** (2026-10-09, Asia/Shanghai). The clean card
remains an isolated preview; nothing was published to formal `images/`.

## Cause and correction

The prior gate only audited labels passed to `LabelLayout`. The plain
Matplotlib text “辅助矩形角点不在曲线上” was therefore not registered and crossed an
asymptote. The prior point search tried all offsets in one direction before
trying the next direction, which placed B 52 px to the lower right of its
auxiliary corner despite closer safe directions.

The builder now finalizes the layout after every text artist has been drawn.
For a card with plot bounds, it enumerates **all visible Matplotlib text**,
marks each as registered, explicitly exempt, or outside the plot, and checks
every in-plot text against paths, markers, other text, and the plot boundary.
An uncovered text blocks Rendering PASS with `LAYOUT_FAIL`; an ink collision
blocks it with `COLLISION_FAIL`. Explicitly exempt text remains subject to
collision detection. `build_report.json` includes `text_coverage` and
`uncovered_text`.

Point candidate search now tests shorter offsets first, enforces a measured
maximum anchor-to-text distance, and rejects a label that is substantially
closer to another object than to its own point. Segment labels name their
actual line object. An optional short leader is checked against visible
geometry and labels; a leader that cannot be drawn safely yields
`LAYOUT_FAIL`. Mathematical object positions are unchanged.

C043 002 removes the plot note. Its meaning now appears in the bottom panel,
which states `OA=a, AB=b, OB=c`; OB and OF₂ are equal in length but distinct
segments; and B is a rectangle corner, not on the hyperbola and not a focus.
MathText is used for the subscript ₂ because the local Chinese font lacks
that Unicode glyph.

## Final coverage and association

- Visible text artists: **18**; in plot: **8**; registered plot labels: **8**;
  uncovered plot text: **0**; in-plot text collisions: **0**.
- B is placed **NW**, 22.63 px from the actual point anchor to its text box
  (42 px maximum), without a leader. Its closest ink clearance is 14.61 px
  against a rectangle edge (7 px minimum).
- All eight semantic labels meet their configured anchor distances and ink
  clearances. Per-candidate details and measured boxes are in
  `.build/static_cards/C043/build_report.json`.

## Artifacts

| Isolated artifact | SHA-256 |
| --- | --- |
| `.build/static_cards/C043/002.png` | `eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac` |
| `.build/static_cards/C043/002.svg` | `9c6e5d9af2f3178226cae3eb8004c9e3d46bbaeaf2f5eff17982f5fabe03566c` |
| `.build/static_cards/C043/002_layout_debug.png` | `6cd81ca90a1b5c53951930f4e456fd2fd31653aada7cb7a5ff060b0b08d11900` |

The debug image shows red measured text boxes and is preview-only. The clean
PNG and SVG contain no debug marks.

## Executed checks

- Common layout tests: **18/18 PASS**, including ordinary text crossing a
  curve/asymptote, unregistered text, wrong-object proximity, excessive anchor
  distance, safe/unsafe leader lines, impossible layout, and builder failure
  reports.
- C043 math/content/diagram tests: **7/7 PASS**, including plot text coverage,
  B association, and clearance.
- C051 math/diagram tests: **8/8 PASS**.
- Static/dynamic rendering boundary tests: **2/2 PASS**.
- Isolated C051 rebuild: PNGs 001/002/003 each match the corresponding formal
  frozen PNG byte-for-byte. Their SHA-256 values remain respectively
  `b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0`,
  `736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9`,
  and `01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313`.
- No changed files under `scripts/manim/` or either UID's formal `images/`.
  C043 cards 001 and 003 were not modified or rebuilt.

## Remaining limits

The plot coverage gate requires a declared `LabelLayout` and bounds. Legacy
cards without that declaration are not automatically migrated. Paths are
checked at their rendered sampling density, and arbitrary patches or raster
ink still need geometry adapters. A semantic label can deliberately use a
leader only if its complete path stays clear; the gate does not enlarge the
panel or shrink the main text to rescue an impossible layout. Human review of
the new C043 card is still required before any freeze or publication.
