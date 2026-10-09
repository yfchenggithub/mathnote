# Task 13G.2B — C043 static cards publication and final freeze

Date: 2026-10-09 (Asia/Shanghai). Status: **TASK 13G.2 FINAL FREEZE — PASS**.
Scope: C043's three reviewed static PNG cards and the common static-card
interfaces exercised by C043 and C051. Task 13G.0A remains **ARCHITECTURE
REVIEW PENDING**; this manifest does not change its review status. No app sync,
APK, website, or other UID publication was performed.

## Formal assets and reviewed preview

UID: `C043`. Formal directory:
`03_conic/C043_hyperbola_abc_relation/images/`. Publication copied the three
approved, isolated previews from `.build/static_cards/C043/`. The formal
directory contained no files before publication. Only these PNGs were placed
there; no SVG, debug image, contact sheet, or report was published. Each formal
file was SHA-256 identical to its preview immediately after publication.

| Card | Formal file | Preview and formal SHA-256 |
| --- | --- | --- |
| 快记 | `001.png` | `f4a09f974c984fccba2fa0a6eda55bbba411aee9b157c1e01b9d5e399574fafb` |
| 快懂 | `002.png` | `eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac` |
| 快用 | `003.png` | `558b584aa4b3d7fac632b980c53f991a4858ed83047bfdaae2152eb8986ef9d2` |

The 002 hash matches the final artifact in
`scripts/static_cards/TASK_13G_2A_2_REPORT.md`, rather than the earlier 13G.2A
version. The existing preview build report's source (7 files), implementation
(8 files), and output (8 files) hashes all matched current bytes. An isolated
rebuild of all three C043 cards produced PNGs with exactly the same hashes.
The preview report still says `VISUAL REVIEW PENDING` because it records the
earlier preview stage; the current publication instruction explicitly confirms
final human acceptance. The three clean PNGs were re-inspected at original
resolution and as a contact sheet. For 002, B is next to the upper-right
auxiliary corner; A, b, c, O, F₂, and x remain distinguishable; the former
plot note is absent; and the bottom panel distinguishes OB from OF₂ and B
from the curve and focus. No blocking clipping or overlap was observed.

All three PNGs decoded at 1080×1440. Their corresponding
`.build/static_cards/C043/001.svg` through `003.svg` parsed as SVG. The SVGs
remain preview-only.

## Mathematics and automatic layout

The UID-local model is
`03_conic/C043_hyperbola_abc_relation/static_cards/model.py`; card drawing,
copy, and semantic label registration are in the adjacent `cards.py`.
The formal six TeX files and `meta.json` were read as knowledge sources and
were not changed. For the horizontal model,
`x²/a² − y²/b² = 1` with `a,b>0`, the checks confirm `c²=a²+b²`, vertices
`(±a,0)`, foci `(±c,0)`, `c>a`, asymptotes `y=±(b/a)x`, and both branches.
Card 002 checks `O=(0,0)`, `A=(a,0)`, `B=(a,b)`, `OA=a`, `AB=b`, and
`OB=c=OF₂` as equal lengths of distinct segments; B is neither a curve point
nor a focus. Card 003 checks `9x²−16y²=144` gives `a=4`, `b=3`, `c=5`,
foci `(±5,0)`, and asymptotes `y=±3x/4`.

- C043 model/content/diagram suite: **7/7 PASS**. `--validate-only` also
  returned 11 named mathematical assertions and content PASS.
- Shared semantic label and failure-behavior suite: **18/18 PASS**.
- C043 002 build report: 18 visible text artists; 8 inside the plot; all 8
  registered; 0 uncovered; 0 collisions. Required labels are A, B, F₂, O,
  a, b, c, and x. Every final measured ink clearance meets its configured
  6 or 7 px minimum. B is 22.63 px from its anchor box, within the 42 px
  point-label maximum; no leader was needed.
- Static/dynamic architecture boundary suite: **2/2 PASS**.

The shared builder entry is `python -m scripts.static_cards.build` with an
exact `--uid` and `--source-dir`. Its output stays under
`.build/static_cards/<UID>/`; `--output` can select a deeper isolated
directory ending in that UID. `--validate-only` does not export images.
Repeated identical previews are accepted; changed previews require
`--replace-preview`. The builder never writes formal `images/`.

