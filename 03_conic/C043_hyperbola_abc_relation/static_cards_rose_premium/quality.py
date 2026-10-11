"""Measured formula clearance for the two new Rose cards."""

from __future__ import annotations

from static_cards_ab_experiment.formula_spacing import _rect, _overlap


class FormulaRegionError(ValueError):
    pass


def check_formula_regions(canvas, *, min_gap=8, min_panel_clearance=3):
    canvas.fig.canvas.draw()
    renderer = canvas.fig.canvas.get_renderer()
    report = []
    for region in canvas.formula_regions:
        panel = _rect(region["panel"], renderer)
        capsule = _rect(region["capsule"], renderer)
        title = _rect(region["title"], renderer)
        if title["left"]-capsule["left"] < 10 or \
                capsule["right"]-title["right"] < 10 or \
                title["top"] < capsule["top"] or title["bottom"] > capsule["bottom"]:
            raise FormulaRegionError(f"{region['name']}: capsule title exceeds background")
        formulas = [_rect(f, renderer) for f in region["formulas"]]
        if not formulas:
            raise FormulaRegionError(f"{region['name']}: no formula registered")
        gaps = []
        for index, formula in enumerate(formulas):
            capsule_gap = round(formula["top"]-capsule["bottom"], 3)
            title_gap = round(formula["top"]-title["bottom"], 3)
            if _overlap(capsule, formula) or capsule_gap < min_gap:
                raise FormulaRegionError(
                    f"{region['name']}: capsule background / formula {index+1} "
                    f"gap {capsule_gap}px < {min_gap}px")
            if _overlap(title, formula) or title_gap < min_gap:
                raise FormulaRegionError(
                    f"{region['name']}: capsule title / formula {index+1} "
                    f"gap {title_gap}px < {min_gap}px")
            clearances = (formula["top"]-panel["top"],
                          panel["bottom"]-formula["bottom"],
                          formula["left"]-panel["left"],
                          panel["right"]-formula["right"])
            if min(clearances) < min_panel_clearance:
                raise FormulaRegionError(
                    f"{region['name']}: formula {index+1} exceeds panel clearance")
            if "highlight" in region:
                highlight = _rect(region["highlight"], renderer)
                if min(formula["top"]-highlight["top"],
                       highlight["bottom"]-formula["bottom"],
                       formula["left"]-highlight["left"],
                       highlight["right"]-formula["right"]) < min_panel_clearance:
                    raise FormulaRegionError(
                        f"{region['name']}: formula {index+1} exceeds highlight clearance")
            gaps.append({"formula": index+1, "capsule_gap_px": capsule_gap,
                         "title_gap_px": title_gap,
                         "panel_bottom_clearance_px": round(clearances[1], 3)})
        for first, second in zip(formulas, formulas[1:]):
            if min(first["right"], second["right"]) > max(first["left"], second["left"]):
                if second["top"]-first["bottom"] < min_gap:
                    raise FormulaRegionError(
                        f"{region['name']}: adjacent formula rows too close")
        report.append({"name": region["name"], "panel": panel, "capsule": capsule,
                       "title": title, "formulas": formulas, "gaps": gaps})
    for capsule_artist, title_artist in getattr(canvas, "extra_capsules", ()):
        capsule, title = _rect(capsule_artist, renderer), _rect(title_artist, renderer)
        if title["left"]-capsule["left"] < 10 or \
                capsule["right"]-title["right"] < 10 or \
                title["top"] < capsule["top"] or title["bottom"] > capsule["bottom"]:
            raise FormulaRegionError("diagram capsule title exceeds background")
    return report
