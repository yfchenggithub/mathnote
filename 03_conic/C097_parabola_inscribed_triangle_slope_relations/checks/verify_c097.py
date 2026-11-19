"""Exact rational checks for C097; samples supplement the written proofs."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[3]
UID = ROOT / "03_conic/C097_parabola_inscribed_triangle_slope_relations"


def slope(a, b):
    assert a[0] != b[0]
    return (b[1] - a[1]) / (b[0] - a[0])


def run():
    counts = dict(core=0, tangent=0, translated_quadratic=0,
                  parabola_focus=0, ellipse_focus=0, right_triangle=0,
                  reciprocal_algebra=0)
    vals = list(map(Q, [-3, -2, -1, 0, "1/2", 1, 2, 3]))
    origin = (Q(0), Q(0))
    for p in map(Q, [-3, -1, "1/2", 1, 2]):
        for u in vals:
            for v in vals:
                if u == v:
                    continue
                a, b = (u, u*u/(2*p)), (v, v*v/(2*p))
                ka, kb = u/p, v/p
                assert slope(a, b) == (ka + kb)/2
                assert a[1] == ka*a[0] - u*u/(2*p)
                # The intersection quadratic is exactly (x-u)^2.
                assert 2*p*ka == 2*u
                counts["tangent"] += 1
                if u and v:
                    assert slope(origin, a) + slope(origin, b) == slope(a, b)
                    ah, bh = a[::-1], b[::-1]
                    inv_chord = (bh[0]-ah[0])/(bh[1]-ah[1])
                    assert inv_chord == Q(1)/slope(origin, ah) + Q(1)/slope(origin, bh)
                    assert inv_chord == (u/p+v/p)/2
                    if u+v:
                        assert Q(1)/slope(ah, bh) == (Q(1)/(p/u)+Q(1)/(p/v))/2
                    else:
                        assert ah[0] == bh[0]  # Vertical chord: do not invert slope.
                    counts["core"] += 1

    for alpha in map(Q, [-2, "-1/2", "1/2", 1, 3]):
        for h, k in [(Q(0), Q(0)), (Q(2), Q(1)), (Q(-3), Q(4))]:
            for u in vals:
                for v in vals:
                    if not u or not v or u == v:
                        continue
                    a = (h+u, k+alpha*u*u)
                    b = (h+v, k+alpha*v*v)
                    assert slope((h, k), a) + slope((h, k), b) == slope(a, b)
                    assert slope(a, b) == (2*alpha*u+2*alpha*v)/2
                    counts["translated_quadratic"] += 1

    for p in map(Q, ["1/2", 1, 2, 3, 5]):
        for t in vals:
            if not t:
                continue
            u, v = p*t, -p/t
            a, b = (u*u/(2*p), u), (v*v/(2*p), v)
            r, s = a[0]+p/2, b[0]+p/2
            f = (p/2, Q(0))
            assert r > 0 and s > 0
            assert (a[0]-f[0])*b[1] == (b[0]-f[0])*a[1]
            assert (a[0]-f[0])**2+a[1]**2 == r*r
            assert r*s == p*(r+s)/2
            assert Q(1)/r+Q(1)/s == 2/p
            counts["parabola_focus"] += 1

    directions = [(Q(0), Q(1))]
    for t in vals:
        directions.append(((1-t*t)/(1+t*t), 2*t/(1+t*t)))
    for a, b, c in [(Q(5), Q(3), Q(4)), (Q(13), Q(5), Q(12)),
                    (Q(5), Q(4), Q(3))]:
        assert a*a == b*b+c*c
        for dx, dy in directions:
            assert dx*dx+dy*dy == 1
            r, s = b*b/(a+c*dx), b*b/(a-c*dx)
            pa = (c+r*dx, r*dy)
            pb = (c-s*dx, -s*dy)
            assert r > 0 and s > 0
            for point, distance in [(pa, r), (pb, s)]:
                x, y = point
                assert x*x/(a*a)+y*y/(b*b) == 1
                assert (x-c)**2+y*y == distance*distance
                assert distance == a-c*x/a
            assert Q(1)/r+Q(1)/s == 2*a/(b*b)
            counts["ellipse_focus"] += 1

    for a, b, c in map(lambda t: tuple(map(Q, t)), [(3,4,5),(5,12,13),(8,15,17)]):
        h = a*b/c
        assert a*a+b*b == c*c
        assert Q(1)/(h*h) == Q(1)/(a*a)+Q(1)/(b*b)
        foot = (a*a*b/(c*c), a*b*b/(c*c))
        assert a*foot[0]+b*foot[1] == a*b
        assert foot[0]*b-foot[1]*a == 0
        assert foot[0]**2+foot[1]**2 == h*h
        counts["right_triangle"] += 1
    for u in vals:
        for v in vals:
            if not u or not v:
                continue
            reciprocal_sum = Q(1)/u+Q(1)/v
            assert reciprocal_sum == (u+v)/(u*v)
            if u+v:
                assert Q(1)/reciprocal_sum == u*v/(u+v)
            else:
                assert reciprocal_sum == 0
            counts["reciprocal_algebra"] += 1

    # Exact values used by the seven new diagrams and examples.
    assert slope((Q(3),Q(2)), (Q("1/2"),Q("13/4"))) == Q("-1/2")
    assert slope((Q("1/2"),Q(1)), (Q("1/18"),Q("1/3"))) == Q("3/2")
    assert (Q(4)-1)**2+Q(4)**2 == 25
    assert (Q("1/4")-1)**2+Q(-1)**2 == Q("25/16")
    assert Q(1)/5+Q(1)/Q("5/4") == 1
    assert Q(2)/5 != 1  # Nonfocal x=4 counterexample.

    meta = json.loads((UID/"meta.json").read_text(encoding="utf-8"))
    assert meta["id"] == "C097" and type(meta["isPro"]) is int and meta["isPro"] == 0
    assets = [meta["assets"]["tikz"]]+meta["assets"]["additional_tikz"]
    assert len(assets) == 18 and len(set(assets)) == 18
    assert all((ROOT/name).is_file() for name in assets)
    for path in UID.glob("*.tex"):
        for target in re.findall(r"\\input\{([^}]+)\}", path.read_text(encoding="utf-8")):
            candidate = ROOT/target
            if candidate.suffix != ".tex":
                candidate = candidate.with_suffix(".tex")
            assert candidate.is_file(), target

    before = ROOT/".tmp/C097_extension_20261119/before"
    if before.is_dir():
        manifest = json.loads((before/"manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest.items():
            if name.startswith("assets/") or name.endswith("/main.tex"):
                assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
        for filename in ["01_statement.tex","02_explanation.tex","03_proof.tex",
                         "04_examples.tex","05_traps.tex","06_summary.tex","source.tex"]:
            previous = (before/UID.relative_to(ROOT)/filename).read_text(encoding="utf-8").strip()
            assert previous in (UID/filename).read_text(encoding="utf-8"), filename
        old_meta = json.loads((before/UID.relative_to(ROOT)/"meta.json").read_text(encoding="utf-8"))
        def check_types(old, new):
            assert type(old) is type(new)
            if isinstance(old, dict):
                for key in old:
                    assert key in new
                    check_types(old[key], new[key])
        check_types(old_meta, meta)
        assert old_meta["math"]["core_formula"] == meta["math"]["core_formula"]

    return {"status":"PASS", "exact_cases":counts, "total_exact_cases":sum(counts.values()),
            "diagram_count":len(assets), "input_paths":"PASS", "metadata":"PASS",
            "original_content_and_11_figures_preserved":"PASS",
            "scope":"C097 only; samples supplement general algebraic proofs"}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
