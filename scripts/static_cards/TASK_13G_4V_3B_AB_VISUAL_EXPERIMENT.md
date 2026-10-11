# Task 13G.4V.3B — C043-002 Blue / Rose Premium A/B

**Status: `TASK 13G.4V.3B — VISUAL A/B SELECTION PENDING`**

## 1. Pre-flight and reference

- Scope: C043-002 only. Read `AGENTS.md`, static rendering architecture, static card README, C043 freeze report, Style Lab selection report, Style A three-card report, 3A polish report, current component/drawing code and C043 model/tests. The architecture contract remains REVIEW PENDING; this experiment uses only isolated previews.
- Initial working tree was clean. Formal C043/C051 PNGs, selected Style A-002, and current 3A polished 002 matched their expected SHA-256 values before and after rendering. The eight protected digests are recorded in `build_report.json`.
- The rose C++ card was visible as the user's inline attachment in this conversation; no separate local image file was identified or needed. Observed features: rose index block and title, pale background, slim rounded panel borders, colored section capsules, a large explanatory visual, and a substantial bottom memory panel. Its C++ text and diagram were not used as math content.
- Comparison baseline: `.build/static_cards_style_a_polish/C043/002.png` (latest 3A), SHA-256 `3588a70376964804a40e2f08aeff6f523b22a52b7595bced6b83b265a95b9223`. The originally selected Style A-002 remains SHA-256 `997b137ebc44b874134ad26e4591e851d9156a29d55ea7db869524101137c522`.

## 2. Shared premium layout and theme variables

One `card_002()` builds both candidates. The `Theme` values change only brand colors: page/outer border, gradient title, capsule, pale panel, and memory panel. Canvas size, panel boxes, corner radii, title positions and fonts, formulas, content order, the yellow formula chip, and all mathematical curves/points/labels are shared.

The new visual components are a fine outer border, distinct white UID/number badges within the gradient masthead, wider colored section capsules, consistent narrow panel outlines, and a full-height memory panel. The construction reuses the existing C043 3A `hyperbola_diagram()` and frozen `Hyperbola(3, 4)` model. The curve and semantic parameter colors remain blue for *a*, teal for *b*, amber for *c* in both candidates.

| Theme | Title gradient | Section capsule | Pale panel | Memory panel |
| --- | --- | --- | --- | --- |
| A Blue Premium | `#115DAE → #2686D5` | `#176DB8` | `#EEF7FF` | `#E7F4FF` |
| B Rose Premium | `#BB2857 → #E84F80` | `#C52C5C` | `#FFF0F5` | `#FCEAF0` |

## 3. Previews and comparison

All outputs are isolated in `.build/static_cards_ab_experiment/C043/`:

- `A_blue/002.png`, `A_blue/002.svg`, `A_blue/002_mobile_360.png`, `A_blue/002_mobile_390.png`
- `B_rose/002.png`, `B_rose/002.svg`, `B_rose/002_mobile_360.png`, `B_rose/002_mobile_390.png`
- `ab_comparison.png`: same-scale A/B; `ab_mobile_comparison.png`: 360px A/B; `style_a_original_vs_blue_vs_rose.png`: current 3A vs new blue vs new rose.
- `build_report.json`: exact hashes, mathematical results, typography and consistency checks.

The three-way sheet shows the new capsule system, outer border and memory block against the current Style A. The current green relation module gives the relation a different semantic accent; the new candidates unify the module treatment with their brand hue. The two new cards are directly comparable because their content and geometry are identical. Rose has a stronger warm brand impression; blue retains the current Zhishu blue identity. Which feels better over repeated mobile reading requires the user's visual choice.

## 4. Math and visual gates

| Gate | Result and evidence |
| --- | --- |
| Formal/model mathematics | **PASS**: 11 `validation_results()` checks and formal source checks via existing C043 3A validator. C043 model suite: **7 tests passed**. |
| A/B content/layout/geometry | **PASS**: text layout SHA-256 `e9ecf1d70b52fbf9f226067ef5aa1052972bbb0ac39661d897ea604b87c4d65f`, named mathematical paths/points, auxiliary triangle and their colors `6ba094f13eea44ea585ac0fdedebec787a33bd37174fcccc85879a2c149e39ce`, and label placements `9c0b163ffc0dd1fd61b4087738f2d1333c06fa595fbf4a5e3e8cfb698f4e0fe2` match across A/B. |
| Diagram labels | **PASS**: seven registered labels O, A, B, F₂, a, b, c; one exempt diagram section title; no detected label collisions or uncovered plot text. B remains the auxiliary rectangle corner, off the curve and distinct from F₂. |
| Text | **PASS**: 21 visible text artists per card; no detected text overlap or out-of-canvas text. Existing 3A polish suite: **5 tests passed**. |
| Export | **PASS**: both 1080×1440 PNGs decode; both SVGs parse; 360px and 390px previews and all three contact sheets generated. |
| Mobile | **PASS for generated 360px inspection**: title, key relation, diagram labels and two-line memory are readable in the reviewed contact sheet. Minimum measured essential text bounding-box height at 360px is 14.17px. Physical Android device review was not performed. |
| Contrast | **PASS for checked pairs**: white on the title gradient at the small heading's vertical position is 5.43:1 (blue) / 4.94:1 (rose); white on capsule is 5.36:1 / 5.40:1; memory ink on memory fill is 7.65:1 / 7.95:1; core formula ink on yellow is 13.05:1. The large white title at its lower gradient position is 4.30:1 / 3.96:1. |
| Freeze regression | **PASS**: the six formal C043/C051 PNG hashes and two Style A baseline hashes were identical before and after. No Publisher, Sync, APK, formal images, TeX, PDF, `meta.json`, or other UID was edited. |

The diagram does not draw asymptote lines, matching the existing 3A diagram. The model suite checks asymptotic behavior, but this experiment has no visual asymptote-line gate. Automated text checks cover text boxes, not all decorative patch-to-patch intersections; the rendered sheets were also inspected manually. No Android device claim is made.

## 5. Cost, files and selection

- New implementation: 326 Python lines in C043-private `cards.py` and `build.py`; one shared layout, two theme parameter sets, existing mathematical drawing reused. Measured final render/build time: **4.32 s** on this workstation.
- New report: this file. No existing source file was changed. Generated artifacts are in the ignored `.build` experiment directory.
- Potentially reusable component choices: slim panel borders, modest section capsules, separated UID/index badges, and a full-size memory block. Their wider adoption is a separate decision.

**User decision pending:** compare the two A/B sheets and 360px sheet, then choose **A Blue Premium**, **B Rose Premium**, or retain the current Style A polish. No candidate is frozen or published by this task.
