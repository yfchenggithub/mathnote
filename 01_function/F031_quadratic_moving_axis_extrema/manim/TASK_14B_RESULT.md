# Task 14B Result — F031

Date: 2026-10-09. Scope: one independent F031 mathematical animation.
Status: CODE PASS / MATH PASS / RENDER PASS / LOCAL VISUAL PASS /
USER VISUAL PENDING / DEVICE PENDING. This is not FINAL FREEZE.

## 1. Pre-flight

The worktree was clean at task start. Task 13F freeze and shared README were
read. The frozen check_env.ps1 passed with Python 3.14.3, Manim 0.21.0,
Pillow 12.3.0, FFmpeg, TeX and dvisvgm available. A SHA-256 baseline for
5,709 pre-existing formal TeX/PDF/JSON, C001/C002 protected assets/source,
and shared scripts was saved at build/manim/F031/14B/freeze_baseline.json.

## 2. Actual UID Directory

The shared exact-UID discovery rule located a single directory:
01_function/F031_quadratic_moving_axis_extrema/. Its meta.json title is
“二次函数在定区间上的最值（对称轴变动）”. The existing images/ was empty;
the formal PDF already existed in pdfs/. No new knowledge ID was created.

## 3. Official Mathematics Audit

All six formal TeX sections and meta.json were read before modeling.
The source studies f(x)=ax²+bx+c with a≠0 on a fixed [m,n], m<n; the
axis x₀=-b/(2a) may change with parameters. It treats both openings and
both extrema. For a>0, the point nearest the axis takes the minimum and
the farthest endpoint takes the maximum; for a<0 the roles reverse.
The nearest point changes rule at m and n. The farthest endpoint changes
at (m+n)/2 and BOTH endpoints tie there. At x₀=m or n, the vertex is
that endpoint, so the nearest-point extremum is unique.

The formal formulas report extreme VALUES. Their single endpoint branch
at the midpoint is valid for the value but does not enumerate all points
attaining it; the animation correctly marks both. The metadata field
math.core_formula presents the a>0 minimum formula without a local
qualifier, although math.conclusions and the TeX include a<0. This
pre-existing scope ambiguity was not edited and does not block the
explicitly labeled example. interactive.has_diagram is true despite
no pre-existing local static image. No formal source was modified.

## 4. Animation Value Assessment

Static snapshots can show separate cases. The continuous scene shows
why the green nearest point follows the vertex only while it lies
inside the interval, while the orange farthest endpoint switches
DISCONTINUOUSLY at the midpoint. Two live endpoint-distance bars
make the cause of the orange switch visible. A separate downward
snapshot changes the min/max roles without passing through a=0.

## 5. Mathematical Model

math_model.py defines the valid subfamily f_h(x)=a(x-h)²+k:
b=-2ah, c=ah²+k. The interval, a and k remain fixed while h moves.
The state includes the vertex, both endpoint values, extreme values,
and tuples of ALL attaining points. The primary calculation classifies
by distance to h. An independent candidate method evaluates the
expanded polynomial at both endpoints and any interior stationary point.
Tie tolerance was separated from the looser cross-method numeric
comparison after a boundary test exposed false near-ties.

## 6. Teaching Storyboard

The UID-local README records the storyboard. The plotted interval is
shaded; its blue curve is emphasized and the outside curve muted.
Purple is the moving axis/vertex, green the minimum points, orange
the maximum points, and blue bars the endpoint distances. The scene
passes the left endpoint, midpoint tie, right endpoint, and outside
states in order; the closing downward snapshot reverses the roles.
The opening is restored for the GIF loop.

## 7. Demonstration Parameters

The main sweep uses [L,R]=[-2,2], a=1/4, k=0, and h from -2.8 to 2.8.
Thus the distinct thresholds L=-2, midpoint 0 and R=2 are easy to
identify. The closing snapshot uses a=-1/4, k=3, h=0; its two minimum
endpoints equal 2 and its maximum vertex equals 3. These are examples
of the formal theorem, not a claim that every parameterized quadratic
merely translates.

## 8. Manim Implementation

scene.py defines one direct Scene subclass, F031MovingAxisLesson.
One ValueTracker drives the curve, axis, vertex, point markers, distance
bars and numbers through QuadraticSpec. The midpoint draws two orange
markers; it never animates a maximum point across the interval. The
downward state is a separate discrete switch, so no invalid a=0 scene
is displayed. The frozen shared scripts were used without edits.

## 9. Mathematical Tests

Running test_math_model.py produced 7 passing unittest cases. They cover
seven axis regions for each opening, the three thresholds and both
sides of each, midpoint ties, endpoint uniqueness, outside vertices,
and 300 deterministic random parameter cases. The candidate-value
method independently agrees with the distance-classification method.
Source and rendered color-marker checks are independent enough to
detect wrong plotted point positions or missing midpoint markers.

## 10. MP4 / GIF Export

Frozen render.ps1 produced build/manim/F031/moving_axis/moving_axis.mp4:
576×1024, 24 FPS, 377 frames, 15.708 seconds (ffprobe). Frozen
export_gif.ps1 produced the staged GIF and then safely published a
NEW file, without -Overwrite:
01_function/F031_quadratic_moving_axis_extrema/images/
f031_moving_axis_extrema.gif. Staging and formal SHA-256 match:
DDCEB56C4DBF4C42C3223FF1E932ACB9D78C6DE2F9F0FE91BF7E3390F998AEED.
No existing formal GIF was overwritten.

