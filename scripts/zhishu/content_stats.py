"""Export-time statistics over registered, actually packaged knowledge resources."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

FIELDS = {"schemaVersion", "knowledgeCount", "imageCount", "gifCount", "pdfPageCount"}


def validate(value: object) -> None:
    if (not isinstance(value, dict) or set(value) != FIELDS
            or any(type(v) is not int or not 0 <= v <= 2**53 - 1 for v in value.values())
            or value["schemaVersion"] != 1):
        raise ValueError("invalid/missing contentStats (expected schema 1 nonnegative integers)")


def pdf_pages(path: Path) -> int:
    """Read the actual page tree with Poppler; errors never become zero pages."""
    executable = shutil.which(os.environ.get("PDFINFO_BINARY", "pdfinfo"))
    if not executable:
        raise ValueError("contentStats requires Poppler pdfinfo on PATH (or PDFINFO_BINARY)")
    try:
        result = subprocess.run([executable, str(path.resolve())], capture_output=True,
                                timeout=60, env={**os.environ, "LC_ALL": "C", "LANG": "C"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"PDF page parsing failed: {path}: {exc}") from exc
    match = re.search(rb"^Pages:\s*([0-9]+)\s*$", result.stdout, re.MULTILINE)
    # Treat parser diagnostics as a failure, including recovered malformed PDFs.
    if result.returncode or result.stderr.strip() or not match or int(match[1]) <= 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"PDF page parsing failed: {path}: {detail or 'missing valid Pages'}")
    return int(match[1])


def calculate(root: Path, data: dict) -> dict[str, int]:
    knowledge = {r["id"] for r in data["knowledgeNodes"] if r["type"] == "knowledge"}
    assets = {}
    for row in data["knowledgeAssets"]:
        if row["knowledgeId"] not in knowledge:
            raise ValueError(f"contentStats asset has no exported knowledge owner: {row['id']}")
        previous = assets.setdefault(row["id"], row)
        if previous != row:
            raise ValueError(f"contentStats conflicting asset ID: {row['id']}")
    images = gifs = pages = 0
    for row in assets.values():
        path = root / row["uri"]
        if row["type"] == "pdf":
            pages += pdf_pages(path)
        elif row["type"] == "image":
            # These are formal KnowledgeAsset records, never directory scans of
            # covers, app icons, share cards, video previews or temporary files.
            if path.suffix.lower() == ".gif":
                gifs += 1
            else:
                images += 1
        else:
            raise ValueError(f"contentStats unknown asset type: {row['type']}")
    result = dict(schemaVersion=1, knowledgeCount=len(knowledge), imageCount=images,
                  gifCount=gifs, pdfPageCount=pages)
    validate(result)
    return result
