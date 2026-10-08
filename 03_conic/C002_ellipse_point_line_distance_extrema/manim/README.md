# C002 ellipse point-to-line distance animation (Task 13E)

## Formal mathematics audit

The six authoritative TeX sections and `meta.json` agree on the result. For
`E: x²/a²+y²/b²=1` with `a>b>0`, `l: Ax+By+C=0` with `(A,B)≠(0,0)`, and
`R=√(a²A²+b²B²)`, the distance extrema over the ellipse are

    d_min = max(0, (|C|-R)/√(A²+B²))
    d_max = (|C|+R)/√(A²+B²).

The line is separate, tangent, or secant according as `|C|` is greater than,
equal to, or less than `R`. The normal support points are
`P±=±(a²A/R,b²B/R)`. No blocking contradiction was found in the formal
content. The animation does not change the TeX, PDF, PNGs, or metadata.

## Animation decision and storyboard

The difficult step is seeing why the **minimum** changes formula at tangency
while the **maximum** continues to come from a support point. The example is
`E:x²/4+y²=1`, `l_C:3x+4y+C=0`, `C≥0`. Here `R=2√13≈7.21`, and the two
support points stay fixed as the red line slides along its normal. Gold marks
the near support point and, while separate, its perpendicular gap to the line.
Purple marks the far support point and its perpendicular distance. Teal dots
are exact ellipse-line intersections.

1. Start at `C=10>R`: the gold gap is positive; the purple segment is longer.
2. Move continuously to `C=R`: the gold gap contracts to zero at tangency.
3. Move through `C=2` to `C=0`: two actual intersections appear; the minimum
   remains zero while the purple far distance keeps changing.
4. Slide back to `C=10` to restore the opening composition for looping.

The changing line, feet, intersections, and displayed values all use
`math_model.state(C)`. The formulas at the bottom use `C` in place of `|C|`
because this demonstration explicitly restricts `C≥0`; the formal statement
covers either sign.

The GIF replaces a long spoken classification of the three cases. Its main
teaching picture is the moving line with two fixed support points, and the
creation of actual intersection dots when the gap disappears. A static frame
cannot show the continuous transition as directly.

## Rebuild and review

From the repository root, using the existing `.venv-manim` environment:

```powershell
.\03_conic\C002_ellipse_point_line_distance_extrema\manim\build.ps1
.\.venv-manim\Scripts\python.exe -B .\03_conic\C002_ellipse_point_line_distance_extrema\manim\qa.py
```

The build runs C002 mathematical tests, renders with Manim at 576×1024 and
24 FPS, exports an infinite-loop 12 FPS GIF with FFmpeg's `palettegen` and
`paletteuse`, and runs the shared GIF technical validator. Intermediate MP4:
`build/manim/C002/C002_ellipse_line_distance.mp4`. Formal source asset:
`../images/ellipse_line_distance.gif`. The QA script decodes every GIF frame
and writes `build/manim/C002/C002_13E_contact_sheet.png` and
`C002_13E_visual_report.json`, plus four full-size representative frames.

The shared render/export scripts remain untouched. This UID-specific script
avoids their existing C001-specific scene and output names. Current Zhishu
runtime image preparation discovers direct `.gif` files under the conclusion's
`images/`, validates frame timing and loop information, and copies them
byte-for-byte to its prepared image mirror. No Publisher, Sync, or package
build is part of this task.
