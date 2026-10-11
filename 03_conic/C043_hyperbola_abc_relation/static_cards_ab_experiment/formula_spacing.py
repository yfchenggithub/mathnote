"""The C043-002 equation capsule/MathText clearance gate."""

from __future__ import annotations

from scripts.static_cards.canvas import HEIGHT


class FormulaSpacingError(ValueError):
    pass


def _rect(artist, renderer):
    box = artist.get_window_extent(renderer)
    return {"left": round(float(box.x0), 3), "top": round(float(HEIGHT-box.y1), 3),
            "right": round(float(box.x1), 3), "bottom": round(float(HEIGHT-box.y0), 3)}


def _overlap(a, b):
    width = max(0, min(a["right"], b["right"])-max(a["left"], b["left"]))
    height = max(0, min(a["bottom"], b["bottom"])-max(a["top"], b["top"]))
    return round(width*height, 3)


def measure_standard_equation(canvas):
    """Measure registered final-renderer artists, in top-left-origin pixels."""
    canvas.fig.canvas.draw()
    renderer = canvas.fig.canvas.get_renderer()
    panel, capsule, title, formula = canvas.standard_equation
    p, c, t, f = [_rect(x, renderer) for x in (panel, capsule, title, formula)]
    return {
        "panel": p, "capsule_background": c, "capsule_title": t, "formula": f,
        "capsule_formula_gap_px": round(f["top"]-c["bottom"], 3),
        "title_formula_gap_px": round(f["top"]-t["bottom"], 3),
        "capsule_formula_bbox_overlap_px2": _overlap(c, f),
        "title_formula_bbox_overlap_px2": _overlap(t, f),
        "formula_bottom_panel_clearance_px": round(p["bottom"]-f["bottom"], 3),
        "formula_top_panel_clearance_px": round(f["top"]-p["top"], 3),
        "formula_font_pt": formula.get_fontsize(),
        "canvas_dpi": canvas.fig.dpi,
    }


def check_standard_equation(canvas, *, min_gap_px=8, min_panel_clearance_px=3):
    result = measure_standard_equation(canvas)
    if result["capsule_formula_gap_px"] < min_gap_px:
        raise FormulaSpacingError(
            "standard equation capsule background / MathText formula: "
            f"gap {result['capsule_formula_gap_px']:.3f}px < {min_gap_px}px")
    if result["title_formula_gap_px"] < min_gap_px:
        raise FormulaSpacingError(
            "standard equation capsule title / MathText formula: "
            f"gap {result['title_formula_gap_px']:.3f}px < {min_gap_px}px")
    if result["formula_bottom_panel_clearance_px"] < min_panel_clearance_px or \
            result["formula_top_panel_clearance_px"] < min_panel_clearance_px:
        raise FormulaSpacingError("standard equation MathText formula exceeds panel clearance")
    if result["formula"]["left"] < result["panel"]["left"] or \
            result["formula"]["right"] > result["panel"]["right"]:
        raise FormulaSpacingError("standard equation MathText formula exceeds panel width")
    return result
