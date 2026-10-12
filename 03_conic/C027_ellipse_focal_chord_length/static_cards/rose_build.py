"""One-command C027 exact rose preview; never writes formal images/."""

import hashlib
import json
import platform
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
from PIL import Image

from .model import Ellipse, validation_results
from .rose_geometry import draw
from .rose_cards import CARDS, W, H


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1]
OUT = ROOT / ".build" / "static_cards" / "C027" / "rose_exact"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if SOURCE.name != "C027_ellipse_focal_chord_length":
        raise ValueError("wrong UID")
    names = ("statement", "explanation", "proof", "examples", "traps", "summary")
    formal = [SOURCE / f"0{i}_{name}.tex" for i, name in enumerate(names, 1)]
    formal.append(SOURCE / "meta.json")
    if json.loads(formal[-1].read_text(encoding="utf-8"))["id"] != "C027":
        raise ValueError("meta UID mismatch")
    references = [SOURCE / "images" / f"{n}.png" for n in ("001", "002", "003")]
    protected = formal + references
    before = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    math = validation_results()
    example = Ellipse(3, 3**.5).validate_case(1, 1)
    assert abs(example["distance"] - 3) < 1e-11
    diagrams_dir = OUT / "geometry"
    cards_dir = OUT / "cards"
    mobile_dir = OUT / "mobile"
    for path in (diagrams_dir, cards_dir, mobile_dir):
        path.mkdir(parents=True, exist_ok=True)
    diagrams = {kind: draw(kind, diagrams_dir)
                for kind in ("general", "example", "vertical")}
    for item in diagrams.values():
        svg = ET.parse(item["svg"])
        if svg.findall(".//{http://www.w3.org/2000/svg}image"):
            raise ValueError("vector diagram embeds a raster")
        with Image.open(item["png"]) as im:
            im.load()
            if im.mode != "RGBA" or im.getchannel("A").getextrema() != (0, 255):
                raise ValueError("geometry transparency invalid")
    card_metrics = {}
    for number, render in CARDS.items():
        dest = cards_dir / f"{number}.png"
        card_metrics[number] = render(diagrams_dir, dest)
        with Image.open(dest) as im:
            im.load()
            if im.size != (W, H):
                raise ValueError("card dimensions invalid")
            im.resize((390, round(H*390/W)), Image.Resampling.LANCZOS).save(
                mobile_dir / f"{number}_390.png", optimize=True)
    contact = Image.new("RGB", (W*3, H), "white")
    for i, number in enumerate(CARDS):
        with Image.open(cards_dir / f"{number}.png") as im:
            contact.paste(im, (i*W, 0))
    contact.save(OUT / "contact_sheet.png", optimize=True)
    source_files = formal + [Path(__file__), SOURCE / "static_cards" / "rose_cards.py",
                            SOURCE / "static_cards" / "rose_geometry.py",
                            SOURCE / "static_cards" / "model.py",
                            SOURCE / "static_cards" / "cards.py"]
    outputs = sorted([*diagrams_dir.iterdir(), *cards_dir.iterdir(),
                      *mobile_dir.iterdir(), OUT / "contact_sheet.png"])
    report = {
        "uid": "C027", "status": "PREVIEW_VALIDATED",
        "command": "python -m 03_conic.C027_ellipse_focal_chord_length.static_cards.rose_build",
        "size": [W, H], "preview_only": True,
        "inputs_sha256": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
        "reference_sha256": {str(p.relative_to(ROOT)): digest(p) for p in references},
        "outputs_sha256": {str(p.relative_to(OUT)): digest(p) for p in outputs},
        "math_cases": len(math["cases"]) + 1,
        "example_distance": example["distance"],
        "diagrams": diagrams, "cards": card_metrics,
        "environment": {"python": platform.python_version(),
                        "matplotlib": matplotlib.__version__},
        "gates": {"math": "PASS", "technical": "PASS",
                  "visual_local": "PENDING", "user_visual": "PENDING",
                  "formal_publish": "NOT_EXECUTED"},
    }
    (OUT / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    after = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    if after != before:
        raise RuntimeError("formal inputs or existing images changed")
    print(json.dumps({"status": "PREVIEW_VALIDATED", "output": str(OUT),
                      "math_cases": report["math_cases"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
