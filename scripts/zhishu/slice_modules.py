"""Deterministically slice two pilot packages; never invokes Publisher or Sync."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__:
    from .module_package import ModuleError, slice_modules
else:
    from module_package import ModuleError, slice_modules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--modules", default="sets,analytic-geometry")
    parser.add_argument("--package-version", type=int, default=1)
    args = parser.parse_args()
    try:
        results = slice_modules(args.input, args.output, args.modules.split(","), args.package_version)
    except (ModuleError, OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"MODULE PACKAGE FAILED: {exc}\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