## 11. Critical State Validation

Real GIF frames at approximately 0.33, 2.42, 3.83, 5.67, 7.42, 9.08,
10.33, 13.67 and 15.42 seconds appear in the contact sheet under
build/manim/F031/14B/. They show left outside, h=L, inside left,
midpoint tie, inside right, h=R, right outside, downward tie and loop
return. At h=0 in the upward case, both orange endpoints appear,
the green point is at the vertex, and both blue distance bars agree.
At h=0 in the downward case, the green endpoints tie and the orange
vertex is unique.

## 12. Visual Validation

The first render failed in a FadeOut of a dynamically reconstructed
group; scene-specific transition usage was fixed without touching
shared tools. A subsequent contact sheet exposed a blue filled wedge:
the curve transparency call changed fill as well as stroke. The scene
now changes stroke opacity only; the corrected final contact sheet and
full-size midpoint/downward frames were inspected. No observed
overlap, cropping, black frame or mathematical color-role reversal
remains. The main mathematical graphic occupies most of the chart,
and text and labels are legible at 576×1024.

qa_frames.py decoded all 188 FINAL formal GIF frames, recorded 174
distinct frames and 180 changed adjacent pairs, and found no black
frame. It checked green/orange graph-marker positions against the
independent timeline and model on 171 frames with zero failures;
17 transition or frame-timing-boundary frames were still decoded and
covered by contact/visual inspection. The first/last mean RGB
difference is 1.093/255, consistent with a gentle loop.
Evidence: build/manim/F031/14B/F031_14B_contact_sheet.png and
F031_14B_visual_report.json.

## 13. GIF Technical Validation

verify_gif.py passed on the formal file: GIF89a, 576×1024, 188 frames,
174 distinct, 15.66 seconds, 80–90 ms frame delays, infinite loop,
zero black frames, complete decode, 3,545,345 bytes (3.38 MiB).
The output contains continuous curve and marker motion, not a
slideshow of static cards.

## 14. Resource Integration Audit

The name f031_moving_axis_extrema.gif did not previously exist in
F031 images/ and has no PNG/WebP name collision. An isolated direct
run of the existing Zhishu runtime-image preparation worker used
only F031 and output to build/manim/F031/14B/resource-preview/.
Its manifest maps the source to
images/F031/f031_moving_axis_extrema.gif, reports 188 frames, and
the copied GIF hash equals the formal source. The worker discovers
direct GIFs from the UID images/ directory; no registry entry is
needed for this asset. No formal Publisher, package update or Sync ran.

## 15. Freeze Integrity

After publication, all 5,709 baseline files were rehashed:
zero changed and zero missing. The result is saved at
build/manim/F031/14B/freeze_integrity.json. This covers the F031
pre-existing TeX, PDF, meta.json, C001/C002 protected files and
Task 13F shared tools. Only the new F031 UID-local source/asset and
ignored F031 build evidence were created.

## 16. Files Changed

- 01_function/F031_quadratic_moving_axis_extrema/manim/math_model.py
- 01_function/F031_quadratic_moving_axis_extrema/manim/test_math_model.py
- 01_function/F031_quadratic_moving_axis_extrema/manim/scene.py
- 01_function/F031_quadratic_moving_axis_extrema/manim/qa_frames.py
- 01_function/F031_quadratic_moving_axis_extrema/manim/README.md
- 01_function/F031_quadratic_moving_axis_extrema/manim/TASK_14B_RESULT.md
- 01_function/F031_quadratic_moving_axis_extrema/images/f031_moving_axis_extrema.gif

Ignored, reproducible evidence and MP4 are under build/manim/F031/.

## 17. Known Issues

The existing metadata core_formula lacks a local a>0 qualifier; formal
TeX and the broader metadata conclusion supply the scope. The user
has not yet visually accepted the GIF, and no Android device test has
been performed. The downward case is a short comparison snapshot;
the full moving-axis sweep is upward-opening, deliberately keeping
one GIF focused on the two distinct switching thresholds.

## 18. Final Status

| Gate | Status | Evidence |
|---|---|---|
| A Source alignment | PASS | Six formal TeX files and metadata audited; explicit subfamily |
| B Mathematical model | PASS | Independent candidate method; seven tests |
| C Teaching design | PASS | Distinct endpoint/midpoint role; UID-local storyboard |
| D Manim implementation | PASS | UID-local Scene and shared ValueTracker state |
| E Rendering | PASS | MP4 and final GIF produced |
| F Local visual validation | PASS | Corrected contact sheet, full-size frames, all-frame decode and marker checks |
| G Infrastructure freeze | PASS | Shared scripts unchanged; isolated UID/Scene output |
| H Resource compatibility | PASS | Isolated F031 worker preview and identical GIF hash |
| I Frozen assets | PASS | 5,709 unchanged hashes |
| User visual acceptance | PENDING | Await user review of formal GIF |
| Android device acceptance | PENDING | Not performed |

CODE PASS / MATH PASS / RENDER PASS / LOCAL VISUAL PASS /
USER VISUAL PENDING / DEVICE PENDING. F031 is ready for user review;
it is not FINAL FREEZE.
