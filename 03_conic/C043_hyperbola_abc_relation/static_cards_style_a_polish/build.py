"""Isolated 13G.4V.3A preview; never writes reviewed or formal assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cards import (card_001, card_002, card_003, mathematical_checks,
                   validate_visible_copy)


ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / ".build/static_cards_style_a/C043"
SELECTED = ROOT / ".build/static_cards_style_lab/C043/A_premium_infographic/002.png"
DEST = ROOT / ".build/static_cards_style_a_polish/C043"
OLD_HASHES = {
    "001": "2a3133da531403b86b18360ebf05e705f0aa25bb90d6337067f56f1bb2a88e45",
    "002": "997b137ebc44b874134ad26e4591e851d9156a29d55ea7db869524101137c522",
    "003": "a826550d45a40d63b7177f52837037262eee0c1c55de0d57c5eb3f5b7239e10a",
}


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_baselines():
    if not SELECTED.is_file() or sha(SELECTED) != OLD_HASHES["002"]:
        raise ValueError("selected Style A-002 baseline changed or is missing")
    result = {}
    for n, expected in OLD_HASHES.items():
        path = OLD / f"{n}.png"
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"reviewed Style A {n} baseline changed or is missing")
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            if im.size != (1080, 1440):
                raise ValueError(f"reviewed Style A {n} has wrong size")
        result[n] = expected
    for name in ("three_card_contact_sheet.png", "three_card_mobile_contact_sheet.png"):
        if not (OLD / name).is_file():
            raise FileNotFoundError(f"reviewed contact sheet missing: {name}")
        result[name] = sha(OLD / name)
    return result


def audit(canvas, number: str):
    validate_visible_copy(number, canvas)
    coverage = canvas.label_layout.finalize() if canvas.label_layout else []
    plot = [entry for entry in coverage if entry["zone"] == "plot"]
    expected = {"001": 6, "002": 7, "003": 0}[number]
    registered = [entry for entry in plot if entry["registered"]]
    if len(registered) != expected or any(
            (not x["registered"] and not x["exemption"]) or x["collisions"] for x in plot):
        raise ValueError(f"{number} coverage or collision failure")
    typography = canvas.audit_text()
    canvas.fig.canvas.draw()
    renderer = canvas.fig.canvas.get_renderer()
    font_rows = []
    for artist in canvas.ax.texts:
        if not artist.get_visible():
            continue
        box = artist.get_window_extent(renderer)
        font_rows.append({"text": artist.get_text(), "font_pt": artist.get_fontsize(),
                          "bbox_height_360_px": round(box.height/3, 1)})
    return {"math_content": "PASS", "plot_text": len(plot),
            "registered_plot_labels": len(registered),
            "exempt_plot_titles": len(plot)-len(registered),
            "uncovered_plot_text": 0, "plot_collisions": 0,
            "labels": canvas.layout_report, "typography": typography,
            "font_audit": font_rows, "layout_areas": canvas.areas}


def export_card(canvas, number: str, *, replace_preview=False):
    data = audit(canvas, number)
    tmp_png, tmp_svg = DEST / f"_{number}.png", DEST / f"_{number}.svg"
    canvas.export(tmp_png, tmp_svg)
    for temporary, final in ((tmp_png, DEST / f"{number}.png"),
                             (tmp_svg, DEST / f"{number}.svg")):
        if final.exists() and sha(final) != sha(temporary) and not replace_preview:
            raise FileExistsError(f"changed polish preview requires --replace-preview: {final}")
        temporary.replace(final)
    png, svg = DEST / f"{number}.png", DEST / f"{number}.svg"
    with Image.open(png) as im:
        im.verify()
    with Image.open(png) as im:
        if im.size != (1080, 1440):
            raise ValueError(f"{number} incorrect output size")
    ET.parse(svg)
    data.update({"png_sha256": sha(png), "svg_sha256": sha(svg),
                 "size": [1080, 1440], "svg_parse": "PASS"})
    return data


def font(size=27):
    path = Path("C:/Windows/Fonts/msyh.ttc")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def sheet(path: Path, items, *, card_width: int, heading: str):
    gap, margin, head, label_h = 24, 24, 74, 58
    card_h = card_width*4//3
    out = Image.new("RGB", (margin*2+card_width*3+gap*2,
                             head+label_h+card_h+margin), "#E8F1F7")
    draw = ImageDraw.Draw(out)
    draw.text((margin, 16), heading, fill="#15375F", font=font(27))
    for i, (label, image_path) in enumerate(items):
        x = margin+i*(card_width+gap)
        draw.text((x, head), label, fill="#15375F", font=font(26))
        with Image.open(image_path) as im:
            thumb = im.convert("RGB").resize((card_width, card_h), Image.Resampling.LANCZOS)
        out.paste(thumb, (x, head+label_h))
    out.save(path)


def before_after(number: str):
    card_width, card_h = 540, 720
    out = Image.new("RGB", (card_width*2+78, card_h+104), "#E8F1F7")
    draw = ImageDraw.Draw(out)
    draw.text((24, 22), f"{number}  /  精修前", fill="#15375F", font=font(27))
    draw.text((card_width+54, 22), f"{number}  /  精修后", fill="#15375F", font=font(27))
    for x, image_path in ((24, OLD / f"{number}.png"),
                          (card_width+54, DEST / f"{number}.png")):
        with Image.open(image_path) as im:
            out.paste(im.convert("RGB").resize((card_width, card_h),
                                                Image.Resampling.LANCZOS), (x, 75))
    out.save(DEST / f"{number}_before_after.png")


def whole_comparison():
    card_width, card_h, gap, margin = 360, 480, 22, 24
    row_h = 55+card_h
    out = Image.new("RGB", (margin*2+3*card_width+2*gap,
                             margin*2+2*row_h+52), "#E8F1F7")
    draw = ImageDraw.Draw(out)
    draw.text((margin, 12), "C043  /  Style A 精品精修 · 同尺度对照",
              fill="#15375F", font=font(27))
    for row, (label, directory) in enumerate((("精修前", OLD), ("精修后", DEST))):
        y = margin+52+row*row_h
        for col, (n, kind) in enumerate((("001", "快记"), ("002", "快懂"), ("003", "快用"))):
            x = margin+col*(card_width+gap)
            draw.text((x, y), f"{label}  /  {n} {kind}", fill="#15375F", font=font(24))
            with Image.open(directory / f"{n}.png") as im:
                thumb = im.convert("RGB").resize((card_width, card_h),
                                                  Image.Resampling.LANCZOS)
            out.paste(thumb, (x, y+55))
    out.save(DEST / "three_card_before_after.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace-preview", action="store_true")
    args = parser.parse_args()
    baselines = verify_baselines()
    math_checks = mathematical_checks()
    DEST.mkdir(parents=True, exist_ok=True)
    report = {"task": "13G.4V.3A", "uid": "C043",
              "status": "PREMIUM VISUAL REVIEW PENDING", "old_baselines": baselines,
              "selected_A_002_sha256": sha(SELECTED), "model_math": math_checks,
              "cards": {}}
    for number, make in (("001", card_001), ("002", card_002), ("003", card_003)):
        report["cards"][number] = export_card(make(), number,
                                               replace_preview=args.replace_preview)
        with Image.open(DEST / f"{number}.png") as im:
            rgb = im.convert("RGB")
        for width in (360, 390):
            rgb.resize((width, width*4//3), Image.Resampling.LANCZOS).save(
                DEST / f"{number}_mobile_{width}.png")
        before_after(number)
    items = [(f"{n}  {k}", DEST / f"{n}.png") for n,k in
             (("001", "快记"), ("002", "快懂"), ("003", "快用"))]
    sheet(DEST / "three_card_contact_sheet.png", items, card_width=540,
          heading="C043  /  Style A 精品精修三卡")
    mobile_items = [(f"{n}  {k}", DEST / f"{n}_mobile_360.png") for n,k in
                    (("001", "快记"), ("002", "快懂"), ("003", "快用"))]
    sheet(DEST / "three_card_mobile_contact_sheet.png", mobile_items,
          card_width=360, heading="C043  /  Style A 精品精修 · 360px")
    shutil.copyfile(OLD / "three_card_contact_sheet.png",
                    DEST / "baseline_three_card_contact_sheet.png")
    whole_comparison()
    report["baseline_recheck"] = verify_baselines()
    (DEST / "build_report.json").write_text(json.dumps(report, ensure_ascii=False,
                                                  indent=2), encoding="utf-8")
    print(f"C043 Style A polish: {DEST}")


if __name__ == "__main__":
    main()
