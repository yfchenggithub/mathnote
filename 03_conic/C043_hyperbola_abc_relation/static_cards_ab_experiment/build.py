"""Build isolated C043-002 premium color comparison and audit its constants."""

from __future__ import annotations

import hashlib
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from PIL import Image, ImageDraw, ImageFont

from cards import card_002, mathematical_checks, validate_visible_copy


ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / ".build/static_cards_ab_experiment/C043"
POLISH = ROOT / ".build/static_cards_style_a_polish/C043/002.png"
SELECTED = ROOT / ".build/static_cards_style_lab/C043/A_premium_infographic/002.png"
FREEZE = {
    "C043": (ROOT / "03_conic/C043_hyperbola_abc_relation/images", {
        "001": "f4a09f974c984fccba2fa0a6eda55bbba411aee9b157c1e01b9d5e399574fafb",
        "002": "eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac",
        "003": "558b584aa4b3d7fac632b980c53f991a4858ed83047bfdaae2152eb8986ef9d2"}),
    "C051": (ROOT / "03_conic/C051_parabola_focal_radius_coordinate/images", {
        "001": "b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0",
        "002": "736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9",
        "003": "01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313"}),
}
POLISH_SHA = "3588a70376964804a40e2f08aeff6f523b22a52b7595bced6b83b265a95b9223"
SELECTED_SHA = "997b137ebc44b874134ad26e4591e851d9156a29d55ea7db869524101137c522"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protected():
    checks = {}
    for uid, (directory, expected) in FREEZE.items():
        for number, digest in expected.items():
            path = directory / f"{number}.png"
            if not path.is_file() or sha(path) != digest:
                raise ValueError(f"protected {uid}-{number} changed or missing: {path}")
            checks[f"{uid}-{number}"] = digest
    for name, path, digest in (("selected_style_a_002", SELECTED, SELECTED_SHA),
                               ("polished_style_a_002", POLISH, POLISH_SHA)):
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f"protected {name} changed or missing: {path}")
        checks[name] = digest
    return checks


def signature(canvas):
    """Exclude color, retain exact text, positions, sizes and math paths."""
    texts = [(t.get_text(), *[round(float(v), 5) for v in t.get_position()],
              round(t.get_fontsize(), 5), t.get_ha(), t.get_va(),
              str(t.get_fontproperties().get_weight())) for t in canvas.ax.texts]
    plots = []
    for line in canvas.ax.lines:
        name = getattr(line, "_mathnote_name", None)
        if not name:
            continue
        plots.append((name, line.get_color(),
                      [[round(float(x), 5), round(float(y), 5)]
                       for x, y in line.get_xydata()]))
    shapes = []
    for patch in canvas.ax.patches:
        if isinstance(patch, Circle) and getattr(patch, "_mathnote_name", None):
            shapes.append((patch._mathnote_name, [float(v) for v in patch.center],
                           float(patch.radius), [float(v) for v in patch.get_facecolor()]))
        elif isinstance(patch, Polygon):
            shapes.append(("auxiliary triangle",
                           [[float(v) for v in xy] for xy in patch.get_xy()],
                           [float(v) for v in patch.get_facecolor()]))
    labels = [(x["label"], x["object"], x["candidate"], x["bbox_px"])
              for x in canvas.layout_report]
    return {"text_layout": hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest(),
            "math_geometry": hashlib.sha256(json.dumps({"lines": plots, "shapes": shapes}).encode()).hexdigest(),
            "labels": hashlib.sha256(json.dumps(labels, ensure_ascii=False).encode()).hexdigest(),
            "text_count": len(texts), "math_object_count": len(plots),
            "registered_labels": len(labels)}


