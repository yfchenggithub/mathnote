"""Isolated 13G.4V.3B.1 rebuild; preserve the original A/B artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
from PIL import Image, ImageChops

import build as original
from cards import card_002
from formula_spacing import check_standard_equation, measure_standard_equation


ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / ".build/static_cards_ab_experiment/C043"
DEST = ROOT / ".build/static_cards_ab_experiment_fix/C043"
PROTECTED_PREVIEWS = [
    OLD,
    ROOT / ".build/static_cards_style_a/C043",
    ROOT / ".build/static_cards_style_a_polish/C043",
    ROOT / ".build/static_cards_style_lab/C043",
]


def preview_hashes():
    result = {}
    for directory in PROTECTED_PREVIEWS:
        if not directory.is_dir():
            raise FileNotFoundError(f"protected preview directory missing: {directory}")
        for path in directory.rglob("*"):
            if path.is_file():
                result[str(path.relative_to(ROOT))] = original.sha(path)
    return result


def reconstructed_old_layout(name):
    """Restore only the prior four layout coordinates for measured reproduction."""
    canvas = card_002(name)
    panel, capsule, title, _ = canvas.standard_equation
    panel.set_y(255)
    panel.set_height(145)
    capsule.set_y(266)
    title.set_y(293)
    return canvas


def audited(canvas):
    quality = original_audit(canvas)
    quality["standard_equation_spacing"] = check_standard_equation(canvas)
    return quality


def changed_pixel_bounds(old_path, new_path):
    with Image.open(old_path) as im:
        before = im.convert("RGB")
    with Image.open(new_path) as im:
        after = im.convert("RGB")
    if before.size != after.size or before.size != (1080, 1440):
        raise ValueError("before/after canvas size changed")
    bounds = ImageChops.difference(before, after).getbbox()
    if bounds is None or bounds[1] < 230 or bounds[3] > 410:
        raise ValueError(f"change escaped standard equation module: {bounds}")
    return list(bounds)


def main():
    preview_before = preview_hashes()
    formal_before = original.verify_protected()
    old_report = json.loads((OLD / "build_report.json").read_text(encoding="utf-8"))
    before = {}
    for name in ("A_blue", "B_rose"):
        before[name] = measure_standard_equation(reconstructed_old_layout(name))
        if before[name]["capsule_formula_gap_px"] >= 0:
            raise ValueError(f"old {name} overlap did not reproduce")

    original.DEST = DEST
    original.audit = audited
    original.main()
    report_path = DEST / "build_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["task"] = "13G.4V.3B.1"
    report["status"] = "A/B VISUAL REVIEW PENDING"
    report["original_ab_sha256"] = preview_before
    report["before_after_changed_pixel_bounds"] = {}
    for name in ("A_blue", "B_rose"):
        old_sig = old_report["themes"][name]["signature"]
        new_sig = report["themes"][name]["signature"]
        if old_sig["math_geometry"] != new_sig["math_geometry"] or \
                old_sig["labels"] != new_sig["labels"] or \
                old_sig["text_count"] != new_sig["text_count"]:
            raise ValueError(f"{name} mathematical diagram or content count changed")
        report["before_after_changed_pixel_bounds"][name] = changed_pixel_bounds(
            OLD / name / "002.png", DEST / name / "002.png")
        original.sheet(DEST / ("blue_before_after.png" if name == "A_blue" else
                               "rose_before_after.png"),
                       [("修复前", OLD/name/"002.png"),
                        ("修复后", DEST/name/"002.png")], 540,
                       f"C043-002  /  {name} 标准方程修复前后")

    preview_after = preview_hashes()
    formal_after = original.verify_protected()
    if preview_before != preview_after or formal_before != formal_after:
        raise ValueError("protected preview or formal freeze changed")
    report["protected_preview_regression"] = "PASS"
    report["frozen_formal_regression"] = "PASS"
    report["protected_preview_count"] = len(preview_before)
    overlap = {
        "status": "PASS", "measurement": "final Matplotlib renderer artist bounding boxes",
        "environment": {"matplotlib": matplotlib.__version__,
                        "backend": matplotlib.get_backend(), "dpi": 100,
                        "mathtext_fontset": matplotlib.rcParams["mathtext.fontset"],
                        "chinese_font_file": card_002("A_blue").standard_equation[2]
                        .get_fontproperties().get_file()},
        "thresholds_px": {"capsule_formula": 8, "title_formula": 8,
                          "formula_panel": 3},
        "old_typography_gate": {name: old_report["themes"][name]["quality"]["typography"]
                                for name in ("A_blue", "B_rose")},
        "themes": {name: {"before": before[name],
                          "after": report["themes"][name]["quality"]["standard_equation_spacing"]}
                   for name in ("A_blue", "B_rose")},
    }
    (DEST / "layout_overlap_report.json").write_text(
        json.dumps(overlap, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(DEST), "capsule_formula_gap_px":
                      {name: overlap["themes"][name]["after"]["capsule_formula_gap_px"]
                       for name in ("A_blue", "B_rose")},
                      "protected_preview_count": len(preview_before)}, ensure_ascii=False))


original_audit = original.audit

if __name__ == "__main__":
    main()