`scripts/static_cards/labels.py` exposes `LabelLayout` and `PointLabel`,
`SegmentLabel`, `CurveLabel`, `LineLabel`. Callers register semantic object
names and mathematical anchors; segment labels include an endpoint. The
bounded candidate search measures final renderer text boxes and checks
sampled visible paths, stroke width, point markers, other text, and plot
bounds with pixel clearance. `max_anchor_distance` and wrong-object
proximity enforce association; optional leaders are checked as geometry.
`resolve()` places labels and `finalize()` enumerates visible text in the
declared plot. Unregistered plot text causes `LAYOUT_FAIL`; ink collisions
cause `COLLISION_FAIL`; the builder records failure and does not export a
clean card. Intentional named exceptions remain explicit.

The gate applies to cards declaring a plot `LabelLayout`; it does not migrate
legacy cards automatically. Arbitrary patches and raster ink need geometry
adapters, curve checks depend on rendered path sampling, and automatic checks
do not prove teaching semantics. Human visual review remains required.

## C051, dynamic, and protected-resource regression

C051's `TASK_13G_1_C051_FREEZE.md` baseline was checked before C043
publication. Its model/diagram suite passed **8/8**. An isolated rebuild using
the current shared builder gave byte-identical results against each frozen
formal PNG:

| C051 card | Frozen formal and isolated rebuild SHA-256 |
| --- | --- |
| `001.png` | `b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0` |
| `002.png` | `736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9` |
| `003.png` | `01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313` |

The before/after SHA-256 baseline covered **114 protected files**: 90 other
UID formal image files and 24 dynamic production/source files. None changed
or disappeared. This includes `scripts/manim/`, the C001/C002 Manim sources,
and their three frozen GIFs. The three GIF hashes remained
`30862f60db7297b7d4fc0166c78cd18443c25c5466ce68214c69b46e49483b82`,
`5fdba739039e6d7138d908ee257e219bc262d8cdb4135bf0020fa598b768e840`,
and `1ad4d074699a3d193627bb0cbeadd7fdbedc53e833e8772fd9f0584494f9a5ad`.
The baseline list is in
`.build/static_cards/C043/publication_13g2b/protected_before.json`.
Task 13F was checked by hashes and architecture tests; GIFs were not
rerendered.

## Publisher compatibility

The actual Publisher worker and mapping code were audited. Repository source
discovery found C043 exactly once among 571 conclusions with 0 errors.
The published PNGs were the sole input to an isolated invocation of
`scripts/zhishu/prepare_knowledge_images.mjs` under
`.build/static_cards/C043/publication_13g2b/`. It produced exactly three
decodable 1080×1440 WebP files. `verify_prepared_runtime_images` passed
source/output hashes, contract, freshness, and complete file coverage.
`map_runtime` returned exactly three unique C043 image assets, ordered
001–003, with URIs `resources/images/C043/001.webp` through `003.webp`,
0 errors and 0 warnings. An isolated content package passed
`validate_package`, with 3 image assets, 1 existing PDF asset, 0 errors, and
0 warnings; package hash:
`6724ee1defbe65550141d613744663c259180e1848d64acfacdecafffb505a16`.
The standard package entry succeeded when run outside the execution sandbox.
Within the sandbox, Python's newly created temporary staging directory was
inaccessible; an accessible isolated staging directory also produced a
validated package. This was an execution-environment permission issue; no
Publisher code or formal Publisher output was changed. The worker's GIF branch
was left intact. No knowledge-tree Sync was run.

## Reproduction and freeze boundary

From `D:\mathnote`:

```powershell
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --validate-only
python -m unittest discover -s 03_conic/C043_hyperbola_abc_relation/static_cards -p test_model.py
python -m unittest tests.test_static_label_layout
python -m unittest discover -s 03_conic/C051_parabola_focal_radius_coordinate/static_cards -p test_model.py
python -m unittest tests.test_rendering_boundaries
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --output .build/static_cards/C043/recheck/C043
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --output .build/static_cards/C043/recheck/C051
```

Rebuilt PNGs must be compared by SHA-256 with the tables above; merely
rendering is not a freeze check. Isolated Publisher job JSON, WebP output,
package, and a package probe are under
`.build/static_cards/C043/publication_13g2b/`; that ignored directory is
local evidence, not a formal asset. This freeze records behavior proven by
C051 and C043, while allowing future compatible extensions with explicit
mathematical, layout, visual, and regression checks. It does not redesign the
common API or authorize changes to the separate Manim pipeline.
