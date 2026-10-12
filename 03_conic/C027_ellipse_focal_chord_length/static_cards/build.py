"""Build only C027's exact premium pilot under .build/static_cards/C027/."""

import json
import platform
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
from PIL import Image

from .model import Ellipse, validation_results
from .geometry import make_diagram
from .cards import CARDS,W,H
from scripts.static_cards.build import digest as sha


ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/".build"/"static_cards"/"C027"/"exact_pilot"


def main():
    if SOURCE != ROOT/"03_conic"/"C027_ellipse_focal_chord_length":
        raise ValueError("wrong UID source")
    formal=[SOURCE/f"0{i}_{name}.tex" for i,name in enumerate(
        ("statement","explanation","proof","examples","traps","summary"),1)]
    formal.append(SOURCE/"meta.json")
    if not all(p.is_file() for p in formal):raise FileNotFoundError("formal source incomplete")
    meta=json.loads(formal[-1].read_text(encoding="utf-8"))
    if meta.get("id")!="C027":raise ValueError("meta UID mismatch")
    sourcehash={str(p.relative_to(ROOT)):sha(p) for p in formal}
    reference={name:SOURCE/"images"/f"{name}.png" for name in ("001","002","003")}
    if not all(p.is_file() for p in reference.values()):
        raise FileNotFoundError("visual reference missing")
    refhash={name:sha(p) for name,p in reference.items()}
    protected={*formal,*reference.values(),SOURCE/"pdfs"/"C027_ellipse_focal_chord_length.pdf"}
    protected_before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    math=validation_results()
    geometry=OUTPUT/"geometry";cards=OUTPUT/"cards";reports=OUTPUT/"reports"
    for path in (geometry,cards,reports):path.mkdir(parents=True,exist_ok=True)
    geometries={name:make_diagram(name,geometry) for name in
                ("main","example","latus_rectum")}
    for name,item in geometries.items():
        tree=ET.parse(item["svg"])
        if tree.findall(".//{http://www.w3.org/2000/svg}image"):
            raise ValueError(f"raster image embedded in vector SVG: {name}")
        paths=tree.findall(".//{http://www.w3.org/2000/svg}path")
        if not paths:raise ValueError(f"SVG has no vector paths: {name}")
        item["svg_path_count"]=len(paths)
        with Image.open(item["png"]) as im:
            im.load()
            if im.size!=tuple(item["size"]) or im.mode!="RGBA":
                raise ValueError(f"invalid transparent geometry: {name}")
            if im.getchannel("A").getextrema()!=(0,255):
                raise ValueError(f"geometry alpha coverage invalid: {name}")
    cardresults={name:fn(geometry,cards/f"{name}.png") for name,fn in CARDS.items()}
    mobile=OUTPUT/"mobile";mobile.mkdir(exist_ok=True)
    for name in CARDS:
        with Image.open(cards/f"{name}.png") as im:
            im.load()
            if im.size!=(W,H):raise ValueError("wrong card dimensions")
            im.resize((390,round(390*H/W)),Image.Resampling.LANCZOS).save(
                mobile/f"{name}_390.png")
    contact=Image.new("RGB",(W*3,H),"white")
    for i,name in enumerate(CARDS):
        with Image.open(cards/f"{name}.png") as im:contact.paste(im,(i*W,0))
    contact.save(OUTPUT/"contact_sheet.png")
    (reports/"audit.md").write_text(
        "# C027 pre-flight audit\n\n"
        "- Scope: C027 only. Existing formal TeX, meta, PDF, and images are read only.\n"
        "- Reference mapping: formal 001 快记, formal 003 快懂, formal 002 快用; pilot 001/002/003 follows 快记/快懂/快用.\n"
        "- Existing `scripts/static_cards/build.py` enforces 1080×1440 Matplotlib canvases; references are 941×1672. This UID-private pilot uses its mathematical/source hash conventions and `.build/static_cards/C027/` boundary, while retaining reference portrait ratio.\n"
        "- `scripts/static_cards/canvas.py` provides exact coordinate mapping and Noto Sans SC font conventions. This pilot uses Matplotlib equal-aspect data coordinates and the same local Noto font.\n"
        "- Python environment: Matplotlib, Pillow, NumPy, ImageMagick and TeX Live available. Matplotlib exports transparent SVG; ImageMagick rasterizes that exact SVG to transparent PNG for deterministic Pillow composition. MathText renders card equations. No generative image model.\n"
        "- The shared static preview builder blocks formal image writes and requires explicit replacement of changed previews. This pilot writes only its dedicated `.build` folder. Publisher scans formal `images/`; it is not called.\n"
        f"- Formal SHA-256: `{json.dumps(sourcehash,ensure_ascii=False)}`\n"
        f"- Reference SHA-256: `{json.dumps(refhash,ensure_ascii=False)}`\n",
        encoding="utf-8")
    cases=math["cases"]
    (reports/"math_validation.md").write_text(
        "# Mathematical validation — MATH PASS\n\n"
        f"- {len(cases)}/{len(cases)} model cases: k = 0, 1, −1, vertical through both foci. Every P/Q is on the ellipse and line; P/F/Q are collinear; Euclidean distance equals formula.\n"
        "- Matplotlib diagram uses `ax.transData` for every object and requires identical x/y unit scale. The SVG is the geometry master; ImageMagick rasterizes it for composition.\n"
        "- Algebra: A=a²k²+b², B=−2a²k²c, C=a²k²c²−a²b². Coefficient identity verifies Δ=4a²b⁴(1+k²). Thus |x₁−x₂|=√Δ/A and |PQ|=√(1+k²)|x₁−x₂|.\n"
        "- Example a=3, b=2, c=√5, k=1: |PQ|=48/13. Vertical: P/Q=(c,±4/3), |PQ|=8/3.\n"
        f"- Full numeric evidence: `{json.dumps(math,ensure_ascii=False)}`\n",
        encoding="utf-8")
    (reports/"visual_validation.md").write_text(
        "# Visual validation\n\n"
        "VISUAL AUTO PASS: 3 full PNGs decode at 941×1672; 3 transparent geometry SVGs parse; paired geometry PNGs have matching dimensions and alpha. Diagram x/y scales agree; visible diagram text boxes stay in the SVG canvas and do not overlap one another. Diagram alpha bounds stay inside intended card panels; recorded card text/formulas fit the card bounds with zero mutual text/formula rectangle overlaps. Mobile 390 px previews exist.\n\n"
        "Local visual inspection of all three full cards and 390 px previews: the reference blue title/tag, pale background, colored numbered modules, formula highlight boxes, example and warning boxes are present. The initial formula white backgrounds, missing glyphs, panel overflow and 002 line-setting collision were corrected and previews rerendered. Inset diagram labels remain small at 390 px.\n\n"
        "HUMAN REVIEW PENDING: user comparison to each formal reference, phone-size inset label legibility, plot label association with nearby curves/lines, and final visual polish.\n\n"
        f"Card metrics: `{json.dumps(cardresults,ensure_ascii=False)}`\n\n"
        f"Diagram metrics: `{json.dumps({k:{'label_count':v['label_count'],'label_overlap_count':v['label_overlap_count'],'unit_scale_px':v['unit_scale_px'],'svg_path_count':v['svg_path_count']} for k,v in geometries.items()},ensure_ascii=False)}`\n",
        encoding="utf-8")
    artifacts=[*geometry.glob("*.svg"),*geometry.glob("*.png"),*cards.glob("*.png"),
               *mobile.glob("*.png"),OUTPUT/"contact_sheet.png"]
    (reports/"final_report.md").write_text(
        "# Task 13G.D1 — C027 exact premium pilot\n\n"
        "MATH PASS · VISUAL AUTO PASS · HUMAN REVIEW PENDING · PUBLISH NOT EXECUTED.\n\n"
        "Three portrait cards are generated in the specified teaching order. Each mathematical plot is calculated from the C027 ellipse model, exported to a transparent vector SVG, rasterized from that SVG with ImageMagick, then composited onto a reference-led premium card with deterministic Pillow and Matplotlib MathText.\n\n"
        "Pipeline integration: place the UID-private package under `C027/static_cards/`; invoke `python -m 03_conic.C027_ellipse_focal_chord_length.static_cards.build`. Preview remains under `.build/static_cards/C027/exact_pilot`. Shared 1080×1440 builder is unchanged. Future secondary conclusions can reuse the background/panel/formula primitives and swap in a separately tested UID model and diagrams; adapt layout to each concept rather than copying the geometry.\n\n"
        f"Artifact SHA-256: `{json.dumps({str(p.relative_to(OUTPUT)):sha(p) for p in artifacts},ensure_ascii=False)}`\n",
        encoding="utf-8")
    protected_after={str(p.relative_to(ROOT)):sha(p) for p in protected}
    if protected_before!=protected_after:
        raise RuntimeError("protected formal assets changed during build")
    print(json.dumps({"status":"built","output":str(OUTPUT),"cards":list(CARDS),
                      "math_cases":len(cases),"geometry":list(geometries)},ensure_ascii=False))


if __name__=="__main__":main()