def audit(canvas):
    validate_visible_copy("002", canvas)
    coverage = canvas.label_layout.finalize()
    plot = [entry for entry in coverage if entry["zone"] == "plot"]
    if len([x for x in plot if x["registered"]]) != 7 or any(
        x["collisions"] or (not x["registered"] and not x["exemption"]) for x in plot
    ):
        raise ValueError("plot label coverage or collision failed")
    typography = canvas.audit_text()
    canvas.fig.canvas.draw()
    renderer = canvas.fig.canvas.get_renderer()
    mobile_min = min(t.get_window_extent(renderer).height / 3 for t in canvas.ax.texts
                     if t.get_text() in ("一眼记忆", "斜边与半焦距等长，",
                                         "但它们不是同一线段。") or
                     t.get_text().startswith("$c^2="))
    if mobile_min < 10:
        raise ValueError(f"mobile essential text too small: {mobile_min:.1f}px")
    return {"visible_copy": "PASS", "plot_labels": 7, "plot_exempt_titles": 1,
            "collision": "PASS", "typography": typography,
            "mobile_essential_min_bbox_height_px": round(mobile_min, 2)}


def font(size=26):
    path = Path("C:/Windows/Fonts/msyh.ttc")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def sheet(path: Path, items, width: int, heading: str):
    margin, gap, head = 26, 26, 94
    height = width * 4 // 3
    out = Image.new("RGB", (2*margin+len(items)*width+(len(items)-1)*gap,
                             head+height+margin), "#EAF1F7")
    draw = ImageDraw.Draw(out)
    draw.text((margin, 16), heading, fill="#193958", font=font(27))
    for i, (label, path_in) in enumerate(items):
        x = margin+i*(width+gap)
        draw.text((x, 57), label, fill="#193958", font=font(25))
        with Image.open(path_in) as im:
            out.paste(im.convert("RGB").resize((width, height), Image.Resampling.LANCZOS),
                      (x, head))
    out.save(path)


def main():
    before = verify_protected()
    math = mathematical_checks()
    DEST.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    data = {"task": "13G.4V.3B", "status": "VISUAL A/B SELECTION PENDING",
            "frozen_before": before, "mathematics": math, "themes": {}}
    signatures = {}
    for name in ("A_blue", "B_rose"):
        canvas = card_002(name)
        quality = audit(canvas)
        signatures[name] = signature(canvas)
        out = DEST / name
        out.mkdir(exist_ok=True)
        png, svg = out / "002.png", out / "002.svg"
        canvas.export(png, svg)
        with Image.open(png) as im:
            im.verify()
        with Image.open(png) as im:
            if im.size != (1080, 1440):
                raise ValueError(f"{name} wrong canvas size")
            rgb = im.convert("RGB")
        ET.parse(svg)
        for width in (360, 390):
            rgb.resize((width, width*4//3), Image.Resampling.LANCZOS).save(
                out / f"002_mobile_{width}.png")
        data["themes"][name] = {"quality": quality, "signature": signatures[name],
                                "png_sha256": sha(png), "svg_sha256": sha(svg),
                                "size": [1080, 1440], "svg_parse": "PASS"}
    if signatures["A_blue"] != signatures["B_rose"]:
        raise ValueError("A/B content, typography, geometry or label placement changed")
    data["ab_consistency"] = "PASS"
    sheet(DEST / "ab_comparison.png", [("A  Blue Premium", DEST/"A_blue/002.png"),
                                         ("B  Rose Premium", DEST/"B_rose/002.png")],
          540, "C043-002  /  蓝色与玫红原尺寸对照")
    sheet(DEST / "ab_mobile_comparison.png",
          [("A  Blue Premium", DEST/"A_blue/002_mobile_360.png"),
           ("B  Rose Premium", DEST/"B_rose/002_mobile_360.png")],
          360, "C043-002  /  360px 手机对照")
    sheet(DEST / "style_a_original_vs_blue_vs_rose.png",
          [("现有 Style A 精修版", POLISH),
           ("新 Blue Premium", DEST/"A_blue/002.png"),
           ("新 Rose Premium", DEST/"B_rose/002.png")],
          440, "C043-002  /  当前基准与 A/B 对照")
    data["frozen_after"] = verify_protected()
    data["freeze_regression"] = "PASS" if data["frozen_before"] == data["frozen_after"] else "FAIL"
    data["render_seconds"] = round(time.perf_counter()-start, 2)
    (DEST / "build_report.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    print(json.dumps({"output": str(DEST), "seconds": data["render_seconds"],
                      "ab_consistency": data["ab_consistency"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
