"""Preview-only static card builder with an exact UID source directory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
from uuid import uuid4

import matplotlib
from PIL import Image, ImageOps

from .canvas import HEIGHT, WIDTH
from .labels import CollisionFailure, save_debug_preview


ROOT = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_source(source_dir: Path, uid: str):
    source_dir = source_dir.resolve()
    if not source_dir.is_dir() or not source_dir.name.startswith(uid + "_"):
        raise ValueError("source directory must be the exact requested UID")
    if not source_dir.is_relative_to(ROOT):
        raise ValueError("source directory must be within the project")
    file = source_dir / "static_cards" / "__init__.py"
    if not file.is_file():
        raise ValueError("UID static card package is missing")
    name = f"_mathnote_static_{uid}"
    spec = importlib.util.spec_from_file_location(name, file,
                                                    submodule_search_locations=[str(file.parent)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return __import__(f"{name}.cards", fromlist=["SPECS", "draw_card", "MODEL"]), \
        __import__(f"{name}.model", fromlist=["validation_results"])


def verify_sources(source_dir: Path, specs: dict):
    source_files = [source_dir / f"0{i}_{n}.tex" for i, n in enumerate(
        ("statement", "explanation", "proof", "examples", "traps", "summary"), 1)]
    source_files.append(source_dir / "meta.json")
    if not all(p.is_file() for p in source_files):
        raise ValueError("formal source files are incomplete")
    meta = json.loads(source_files[-1].read_text(encoding="utf-8"))
    if meta.get("id") != next(iter(specs.values()))["uid"]:
        raise ValueError("UID and meta.json disagree")
    hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in source_files}
    texts = {p.name: p.read_text(encoding="utf-8") for p in source_files[:-1]}
    return hashes, texts


def contact_sheet(paths: list[Path], output: Path):
    thumb_width = 360
    thumb_height = round(HEIGHT * thumb_width / WIDTH)
    sheet = Image.new("RGB", (thumb_width * len(paths), thumb_height), "white")
    for i, path in enumerate(paths):
        with Image.open(path) as im:
            if im.size != (WIDTH, HEIGHT):
                raise ValueError(f"wrong dimensions: {path}")
            im.verify()
        with Image.open(path) as im:
            thumb = ImageOps.contain(im.convert("RGB"), (thumb_width, thumb_height))
            sheet.paste(thumb, (i * thumb_width, 0))
    sheet.save(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uid", required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--card", action="append", help="card number from the UID specification")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--replace-preview", action="store_true")
    parser.add_argument("--debug-layout", action="store_true",
                        help="write preview-only measured label boxes")
    args = parser.parse_args(argv)
    source_dir = (ROOT / args.source_dir).resolve()
    output = (args.output or ROOT / ".build" / "static_cards" / args.uid).resolve()
    if not output.is_relative_to(ROOT / ".build" / "static_cards"):
        parser.error("preview output must remain under .build/static_cards")
    if output.name != args.uid:
        parser.error("preview output directory must end in the exact UID")
    cards, model = load_source(source_dir, args.uid)
    chosen = sorted(set(args.card or cards.SPECS))
    if any(number not in cards.SPECS for number in chosen):
        parser.error(f"unknown card number; available: {', '.join(sorted(cards.SPECS))}")
    if any(cards.SPECS[n]["uid"] != args.uid for n in chosen):
        raise ValueError("card UID mismatch")
    source_hashes, formal_texts = verify_sources(source_dir, cards.SPECS)
    content_gate = cards.validate_content(formal_texts)
    implementation_files = sorted((ROOT / "scripts" / "static_cards").glob("*.py"))
    implementation_files += sorted((source_dir / "static_cards").glob("*.py"))
    implementation_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
        for path in implementation_files
    }
    checks = model.validation_results()
    if not all(v == "PASS" for v in checks.values()):
        raise ValueError("mathematics gate failed")
    if args.validate_only:
        print(json.dumps({"uid": args.uid, "mathematics": checks, "content": content_gate},
                         ensure_ascii=False, indent=2))
        return
    output.mkdir(parents=True, exist_ok=True)
    stage = output / ("_stage_" + uuid4().hex)
    stage.mkdir()
    layout_checks = []
    try:
        for number in chosen:
            canvas = cards.draw_card(number)
            required = getattr(cards, "LABEL_GATE_REQUIRED", {}).get(number, set())
            found = {item["label"] for item in canvas.layout_report if item["status"] == "PASS"}
            if required - found:
                raise CollisionFailure({"uid": args.uid, "card": number,
                                        "label": ", ".join(sorted(required - found)),
                                        "collisions": [{"object": "label registration",
                                                        "type": "missing", "clearance_px": 0}],
                                        "attempted": [], "status": "COLLISION_FAIL"})
            layout_checks.extend(canvas.layout_report)
            if args.debug_layout and canvas.layout_report:
                save_debug_preview(canvas, stage / f"{number}_layout_debug.png")
            canvas.export(stage / f"{number}.png", stage / f"{number}.svg")
            with Image.open(stage / f"{number}.png") as image:
                image.load()
                if image.size != (WIDTH, HEIGHT):
                    raise ValueError(f"incorrect PNG size: {number}")
        all_cards = sorted(cards.SPECS)
        sheet_inputs = [stage / f"{n}.png" if n in chosen else output / f"{n}.png"
                        for n in all_cards]
        if all(path.is_file() for path in sheet_inputs):
            contact_sheet(sheet_inputs, stage / "contact_sheet.png")
        for item in stage.iterdir():
            destination = output / item.name
            if destination.exists() and digest(destination) != digest(item) and not args.replace_preview:
                raise FileExistsError(f"preview exists with different content: {destination}; use --replace-preview")
        for item in stage.iterdir():
            destination = output / item.name
            if not destination.exists() or digest(destination) != digest(item):
                item.replace(destination)
    except CollisionFailure as exc:
        failure_report = {"uid": args.uid, "selected_cards": chosen,
                          "status": "COLLISION_FAIL", "math_gate": "PASS",
                          "render_gate": "COLLISION_FAIL", "failure_reason": str(exc),
                          "label_layout": layout_checks + [exc.report],
                          "source_sha256": source_hashes,
                          "implementation_sha256": implementation_hashes}
        (output / "build_report.json").write_text(
            json.dumps(failure_report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    finally:
        for item in stage.iterdir():
            item.unlink()
        stage.rmdir()
    report = {
        "uid": args.uid, "selected_cards": chosen,
        "status": getattr(cards, "REVIEW_STATUS", "PILOT A VISUAL REVIEW PENDING"),
        "content_gate": content_gate, "math_gate": "PASS", "render_gate": "PASS",
        "failure_reason": None,
        "label_layout": layout_checks,
        "math_checks": checks,
        "terminology": getattr(cards, "TERMINOLOGY_REVIEW",
                               "REVIEW: formal TeX calls p/2 半通径; for y²=2px the conventional semilatus rectum is p. Cards say p/2."),
        "source_sha256": source_hashes,
        "implementation_sha256": implementation_hashes,
        "versions": {"python": platform.python_version(), "matplotlib": matplotlib.__version__,
                     "pillow": Image.__version__},
        "output_sha256": {p.name: digest(p) for p in sorted(output.iterdir())
                          if p.suffix in {".png", ".svg"}},
    }
    (output / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "cards": chosen, "math_gate": "PASS",
                      "status": report["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
