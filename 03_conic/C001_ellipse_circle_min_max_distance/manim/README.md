# C001 Manim pilot

## Source and geometry

The authoritative conclusion is in `../01_statement.tex` through `../06_summary.tex`.
This animation illustrates one exact instance:

\[
E:x^2/9+y^2/4=1,\quad M=(4,0),\quad \Gamma:(x-4)^2+y^2=r^2.
\]

For a point on the ellipse, (PM^2=(5/9)x^2-8x+20), whose derivative is negative on
([-3,3]). Thus (d_{\min}=1), (d_{\max}=7),
(D_{\min}=\operatorname{dist}(r,[1,7])), and (D_{\max}=7+r).
`math_model.py` computes every highlighted point, intersection, and distance shown
by `scene.py`; no visual approximation is used to place the intersections.

## Storyboard

1. Establish a fixed blue ellipse and center (M), then grow a red circle from (r=0.5).
2. Show the gold gap shrink to zero at the first tangency (r=1).
3. Keep both true intersections on the moving curves while (1<r<7).
4. Pause at the second tangency (r=7), then show the gap grow for (r>7).
5. A fixed, same scale number line shows why the changing answer is the distance from (r) to ([1,7]).

The moving geometry and number line replace a long verbal explanation of all three
branches of the minimum distance formula. The GIF concentrates on (D_{\min});
the formal TeX also proves (D_{\max}).

## Rebuild on Windows

Prerequisites: Python 3.14 (3.11–3.14 supported by Manim 0.21.0), FFmpeg on PATH,
and a TeX installation with `latex` and `dvisvgm`. `Microsoft YaHei` is used for
Chinese labels; change `FONT` in `scene.py` if unavailable. This pilot was verified
with Python 3.14.3, Manim Community 0.21.0, TeX Live 2025 and the installed FFmpeg.

From the repository root:

```powershell
python -m venv .venv-manim
.\.venv-manim\Scripts\python.exe -m pip install -r .\scripts\manim\requirements.txt
python -m unittest discover -s .\03_conic\C001_ellipse_circle_min_max_distance\manim -p test_math_model.py
.\scripts\manim\render.ps1 -Uid C001
.\scripts\manim\export_gif.ps1 -Uid C001
```

The MP4 is `build/manim/C001/C001_distance.mp4` (intermediate). The final GIF is
`../images/ellipse_circle_distance.gif`. `export_gif.ps1 -Rebuild` renders again.
The script validates GIF dimensions, timing, distinct frames, and infinite loop
before copying it into `images/`. It never cleans formal TeX, PDF, or old images.

The existing Zhishu asset preparation pipeline discovers `.gif` files in `images/`,
validates them and copies them byte for byte. No Publisher or Sync run is part of
this pilot.
