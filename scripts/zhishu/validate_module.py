"""Validate one independent module ZIP/directory, optionally against Full v2."""
from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .module_package import validate_module
else:
    from module_package import validate_module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    issues = validate_module(args.package, args.source)
    for issue in issues:
        print(f"FAIL: {issue}")
    if not issues:
        print(f"MODULE PACKAGE PASS: {args.package.resolve()}")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
