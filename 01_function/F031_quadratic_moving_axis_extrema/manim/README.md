# F031 independent animation — Task 14B

## Formal mathematics audit

The formal source is the six neighboring section TeX files and meta.json.
It studies f(x)=ax²+bx+c, a≠0, on a fixed closed interval [m,n], m<n;
the axis x₀=-b/(2a) varies with parameters. Both openings and both extrema
are in scope. The statement's formulas give extremal VALUES, selecting a
single endpoint formula at the midpoint; they do not list every POINT
attaining an extremum. At x₀=(m+n)/2, both endpoints attain the maximum
if a>0, or the minimum if a<0. At x₀=m or n, the vertex and endpoint
are the same point, so the nearest-axis extremum is unique.

The metadata math.core_formula is the a>0 minimum formula without a
qualifier in that field. math.conclusions and the formal TeX do give the
a<0 case. This is a scope ambiguity, not a reason to use the first formula
for a<0. interactive.has_diagram is true although no local static image
exists. Neither field is edited in this animation task.

## Chosen subfamily and independent model

f_h(x)=a(x-h)²+k, with fixed a,k,[L,R] and moving h, is a valid subfamily:
b=-2ah, c=ah²+k, x₀=h. It illustrates axis movement but is not a claim
that every parametric quadratic changes only its axis. The main scene uses
L=-2, R=2, a=1/4, k=0 and moves h from -2.8 through L, midpoint 0, and
R to 2.8. A short separate closing snapshot uses a=-1/4, k=3, h=0 to
show the min/max role exchange without passing through forbidden a=0.

math_model.py returns tuples of ALL minimum and maximum points. The primary
method classifies the closest interval point and farthest endpoints by
distance to h; candidate_extrema independently evaluates the expanded
polynomial at L, R, and any interior stationary point. test_math_model.py
covers seven axis regions for both openings, each threshold and its two
sides, midpoint ties, endpoint uniqueness, outside vertices, and 300
deterministic random parameter cases.

## Teaching storyboard

1. Establish the fixed highlighted interval and moving axis. The blue
   curve outside [L,R] is muted. Purple identifies the axis and vertex;
   green and orange identify minimum and maximum POINTS.
2. Move h from outside left to L: the green point stays on L; at h=L
   the vertex enters the interval. Continue inward: green follows it.
3. Show distances from the axis to the two endpoints as separate bars.
   At h=0 their lengths become equal, and BOTH orange endpoint markers
   appear. Crossing 0 switches the farthest endpoint.
4. Continue to R and outside right: green follows the vertex until h=R,
   then remains at R.
5. Briefly show a downward-opening curve at h=0: the nearest point is
   now the maximum point, and both endpoints are minimum points. The
   persistent L, m, R labels and the separate crossing captions show
   the three distinct thresholds before the scene returns to its opening.

All moving geometry and numeric readouts use the same h tracker and
QuadraticSpec. The farthest endpoint marker switches discontinuously at
the midpoint, as the mathematics requires; it never glides between
endpoints. Animated numbers are illustrations, while categorical state
and exact midpoint equality come from the model.

## Build

Run from repository root with the frozen shared tools:

    python -B 01_function/F031_quadratic_moving_axis_extrema/manim/test_math_model.py
    .\scripts\manim\render.ps1 -Uid F031 -Scene F031MovingAxisLesson -SceneFile scene.py -Name moving_axis -BuildRoot build/manim
    .\scripts\manim\export_gif.ps1 -Uid F031 -Scene F031MovingAxisLesson -SceneFile scene.py -Name moving_axis -BuildRoot build/manim
    .\.venv-manim\Scripts\python.exe -B 01_function/F031_quadratic_moving_axis_extrema/manim/qa_frames.py 01_function/F031_quadratic_moving_axis_extrema/images/f031_moving_axis_extrema.gif build/manim/F031/14B

The MP4 and staged GIF are under build/manim/F031/moving_axis/.
After mathematical, technical, and local visual review, publish a new
name with -Publish -AssetName f031_moving_axis_extrema.gif and no overwrite.
Task 14B evidence and the final report are under build/manim/F031/14B/.
Do not run Publisher or Sync.
