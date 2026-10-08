# C001 Manim teaching animation

## Mathematical source

The authoritative conclusion is in `../01_statement.tex` through
`../06_summary.tex`. This GIF illustrates one instance, with **circle circumference**
rather than the filled disk:

$$
E:\frac{x^2}{9}+\frac{y^2}{4}=1,\qquad
M=(4,0),\qquad \Gamma:(x-4)^2+y^2=r^2\quad(r>0).
$$

For a point on this ellipse, $PM^2=(5/9)x^2-8x+20$. Its derivative is negative
for $-3\le x\le3$. Consequently $A=(3,0)$ is nearest to $M$, with $MA=1$,
and $B=(-3,0)$ is farthest, with $MB=7$. These endpoint locations are specific
to this example; they are not a general ellipse rule.

For this example, $D_{\min}=\operatorname{dist}(r,[1,7])$. Here
$\operatorname{dist}(r,[1,7])=\min_{t\in[1,7]}|r-t|$ means the ordinary distance
from a real number to the closed interval. The general C001 formula is
$D_{\min}=\operatorname{dist}(r,[d_{\min},d_{\max}])$. The GIF focuses on the
minimum; the formal TeX also proves $D_{\max}=d_{\max}+r$.

`math_model.py` independently computes all highlighted points, true
intersections and displayed distances. The scene uses its results rather than
placing intersection markers by eye.

## Storyboard and visual meaning

1. The full ellipse and exact model are visible. Short constructions mark
   $A$, $B$, $MA=1$ and $MB=7$ to explain the green interval $[1,7]$.
2. A red circumference grows continuously from $r=0.5$. A gold segment between
   its nearest point and the ellipse shrinks. The gold number-line segment has
   the same mathematical length, shown on the number-line scale.
3. At $r=1$, the curves touch at $(3,0)$; the tangent point is briefly ringed.
   For $1<r<7$, gold dots are actual intersections, so $D_{\min}=0$.
4. At $r=7$, the curves touch at $(-3,0)$. Beyond $7$, the gold geometric and
   number-line gaps grow again.
5. The changing geometry fades out to the same static composition used at the
   start, reducing the GIF loop jump.

The large red circumference is kept at a true uniform scale. Only the part in
the middle geometry viewport is visible; the header and conclusion cover arcs
outside that viewport.

## Rebuild on Windows

Prerequisites: Python 3.14 (Manim 0.21.0 supports Python 3.11–3.14), FFmpeg on
PATH, and TeX with `latex` and `dvisvgm`. The scene uses `Microsoft YaHei` for
Chinese labels. This pilot was verified with Python 3.14.3, Manim Community
0.21.0, TeX Live 2025 and the installed FFmpeg.

From the repository root:

```powershell
python -m venv .venv-manim
.\.venv-manim\Scripts\python.exe -m pip install -r .\scripts\manim\requirements.txt
python -B -m unittest discover -s .\03_conic\C001_ellipse_circle_min_max_distance\manim -p test_math_model.py
.\scripts\manim\render.ps1 -Uid C001
.\scripts\manim\export_gif.ps1 -Uid C001
```

The intermediate MP4 is `build/manim/C001/C001_distance.mp4`. The final GIF is
`../images/ellipse_circle_distance.gif`. The export script validates frame
count, distinct motion frames, timing, size and infinite loop before copying
the GIF into `images/`. `-Rebuild` on the export script renders the MP4 again.

Visual QA artifacts from Task 13B.1 are under `build/manim/C001/`, including
`C001_13B1_contact_sheet.png` and `C001_13B1_before_after.png`. The build folder
is ignored by Git; regenerate those review artifacts when needed. The existing
Zhishu asset preparation pipeline accepts `.gif`, validates it and copies it
byte for byte. Publisher and Sync are outside this pilot.
