# Task 13G.2A — static label layout and collision gate

Status: **TASK 13G.2A — VISUAL REVIEW PENDING** (2026-10-09, Asia/Shanghai).
Scope: common static-card tooling and C043 card 002 only. No formal publication.

## Pre-flight and cause

Read root `AGENTS.md`, the math-rendering architecture contract, static-card
README and canvas, C043 cards, C051 freeze manifest and tests, build code, and
the rendering-boundary test. The working tree already had two uncommitted
C043 002 label-offset edits (`A` and `b`); these were preserved as context
and replaced by semantic auto-placement in this task.

Previously, `MathFrame.point` accepted fixed `dx,dy` and other diagram labels
were placed with fixed canvas coordinates. `CardCanvas.export` checked only
whether text left the card canvas. C051's test checked only named directrix,
P, and PF relations in cards 001/002; C043's test checked panel edges and one
card-001 focus label. Neither test audited every label against every visible
diagram path, marker, other label, and panel boundary. Thus an output could
render successfully while A or b touched geometry. C051's earlier PF repair
was likewise caught only by its later, targeted clearance check.

## Implementation

`labels.py` provides PointLabel, SegmentLabel, CurveLabel, LineLabel, a
deterministic `LabelLayout`, pixel-distance collision checks, a typed failure,
and an optional preview debug overlay. Every semantic label stores content,
mathematical object name and anchor, candidates, style, priority, minimum
clearance, and explicit object-name exceptions. Segment labels also store the
second mathematical endpoint. Point candidates cover eight directions at
bounded distances; segment candidates use the midpoint and both unit normals.
Text is measured by Matplotlib's actual renderer, including MathText, at the
same DPI as the exported card. Path checks use visible polyline segments rather
than a whole-curve bounding box. Point markers include their radius; line
checks include stroke width. Final positions are audited after all labels are
placed. The builder writes `render_gate: COLLISION_FAIL` and attempted positions
to its report if placement fails, and does not export a clean card. C043 002
declares all eight diagram labels as required, so missing registration also
fails the build.

The model, O/A/B/F₂ coordinates, hyperbola, rectangle, asymptotes, OA/AB/OB,
and teaching copy remain unchanged. C043 cards 001/003 were not rebuilt or
modified. The final preview outputs are:

- `.build/static_cards/C043/002.png` — SHA-256 `0b5f9993133cbf2f0b45b6d0875ac6b1b621a6ef467a40650cb97618d4dc85bb`
- `.build/static_cards/C043/002.svg` — SHA-256 `130663c4de45253defddd7944ddc35ab95c986a24ffe99479cb407f30a1e95fa`
- `.build/static_cards/C043/002_layout_debug.png` — preview-only red text boxes
- `.build/static_cards/C043/build_report.json` — candidates, pixel boxes, clearance, hashes, and gates

## Measured label clearance (final pixels)

The clearance includes the distance from the actual text box to nearby ink or
the plot boundary, after stroke/marker thickness. Required clearance is 7 px
for mathematical labels and 6 px for the axis label.

| Label | Chosen candidate | Nearest object | Actual / required |
| --- | --- | --- | --- |
| A | NE, 16 px | hyperbola right branch | 8.32 / 7 px |
| B | SE, 52 px | hyperbola right branch | 12.35 / 7 px |
| F₂ | NE, 16 px | point F₂ | 13.24 / 7 px |
| O | N, 38 px | OB | 9.53 / 7 px |
| b | normal+, 30 px | OB | 13.56 / 7 px |
| a | normal+, 30 px | OA | 9.53 / 7 px |
| c | normal+, 30 px | OB | 9.47 / 7 px |
| x | NE, 12 px | x axis | 10.81 / 6 px |

The C043 test also reconstructs A's former unsafe location (collides with
the hyperbola and rectangle edge) and b centred on AB (collides with AB).
The new positions are selected without moving mathematical geometry.

## Executed checks

- Common layout tests: **11/11 PASS**. Horizontal, vertical, slanted,
  curve-near-point, axes-origin, close labels, blocked candidates, impossible
  layout, actual ink collision, label types, and builder failure status.
- C043 mathematical/content and diagram tests: **7/7 PASS**.
- C051 mathematical and diagram tests: **8/8 PASS**.
- Static/dynamic rendering boundary tests: **2/2 PASS**.
- C051 isolated rebuild: three PNGs match the three formal frozen PNGs
  byte-for-byte and match freeze SHA-256 values. The formal C051 files were
  not written.
- `git diff --name-only -- scripts/manim .../C043.../images .../C051.../images`
  returned no changes. Task 13F dynamic sources and GIFs were not modified.

## Limits

The gate applies to semantic labels registered by a card; existing UID cards
are not automatically migrated. Visible Matplotlib line paths and Circle/line
markers are supported. Arbitrary patches or raster image ink need an explicit
geometry adapter. Curves are checked from their rendered sampled paths, so
sampling density must remain adequate. Dashed lines are conservatively checked
as continuous paths. The search has bounded candidates and reports failure
when no candidate fits; it does not expand the panel or shrink the main label
font. Human visual review of the clean PNG remains required before any freeze
or publication.
