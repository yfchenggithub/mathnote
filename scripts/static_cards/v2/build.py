"""Build only isolated V2 previews for one explicitly selected UID."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path
from uuid import uuid4

import matplotlib
from PIL import Image

from scripts.static_cards.canvas import HEIGHT, WIDTH
from scripts.static_cards.build import contact_sheet
from scripts.static_cards.labels import CollisionFailure


ROOT = Path(__file__).resolve().parents[3]
BUILD_ROOT = ROOT / ".build" / "static_cards_v2"
FORMAL = ("01_statement.tex", "02_explanation.tex", "03_proof.tex",
          "04_examples.tex", "05_traps.tex", "06_summary.tex", "meta.json")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source_data(source):
    paths = [source / name for name in FORMAL]
    if not all(path.is_file() for path in paths):
        raise ValueError("formal C043 source is incomplete")
    if json.loads(paths[-1].read_text(encoding="utf-8")).get("id") != "C043":
        raise ValueError("formal UID mismatch")
    return ({str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
             for path in paths},
            {path.name: path.read_text(encoding="utf-8") for path in paths[:-1]})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uid", required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--replace-preview", action="store_true")
    args = parser.parse_args(argv)
    if args.uid != "C043":
        parser.error("this V2 pilot is scoped to C043")
    source = (ROOT / args.source_dir).resolve()
    if source != ROOT / "03_conic" / "C043_hyperbola_abc_relation":
        parser.error("source-dir must identify the exact C043 directory")
    output = BUILD_ROOT / args.uid
    cards = load_file("_c043_v2_cards", source / "static_cards_v2" / "cards.py")
    model = load_file("_c043_v1_model_for_v2", source / "static_cards" / "model.py")
    source_hashes, texts = source_data(source)
    content_checks = cards.validate_content(texts)
    math_checks = model.validation_results()
    if not all(x == "PASS" for x in math_checks.values()):
        raise ValueError("C043 mathematical model validation failed")
    implementation = sorted((ROOT / "scripts" / "static_cards" / "v2").glob("*.py"))
    implementation += sorted((source / "static_cards_v2").glob("*.py"))
    implementation += [source / "static_cards" / "model.py",
                       ROOT / "scripts" / "static_cards" / "canvas.py",
                       ROOT / "scripts" / "static_cards" / "labels.py"]
    implementation_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
                             for p in implementation}
    output.mkdir(parents=True, exist_ok=True)
    stage = output / ("_stage_" + uuid4().hex)
    stage.mkdir()
    label_layout, coverage, text_audits = [], [], {}
    try:
        for number in sorted(cards.SPECS):
            canvas = cards.draw_card(number, model.Hyperbola)
            if canvas.label_layout is not None:
                canvas.label_layout.finalize()
                coverage.extend({"card": number, **entry}
                                for entry in canvas.text_coverage_report)
            required = cards.LABEL_GATE_REQUIRED.get(number, set())
            found = {item["label"] for item in canvas.layout_report
                     if item["status"] == "PASS"}
            if required - found:
                raise ValueError(f"missing semantic labels: {number}: {required - found}")
            label_layout.extend({"card": number, **entry}
                                for entry in canvas.layout_report)
            text_audits[number] = canvas.text_collision_audit()
            canvas.export(stage / f"{number}.png", stage / f"{number}.svg")
            with Image.open(stage / f"{number}.png") as image:
                image.load()
                if image.size != (WIDTH, HEIGHT):
                    raise ValueError(f"wrong output size: {number}")
        contact_sheet([stage / f"{number}.png" for number in sorted(cards.SPECS)],
                      stage / "contact_sheet.png")
        for file in stage.iterdir():
            target = output / file.name
            if target.exists() and digest(target) != digest(file) and not args.replace_preview:
                raise FileExistsError(f"different V2 preview exists: {target}")
        for file in stage.iterdir():
            target = output / file.name
            if not target.exists() or digest(target) != digest(file):
                file.replace(target)
        report = {
            "uid": args.uid, "status": cards.REVIEW_STATUS,
            "math_gate": "PASS", "content_gate": content_checks,
            "render_gate": "PASS", "math_checks": math_checks,
            "label_layout": label_layout, "text_coverage": coverage,
            "uncovered_text": [x for x in coverage if x["zone"] == "plot"
                               and not x["registered"] and not x["exemption"]],
            "text_audit": text_audits,
            "source_sha256": source_hashes,
            "implementation_sha256": implementation_hashes,
            "versions": {"python": platform.python_version(),
                         "matplotlib": matplotlib.__version__,
                         "pillow": Image.__version__},
            "output_sha256": {name: digest(output / name)
                              for name in [*(f"{n}.{ext}" for n in sorted(cards.SPECS)
                                             for ext in ("png", "svg")),
                                           "contact_sheet.png"]},
        }
        (output / "build_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"output": str(output), "status": report["status"],
                          "math_gate": "PASS", "render_gate": "PASS"}, ensure_ascii=False))
    except CollisionFailure as exc:
        (output / "build_report.json").write_text(json.dumps({
            "uid": args.uid, "status": "BLOCKED", "math_gate": "PASS",
            "render_gate": exc.report["status"], "failure": exc.report,
            "source_sha256": source_hashes,
            "implementation_sha256": implementation_hashes,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    finally:
        for file in stage.iterdir():
            file.unlink()
        stage.rmdir()


if __name__ == "__main__":
    main()
