# Static card preview builder

The shared code owns layout, exact coordinate mapping, PNG/SVG export, source
hashes, and build reports. Each UID owns its own mathematical model, content
checks, card specifications, and drawings. No animation code is imported.

From the repository root:

```powershell
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --card 002
python -m scripts.static_cards.build --uid C051 --source-dir 03_conic/C051_parabola_focal_radius_coordinate --validate-only
python -m unittest discover -s 03_conic/C051_parabola_focal_radius_coordinate/static_cards -p test_model.py
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --card 002
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --validate-only
python -m unittest discover -s 03_conic/C043_hyperbola_abc_relation/static_cards -p test_model.py
```

Output is restricted to `.build/static_cards/<UID>/`. Repeated builds with
identical output succeed. A changed preview requires `--replace-preview`.
This command never writes formal `images/` or calls the GIF builder. PNGs are
1080×1440; SVGs are kept as vector intermediates. `contact_sheet.png` appears
when all three cards are built. `build_report.json` records source/output hashes,
tool versions, checks, and review status. Human visual review remains required.
UID card modules can supply `REVIEW_STATUS` and `TERMINOLOGY_REVIEW` for the
build report; older modules retain the original report values.

## Semantic diagram labels and collision gate

Create the exact mathematical geometry in a `MathFrame` first. Then create a
`LabelLayout(canvas, frame, (left, top, right, bottom))` using the valid plot
rectangle in card coordinates. Register `PointLabel`, `SegmentLabel`,
`CurveLabel`, or `LineLabel` with content, object name, mathematical anchor,
style, priority, and minimum pixel clearance. Segment labels also need their
second mathematical endpoint. Call `resolve()` after all diagram geometry and
other text is present, before export. Do not draw another diagram obstacle
after `resolve()`. C043 card 002 is the working example.

The layout searches a bounded, deterministic set of point directions or
segment normals. It measures actual text extents, including MathText, with the
final Matplotlib renderer. It checks individual visible path segments, stroke
width, point radius, all other text, and the plot boundary in screen pixels.
`canvas.layout_report` records attempted positions, final pixel boxes, nearest
objects, and measured clearance. `CollisionFailure` aborts export; the builder
writes `render_gate: COLLISION_FAIL` in `build_report.json`. UID modules can
declare `LABEL_GATE_REQUIRED` for cards that must have specific semantic
labels registered. Intentional contacts may be declared with an object's
stable `name` in a label's `exceptions` set; avoid broad exclusions.

For a preview-only bounding-box overlay:

```powershell
python -m scripts.static_cards.build --uid C043 --source-dir 03_conic/C043_hyperbola_abc_relation --card 002 --replace-preview --debug-layout
```

This writes `002_layout_debug.png` alongside the clean PNG and SVG under the
isolated preview directory. The renderer checks registered semantic labels;
existing UID cards are not silently migrated. Geometry expressed as arbitrary
patches or raster images requires an adapter before it can enter this gate.

Dependencies: Python, Matplotlib, Pillow. Chinese typography uses the local
Noto Sans SC font when available and Microsoft YaHei as a fallback.
