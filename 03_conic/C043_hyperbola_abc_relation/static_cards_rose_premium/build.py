"""Build C043 Rose Premium 001/003 and copy the selected 002 byte-for-byte."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from cards import card_001, card_003, validate_visible_content
from quality import check_formula_regions
from static_cards_ab_experiment.cards import (  # noqa: E402
    card_002, mathematical_checks, validate_visible_copy)
from static_cards_ab_experiment.formula_spacing import check_standard_equation  # noqa: E402
from scripts.static_cards.style_a import P  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
DEST = ROOT / ".build/static_cards_rose_premium/C043"
SELECTED = ROOT / ".build/static_cards_ab_experiment_fix/C043/B_rose"
SELECTED_HASHES = {
    "002.png": "85096655f6ff7036c5a0e72a8cbbdb2b805839c2f887714f70cadf00d4552be8",
    "002.svg": "891c6c22f39ed4607f482518e6baf18c52527298ad57bf50a64895e6425508fa",
}
FORMAL_HASHES = {
    "C043": {
        "001": "f4a09f974c984fccba2fa0a6eda55bbba411aee9b157c1e01b9d5e399574fafb",
        "002": "eac8a4d0b9ed784f1616da48e89a6acc88f90310582596d9e139c9113560abac",
        "003": "558b584aa4b3d7fac632b980c53f991a4858ed83047bfdaae2152eb8986ef9d2",
    },
    "C051": {
        "001": "b835627c929140e5b36b34eb81714e66cbcabd75b74bc6a0abe67cdb11eedeb0",
        "002": "736e3a9497cf7f0a99bc49f387e4b0e57e59114f915b7f3ac7743b6694606af9",
        "003": "01eca6b6097468b36d9b44cda45e361acb44dd482654d70b21e23cc6150b0313",
    },
}
FORMAL_DIRS = {
    "C043": SOURCE / "images",
    "C051": ROOT / "03_conic/C051_parabola_focal_radius_coordinate/images",
}
PROTECTED_PREVIEW_DIRS = [
    ROOT / ".build/static_cards_v2/C043",
    ROOT / ".build/static_cards_style_a/C043",
    ROOT / ".build/static_cards_style_a_polish/C043",
    ROOT / ".build/static_cards_style_lab/C043",
    ROOT / ".build/static_cards_ab_experiment/C043",
    ROOT / ".build/static_cards_ab_experiment_fix/C043",
]
PROTECTED_DYNAMIC_DIRS = [
    ROOT / "scripts/manim",
    ROOT / "03_conic/C001_ellipse_circle_min_max_distance/manim",
    ROOT / "03_conic/C002_ellipse_point_line_distance_extrema/manim",
]
PROTECTED_GIFS = [
    ROOT / "03_conic/C001_ellipse_circle_min_max_distance/images/ellipse_circle_distance.gif",
    ROOT / "03_conic/C001_ellipse_circle_min_max_distance/images/ellipse_circle_max_distance.gif",
    ROOT / "03_conic/C002_ellipse_point_line_distance_extrema/images/ellipse_line_distance.gif",
]


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_baseline():
    selected = {}
    for filename in (*SELECTED_HASHES, "002_mobile_360.png", "002_mobile_390.png"):
        path = SELECTED / filename
        if not path.is_file():
            raise FileNotFoundError(f"selected Rose-002 file missing: {path}")
        selected[filename] = sha(path)
        if filename in SELECTED_HASHES and selected[filename] != SELECTED_HASHES[filename]:
            raise ValueError(f"selected Rose-002 {filename} hash changed")
    with Image.open(SELECTED / "002.png") as im:
        im.verify()
    with Image.open(SELECTED / "002.png") as im:
        if im.size != (1080, 1440):
            raise ValueError("selected Rose-002 PNG size changed")
    ET.parse(SELECTED / "002.svg")
    for width in (360, 390):
        with Image.open(SELECTED / f"002_mobile_{width}.png") as im:
            if im.size != (width, width*4//3):
                raise ValueError(f"selected Rose-002 mobile {width} size changed")
    for uid, numbers in FORMAL_HASHES.items():
        for number, expected in numbers.items():
            if sha(FORMAL_DIRS[uid] / f"{number}.png") != expected:
                raise ValueError(f"formal {uid}-{number} hash changed")
    return selected


def protected_snapshot():
    files = []
    for directory in (*PROTECTED_PREVIEW_DIRS, *PROTECTED_DYNAMIC_DIRS):
        if not directory.is_dir():
            raise FileNotFoundError(f"protected directory missing: {directory}")
        files.extend(path for path in directory.rglob("*") if path.is_file())
    files.extend(PROTECTED_GIFS)
    files.extend(SOURCE.glob("0[1-6]_*.tex"))
    files.extend(SOURCE.glob("*.pdf"))
    files.append(SOURCE / "meta.json")
    for directory in FORMAL_DIRS.values():
        files.extend(directory.glob("*.png"))
    return {str(path.relative_to(ROOT)): sha(path) for path in sorted(set(files))}


def audit_new_card(number, canvas):
    validate_visible_content(number, canvas)
    typography = canvas.audit_text()
    formulas = check_formula_regions(canvas)
    if number == "001":
        coverage = canvas.label_layout.finalize()
        plot = [entry for entry in coverage if entry["zone"] == "plot"]
        registered = [entry for entry in plot if entry["registered"]]
        if len(registered) != 6 or len(plot) != 7 or any(
                entry["collisions"] or (not entry["registered"] and not entry["exemption"])
                for entry in plot):
            raise ValueError("001 plot coverage/collision failure")
        if any(entry["actual_clearance_px"] < entry["minimum_required_px"]
               for entry in canvas.layout_report):
            raise ValueError("001 plot label clearance failure")
        segments = {getattr(line, "_mathnote_name", None): line.get_color()
                    for line in canvas.ax.lines}
        if {key: segments.get(key) for key in ("OA", "AB", "OB")} != {
                "OA": P.blue, "AB": P.teal, "OB": P.amber}:
            raise ValueError("001 parameter semantic colors changed")
        labels = canvas.layout_report
    else:
        if canvas.label_layout or canvas.layout_report:
            raise ValueError("003 unexpectedly has mathematical plot labels")
        labels = []
    renderer = canvas.fig.canvas.get_renderer()
    essential = [artist for artist in canvas.ax.texts if
                 artist.get_text().startswith("$\\frac{x^2}") or
                 artist.get_text().startswith("$c^2=") or
                 artist.get_text().startswith("$F_1=") or
                 artist.get_text().startswith("$y=\\pm") or
                 artist.get_text() in ("一眼记忆", "一眼方法")]
    min_height = min(a.get_window_extent(renderer).height/3 for a in essential)
    if min_height < 10:
        raise ValueError("essential 360px text smaller than 10px")
    return {"content": "PASS", "typography": typography, "formula_regions": formulas,
            "registered_plot_labels": len(labels), "labels": labels,
            "min_essential_text_height_360_px": round(min_height, 2)}


def font(size=26):
    path = Path("C:/Windows/Fonts/msyh.ttc")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def sheet(path, items, width, heading):
    margin, gap, head = 26, 26, 94
    height = width*4//3
    out = Image.new("RGB", (2*margin+len(items)*width+(len(items)-1)*gap,
                             head+height+margin), "#F8EEF2")
    draw = ImageDraw.Draw(out)
    draw.text((margin, 16), heading, fill="#6D2240", font=font(27))
    for i, (label, filename) in enumerate(items):
        x = margin+i*(width+gap)
        draw.text((x, 57), label, fill="#6D2240", font=font(25))
        with Image.open(filename) as im:
            out.paste(im.convert("RGB").resize((width, height), Image.Resampling.LANCZOS),
                      (x, head))
    out.save(path)


def verify_outputs():
    result = {}
    for number in ("001", "002", "003"):
        png, svg = DEST/f"{number}.png", DEST/f"{number}.svg"
        with Image.open(png) as im:
            im.verify()
        with Image.open(png) as im:
            if im.size != (1080, 1440):
                raise ValueError(f"{number} PNG size changed")
        ET.parse(svg)
        result[number] = {"png_sha256": sha(png), "svg_sha256": sha(svg)}
        for width in (360, 390):
            mobile = DEST/f"{number}_mobile_{width}.png"
            with Image.open(mobile) as im:
                if im.size != (width, width*4//3):
                    raise ValueError(f"{number} {width}px mobile size changed")
            result[number][f"mobile_{width}_sha256"] = sha(mobile)
    return result


def main():
    selected = verify_baseline()
    protected_before = protected_snapshot()
    math = mathematical_checks()
    DEST.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    report = {"task": "13G.4V.3C", "status": "ROSE PREMIUM THREE-CARD VISUAL REVIEW PENDING",
              "selected_theme": "B / ROSE PREMIUM", "selected_002": selected,
              "mathematical_checks": math, "cards": {}}
    for number, make in (("001", card_001), ("003", card_003)):
        canvas = make()
        report["cards"][number] = audit_new_card(number, canvas)
        canvas.export(DEST/f"{number}.png", DEST/f"{number}.svg")
        with Image.open(DEST/f"{number}.png") as im:
            rgb = im.convert("RGB")
        for width in (360, 390):
            rgb.resize((width, width*4//3), Image.Resampling.LANCZOS).save(
                DEST/f"{number}_mobile_{width}.png")

    selected_canvas = card_002("B_rose")
    validate_visible_copy("002", selected_canvas)
    selected_spacing = check_standard_equation(selected_canvas)
    selected_typography = selected_canvas.audit_text()
    selected_plot = [entry for entry in selected_canvas.label_layout.finalize()
                     if entry["zone"] == "plot"]
    if len([x for x in selected_plot if x["registered"]]) != 7 or any(
            x["collisions"] for x in selected_plot):
        raise ValueError("selected Rose-002 label gate failed")
    plt.close(selected_canvas.fig)
    report["cards"]["002"] = {"source": "selected baseline, byte copied",
                               "content": "PASS", "typography": selected_typography,
                               "standard_equation_spacing": selected_spacing,
                               "registered_plot_labels": 7}
    for filename in selected:
        shutil.copyfile(SELECTED/filename, DEST/filename)
        if sha(DEST/filename) != selected[filename]:
            raise ValueError(f"final Rose-002 differs from selected baseline: {filename}")

    numbers = (("001  快记", "001"), ("002  快懂", "002"), ("003  快用", "003"))
    sheet(DEST/"three_card_contact_sheet.png",
          [(label, DEST/f"{number}.png") for label, number in numbers], 540,
          "C043  /  Rose Premium 三卡原尺寸对照")
    sheet(DEST/"three_card_mobile_contact_sheet.png",
          [(label, DEST/f"{number}_mobile_360.png") for label, number in numbers], 360,
          "C043  /  Rose Premium 三卡 360px 对照")
    sheet(DEST/"002_selected_vs_final.png",
          [("已选 Rose-002", SELECTED/"002.png"), ("本轮最终 002", DEST/"002.png")],
          540, "C043-002  /  已选基准与三卡版本")

    report["outputs"] = verify_outputs()
    report["selected_002_byte_identical"] = all(
        sha(DEST/filename) == digest for filename, digest in selected.items())
    if not report["selected_002_byte_identical"]:
        raise ValueError("selected Rose-002 byte identity failed")
    if verify_baseline() != selected or protected_snapshot() != protected_before:
        raise ValueError("protected formal, dynamic or historical preview files changed")
    report["protected_file_count"] = len(protected_before)
    report["freeze_regression"] = "PASS"
    report["render_seconds"] = round(time.perf_counter()-start, 2)
    (DEST/"build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(DEST), "seconds": report["render_seconds"],
                      "selected_002_byte_identical": report["selected_002_byte_identical"],
                      "protected_files": report["protected_file_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
