"""Audit all actual module ZIPs, their source provenance and contentStats."""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.zhishu import module_release


def sample_zip(archive: Path) -> dict:
    """Independent spot check: actual image formats and per-PDF page evidence."""
    m = module_release.m
    with m.temporary_directory() as root:
        m._extract(archive, root)
        manifest = m.read_json(root / "manifest.json")
        nodes = m.read_json(root / "knowledge-nodes.json")
        assets = m.read_json(root / "knowledge-assets.json")
        knowledge = {n["id"] for n in nodes if n["type"] == "knowledge"}
        images, gifs, pdfs = set(), set(), {}
        for row in assets:
            if row["knowledgeId"] not in knowledge:
                raise ValueError("sample resource owner not exported")
            path = root / row["uri"]
            if row["type"] == "pdf":
                pdfs[row["id"]] = m.content_stats.pdf_pages(path)
            else:
                with Image.open(path) as img:
                    (gifs if img.format == "GIF" else images).add(row["id"])
        observed = dict(schemaVersion=1, knowledgeCount=len(knowledge), imageCount=len(images),
                        gifCount=len(gifs), pdfPageCount=sum(pdfs.values()))
        m.require(observed == manifest["contentStats"], f"sample statistics mismatch: {archive.name}")
        return {"zip": archive.name, "status": "PASS", "contentStats": observed,
                "pdfPagesByAssetId": pdfs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--modules", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        index, audit = module_release.audit_modules(args.full, args.modules)
        archives = sorted(args.modules.glob("*.zip"))
        samples = [sample_zip(path) for path in random.SystemRandom().sample(archives, min(3, len(archives)))]
        result = {"status": "PASS", "modules": index["modules"],
                  "contentStats": audit["contentStats"], "audit": audit, "randomSamples": samples}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k in {"status", "error", "contentStats"}}, ensure_ascii=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
