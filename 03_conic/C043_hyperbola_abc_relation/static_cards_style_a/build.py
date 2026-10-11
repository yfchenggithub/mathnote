"""Build the selected Style A C043 three-card set in an isolated preview."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

from cards import (card_001, card_003, validate_card_copy, validate_formal_sources,
                   validate_selected_copy)
from model import validation_results


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
DEST = ROOT / ".build/static_cards_style_a/C043"
SELECTED = ROOT / ".build/static_cards_style_lab/C043/A_premium_infographic"
SELECTED_SHA256 = "997b137ebc44b874134ad26e4591e851d9156a29d55ea7db869524101137c522"


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_selected():
    png, svg, notes = SELECTED / "002.png", SELECTED / "002.svg", SELECTED / "style_notes.json"
    if not all(p.is_file() for p in (png, svg, notes)):
        raise FileNotFoundError("selected Style A-002 baseline is incomplete")
    digest = sha(png)
    stored = json.loads(notes.read_text(encoding="utf-8"))
    if digest != SELECTED_SHA256 or stored["png_sha256"] != digest:
        raise ValueError("selected Style A-002 baseline hash changed")
    with Image.open(png) as image:
        image.verify()
    with Image.open(png) as image:
        if image.size != (1080, 1440):
            raise ValueError("selected A-002 is not 1080×1440")
    ET.parse(svg)
    return {"png_sha256": digest, "svg_sha256": sha(svg), "size": [1080, 1440]}


def audit_canvas(canvas, number):
    validate_card_copy(number, canvas)
    coverage = canvas.label_layout.finalize() if canvas.label_layout else []
    plot = [entry for entry in coverage if entry["zone"] == "plot"]
    if any(not entry["registered"] or entry["collisions"] for entry in plot):
        raise ValueError(f"{number} plot coverage failed")
    typography = canvas.audit_text()
    return {"math_content": "PASS", "labels": canvas.layout_report,
            "plot_text": len(plot), "uncovered_plot_text": 0,
            "plot_collisions": 0, "typography": typography}


def save_checked(canvas, number, *, replace_preview=False):
    data = audit_canvas(canvas, number)
    png, svg = DEST / f"{number}.png", DEST / f"{number}.svg"
    tmp_png, tmp_svg = DEST / f"_{number}.png", DEST / f"_{number}.svg"
    canvas.export(tmp_png, tmp_svg)
    for temporary, final in ((tmp_png, png), (tmp_svg, svg)):
        if final.exists() and sha(final) != sha(temporary) and not replace_preview:
            raise FileExistsError(f"changed preview requires --replace-preview: {final}")
        temporary.replace(final)
    with Image.open(png) as image:
        image.verify()
    with Image.open(png) as image:
        if image.size != (1080, 1440):
            raise ValueError(f"{number} PNG has wrong dimensions")
    ET.parse(svg)
    data.update({"png_sha256": sha(png), "svg_sha256": sha(svg),
                 "png_size": [1080, 1440], "svg_parse": "PASS"})
    return data


def copy_selected(*, replace_preview=False):
    data = verify_selected()
    for suffix in ("png", "svg"):
        src, dst = SELECTED / f"002.{suffix}", DEST / f"002.{suffix}"
        if dst.exists() and sha(dst) != sha(src) and not replace_preview:
            raise FileExistsError(f"changed preview requires --replace-preview: {dst}")
        shutil.copyfile(src, dst)
    assert sha(DEST / "002.png") == SELECTED_SHA256
    # Audit the exact selected drawing code in memory; final pixels are copied.
    sys.path.insert(0, str(SOURCE / "static_cards"))
    from style_lab import style_a
    canvas = style_a()
    validate_selected_copy(canvas)
    coverage = canvas.label_layout.finalize()
    typography = canvas.audit_text()
    plt.close(canvas.fig)
    plot = [entry for entry in coverage if entry["zone"] == "plot"]
    if len(plot) != 7 or any(not item["registered"] or item["collisions"] for item in plot):
        raise ValueError("selected 002 label gate failed")
    data.update({"copied_byte_for_byte": True, "plot_text": len(plot),
                 "math_content": "PASS",
                 "uncovered_plot_text": 0, "plot_collisions": 0,
                 "typography": typography, "svg_parse": "PASS"})
    return data


def sheet(path: Path, images, card_width: int, label: str):
    names = (("001", "快记"), ("002", "快懂"), ("003", "快用"))
    gap, margin, head, label_h = 25, 25, 85, 60
    card_h = card_width*4//3
    sheet_image = Image.new("RGB", (margin*2+card_width*3+gap*2,
                                      head+label_h+card_h+margin), "#EAF1F5")
    draw = ImageDraw.Draw(sheet_image)
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font = ImageFont.truetype(str(font_path), 27) if font_path.exists() else ImageFont.load_default()
    draw.text((margin, 20), label, fill="#15375F", font=font)
    for i, ((number, kind), image) in enumerate(zip(names, images)):
        x = margin+i*(card_width+gap)
        draw.text((x, head), f"{number}  {kind}", fill="#15375F", font=font)
        thumb = image.resize((card_width, card_h), Image.Resampling.LANCZOS)
        sheet_image.paste(thumb, (x, head+label_h))
    sheet_image.save(path)


def compare_002():
    width, height = 390, 520
    comp = Image.new("RGB", (width*2+62, height+90), "#EAF1F5")
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font = ImageFont.truetype(str(font_path), 24) if font_path.exists() else ImageFont.load_default()
    draw = ImageDraw.Draw(comp)
    draw.text((20, 22), "已选 A-002", fill="#15375F", font=font)
    draw.text((width+42, 22), "三卡成套版 002", fill="#15375F", font=font)
    for x, path in ((20, SELECTED / "002.png"), (width+42, DEST / "002.png")):
        with Image.open(path) as image:
            comp.paste(image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS),
                       (x, 65))
    comp.save(DEST / "002_selected_vs_final.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace-preview", action="store_true")
    args = parser.parse_args()
    selected = verify_selected()  # Fail before any output if the chosen image vanished.
    formal = validate_formal_sources()
    DEST.mkdir(parents=True, exist_ok=True)
    report = {"uid": "C043", "style": "A Premium Colorful Infographic",
              "status": "THREE-CARD VISUAL REVIEW PENDING", "selected_002": selected,
              "formal_source": formal, "model_math": validation_results(), "cards": {}}
    report["cards"]["001"] = save_checked(card_001(), "001", replace_preview=args.replace_preview)
    report["cards"]["002"] = copy_selected(replace_preview=args.replace_preview)
    report["cards"]["003"] = save_checked(card_003(), "003", replace_preview=args.replace_preview)
    for number in ("001", "002", "003"):
        with Image.open(DEST / f"{number}.png") as image:
            rgb = image.convert("RGB")
        for width in (360, 390):
            rgb.resize((width, width*4//3), Image.Resampling.LANCZOS).save(
                DEST / f"{number}_mobile_{width}.png")
    full = [Image.open(DEST / f"{n}.png").convert("RGB") for n in ("001", "002", "003")]
    mobile = [Image.open(DEST / f"{n}_mobile_360.png").convert("RGB")
              for n in ("001", "002", "003")]
    sheet(DEST / "three_card_contact_sheet.png", full, 540, "C043  /  Style A 三卡成套")
    sheet(DEST / "three_card_mobile_contact_sheet.png", mobile, 360,
          "C043  /  Style A 360px 手机阅读")
    compare_002()
    report["selected_vs_final"] = {"same_png_hash":
                                   sha(SELECTED / "002.png") == sha(DEST / "002.png"),
                                   "comparison_image": "002_selected_vs_final.png"}
    (DEST / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"C043 Style A three-card preview: {DEST}")


if __name__ == "__main__":
    main()
