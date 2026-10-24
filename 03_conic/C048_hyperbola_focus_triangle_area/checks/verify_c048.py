"""Independent vector/coordinate checks for C048 teaching diagrams and examples."""
from pathlib import Path
import json
import math
import re

ROOT = Path(__file__).resolve().parents[3]
UID_DIR = ROOT / "03_conic/C048_hyperbola_focus_triangle_area"


def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=2e-8, abs_tol=2e-8), (actual, expected)


def measure(point, left, right):
    u = (left[0] - point[0], left[1] - point[1])
    v = (right[0] - point[0], right[1] - point[1])
    cross = abs(u[0] * v[1] - u[1] * v[0])
    dot = u[0] * v[0] + u[1] * v[1]
    return math.hypot(*u), math.hypot(*v), math.atan2(cross, dot), cross / 2


states = 0
for a, b in [(1, math.sqrt(3)), (2, math.sqrt(5)), (3, 4),
             (math.sqrt(17), math.sqrt(8)), (.5, 4), (4, .5)]:
    c = math.hypot(a, b)
    for t in [.001, .01, .1, .3, .8, 1.4, 2.3, 3.2]:
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                x, y = sx * a * math.cosh(t), sy * b * math.sinh(t)
                close(x*x/a**2 - y*y/b**2, 1)
                for point, left, right in [((x, y), (-c, 0), (c, 0)),
                                          ((y, x), (0, -c), (0, c))]:
                    m, n, theta, area = measure(point, left, right)
                    close(abs(m-n), 2*a)
                    close(area, c*abs(y))
                    close(m*n*math.sin(theta/2)**2, b*b)
                    close(area, b*b/math.tan(theta/2))
                    far, near = max(m, n), min(m, n)
                    projection = near*math.cos(theta)
                    altitude = near*math.sin(theta)
                    assert far-projection > 0
                    close(math.hypot(far-projection, altitude), 2*c)
                    close(far*altitude/2, area)
                    assert 0 < theta < math.pi
                    states += 1

# Same physical triangle lies on both the illustrated ellipse and hyperbola.
point, left, right = (2, 3), (-2, 0), (2, 0)
m, n, theta, area = measure(point, left, right)
close(m, 5); close(n, 3); close(area, 6)
close(2**2/16 + 3**2/12, 1)
close(2**2 - 3**2/3, 1)
close(m+n, 8); close(m-n, 2)
close(12*math.tan(theta/2), area)
close(3/math.tan(theta/2), area)

# Exact signed projections for the two actual states in the projection figure.
for x, y, expected_u_sign in [(2, 3, 1), (2/math.sqrt(3), 1, -1)]:
    m, n, angle, area = measure((x, y), left, right)
    u, v = n*math.cos(angle), n*math.sin(angle)
    close(math.hypot(m-u, v), 4)
    close(m*v/2, area)
    assert u*expected_u_sign > 0 and v > 0 and m-u > 0
    if expected_u_sign > 0:
        close(u, 1.8); close(v, 2.4)
    else:
        close(n, 4/math.sqrt(3)-1)
        close(u, -5*n/13); close(v, 12*n/13)

# All three plotted curve points; the vertex has opposite focal rays.
angles, areas = [], []
for height in [0, 1.5, 6]:
    x = math.sqrt(1+height*height/3)
    m, n, angle, area = measure((x, height), left, right)
    close(x*x-height*height/3, 1)
    close(area, 2*height)
    angles.append(angle); areas.append(area)
close(angles[0], math.pi); close(angles[1], math.pi/2)
close(math.degrees(angles[2]), 28.07248693585296)
assert angles[0] > angles[1] > angles[2] and areas[0] < areas[1] < areas[2]

# Independently realize examples 1, 2, and 3/6 and verify their stated angles.
for a, b, point, expected_angle, expected_area in [
    (2, math.sqrt(5), (4*math.sqrt(6)/3, 5*math.sqrt(3)/3), math.pi/3, 5*math.sqrt(3)),
    (3, 4, (3*math.sqrt(41)/5, 16/5), math.pi/2, 16),
    (math.sqrt(17), math.sqrt(8), (7*math.sqrt(17)/5, 8*math.sqrt(3)/5), math.pi/3, 8*math.sqrt(3)),
]:
    c = math.hypot(a, b)
    close(point[0]**2/a**2-point[1]**2/b**2, 1)
    _, _, angle, area = measure(point, (-c, 0), (c, 0))
    close(angle, expected_angle); close(area, expected_area)

meta = json.loads((UID_DIR / 'meta.json').read_text(encoding='utf-8'))
assert meta['interactive']['has_diagram'] is True
for name in ['01_statement', '02_explanation', '03_proof', '04_examples', '05_traps', '06_summary']:
    source = (UID_DIR / (name + '.tex')).read_text(encoding='utf-8')
    for path in re.findall(r'\\input\{([^}]+)\}', source):
        assert (ROOT / (path if path.endswith('.tex') else path+'.tex')).is_file(), path
print(f'C048 PASS: {states} independent curve/angle/area states; actual shared triangle, signed projections, three-state endpoints, example coordinates and TikZ references.')
