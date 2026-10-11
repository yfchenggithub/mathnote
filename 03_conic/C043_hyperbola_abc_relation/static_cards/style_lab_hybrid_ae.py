"""One isolated C043-002 effect preview: Style A structure × Style E background."""

from __future__ import annotations

import hashlib
import json

from PIL import Image

from style_lab import Card, OUT, ROOT, SOURCE, geom
from model import validation_results


DEST = OUT / "AE_hybrid_preview"


def draw():
    c = Card("AE", "#0B1830")
    # A's reading path: title, core relation, coordinate diagram, conclusion,
    # then one-line memory cue. E supplies the dark field and luminous geometry.
    c.gradient(0, 244, "#09182E", "#17466D")
    c.box(62, 228, 956, 4, "#57C9D4", radius=0)
    c.label("知树   /   C043  ·  002 快懂", 68, 76, 26, "#8DE3E2", bold=True)
    c.label("双曲线 a、b、c 的关系", 68, 164, 51, "#F4FAFF", bold=True)

    c.box(62, 270, 956, 176, "#392F29", edge="#9F7650", radius=26)
    c.label("核心关系", 94, 325, 27, "#FFC785", bold=True)
    c.math(r"c^2=a^2+b^2", 94, 390, 53, "#FFF6DF")

    c.label("标准方程  /  横轴型", 62, 493, 24, "#8BDFDC", bold=True)
    c.math(r"\frac{x^2}{a^2}-\frac{y^2}{b^2}=1\quad(a,b>0)",
           1008, 489, 25, "#CBDFEE", ha="right")
    c.box(62, 532, 956, 502, "#132E49", edge="#3B6580", radius=26)
    geom(c, origin=(506, 790), scale=48, bounds=(88, 551, 992, 1013),
         colors=("#6F93A8", "#79BDFF", "#71B1FF", "#6BE1C7", "#FFB26E"),
         curve_width=5)

    c.box(62, 1054, 956, 196, "#153C3E", edge="#3A897D", radius=25)
    c.label("看图得关系", 94, 1102, 27, "#8CE6CB", bold=True)
    c.math(r"OA=a,\quad AB=b,\quad OB=OF_2=c", 94, 1157, 31, "#EDFFF9")
    c.label("B 是辅助矩形角点，不在曲线上，也不是焦点。", 94, 1210, 23, "#B9DED5")

    c.box(62, 1271, 956, 65, "#22484A", edge="#467D73", radius=18)
    c.label("一眼记忆  ·  斜边与半焦距等长，但不是同一线段。",
            90, 1314, 22, "#D5F7EA", bold=True)
    c.label("C043  /  解析几何", 68, 1389, 19, "#8AAFC2")
    c.label("知树  ·  快懂 002", 1010, 1389, 19, "#8AAFC2", ha="right")
    return c


def main():
    formal = (SOURCE / "01_statement.tex").read_text(encoding="utf-8")
    assert all(s in formal for s in (r"\frac{x^2}{a^2}", r"\frac{y^2}{b^2}",
                                     "c^2 = a^2 + b^2", "a>0, b>0"))
    checks = validation_results()
    DEST.mkdir(parents=True, exist_ok=True)
    c = draw()
    coverage = c.label_layout.finalize()
    typography = c.audit_text()
    png, svg = DEST / "002.png", DEST / "002.svg"
    c.export(png, svg)
    im = Image.open(png).convert("RGB")
    assert im.size == (1080, 1440)
    for width in (360, 390):
        im.resize((width, width*4//3), Image.Resampling.LANCZOS).save(
            DEST / f"002_mobile_{width}.png")
    report = {
        "scope": "C043-002 isolated A structure × E background visual effect",
        "formal_source": "read-only", "model_checks": checks,
        "geometry": "Hyperbola(3,4), c=5, isotropic MathFrame",
        "labels": c.layout_report, "coverage": coverage,
        "typography": typography,
        "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
        "status": "VISUAL REVIEW PENDING",
    }
    (DEST / "effect_notes.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A×E effect preview: {DEST}")


if __name__ == "__main__":
    main()
