"""Run the existing image worker on a R028-only isolated GIF copy."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
UID = ROOT / "06_probability-stat" / "R028_bayes_formula"
BUILD = ROOT / "build" / "manim" / "R028"
ASSET_NAME = "r028_bayes_formula.gif"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = Path(sys.argv[1]).resolve(strict=True)
    staged = (BUILD / "bayes_formula" / "bayes_formula.gif").resolve()
    formal = (UID / "images" / ASSET_NAME).resolve()
    if source not in (staged, formal):
        raise ValueError("preview source must be R028's staged or formal GIF")
    record = json.loads((UID / "meta.json").read_text(encoding="utf-8"))
    if record["id"] != "R028":
        raise ValueError("R028 metadata id mismatch")
    BUILD.mkdir(parents=True, exist_ok=True)
    preview = (BUILD / f"publisher-preview-{uuid.uuid4().hex}").resolve()
    if BUILD.resolve() not in preview.parents:
        raise ValueError("preview path escapes R028 build root")
    preview.mkdir()
    if source == formal:
        input_dir = formal.parent
        input_gif = formal
    else:
        input_dir = preview / "input"
        input_dir.mkdir()
        input_gif = input_dir / ASSET_NAME
        shutil.copyfile(source, input_gif)
    jobs = {"sources": [{
        "knowledgeId": "R028",
        "sourceDirectory": str(input_dir),
        "displayDirectory": "06_probability-stat/R028_bayes_formula/images",
    }]}
    jobs_path = preview / "jobs.json"
    jobs_path.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    output = preview / "output"
    worker = ROOT / "scripts" / "zhishu" / "prepare_knowledge_images.mjs"
    result = subprocess.run(["node", str(worker), "--jobs", str(jobs_path),
                             "--output", str(output)], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assets = manifest["assets"]
    if len(assets) != 1:
        raise AssertionError("isolated preview must contain only R028's GIF")
    asset = assets[0]
    expected = "images/R028/r028_bayes_formula.gif"
    runtime_gif = output / expected
    with Image.open(source) as gif:
        frame_count = gif.n_frames
    if not (asset["knowledgeId"] == "R028"
            and asset["source"] == "06_probability-stat/R028_bayes_formula/images/r028_bayes_formula.gif"
            and asset["output"] == expected
            and asset["frameCount"] == frame_count
            and asset["loop"] == 0
            and runtime_gif.is_file()
            and digest(source) == digest(input_gif) == digest(runtime_gif)
            == asset["sourceSha256"] == asset["outputSha256"]):
        raise AssertionError("Publisher GIF compatibility mismatch")
    print(result.stdout.strip())
    print(json.dumps({"preview": str(preview), "runtime_asset": str(runtime_gif),
                      "frames": frame_count, "sha256": digest(source),
                      "mapping": expected, "pass": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
