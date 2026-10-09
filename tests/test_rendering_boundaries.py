"""Small, conservative source-level guard for the rendering production lines."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "00_set", "01_function", "02_sequence", "03_conic", "04_vector",
    "05_geometry-solid", "06_probability-stat", "07_inequality",
    "08_trigonometry", "09_geometry-plane", "10_junior_basics",
)
LINES = ("manim", "static_cards")


def production_sources(root: Path = ROOT):
    for line in LINES:
        shared = root / "scripts" / line
        if shared.is_dir():
            for path in shared.rglob("*"):
                if path.suffix.lower() in {".py", ".ps1"} and path.is_file():
                    yield line, "shared", path
    for module in MODULES:
        base = root / module
        if not base.is_dir():
            continue
        for uid in base.iterdir():
            if not uid.is_dir() or not re.match(r"^[A-Z][0-9]{3}_", uid.name):
                continue
            for line in LINES:
                source = uid / line
                if source.is_dir():
                    for path in source.rglob("*"):
                        if path.suffix.lower() in {".py", ".ps1"} and path.is_file():
                            yield line, uid.name, path


def violations(line: str, owner: str, path: Path) -> list[str]:
    other = "static_cards" if line == "manim" else "manim"
    content = path.read_text(encoding="utf-8-sig")
    errors = []
    if path.suffix.lower() == ".py":
        tree = ast.parse(content, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                names = []
            if any(other in name.split(".") for name in names):
                errors.append(f"line {node.lineno}: cross-module import")
            if owner != "shared" and any(
                re.search(r"^[A-Z][0-9]{3}_", part) and part != owner
                for name in names for part in name.split(".")
            ):
                errors.append(f"line {node.lineno}: cross-UID private import")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                # Inspect literal arguments to known process entry points, not arbitrary text.
                if node.func.attr in {"run", "Popen", "call", "check_call", "check_output", "system"}:
                    literals = [value.value for value in ast.walk(node)
                                if isinstance(value, ast.Constant) and isinstance(value.value, str)]
                    if any(re.search(rf"(?:scripts[/\\])?{other}[/\\].*\.(?:ps1|py)\b", s, re.I)
                           for s in literals):
                        errors.append(f"line {node.lineno}: cross-module build call")
    else:
        for number, raw in enumerate(content.splitlines(), 1):
            code = raw.split("#", 1)[0]
            if re.search(rf"\b(?:scripts[/\\])?{other}[/\\][^\s'\"]+\.(?:ps1|py)\b", code, re.I):
                errors.append(f"line {number}: cross-module script reference")
    if owner == "shared" and line == "static_cards":
        for number, raw in enumerate(content.splitlines(), 1):
            if re.search(r"(?:0[0-9]|10)_[\w-]+[/\\][A-Z][0-9]{3}_[\w-]+", raw):
                errors.append(f"line {number}: shared static tool references a UID implementation")
    return errors


class RenderingBoundaryTests(unittest.TestCase):
    def test_current_production_sources(self):
        found = list(production_sources())
        self.assertTrue(any(line == "manim" for line, _, _ in found))
        issues = [(str(path.relative_to(ROOT)), issue)
                  for line, owner, path in found for issue in violations(line, owner, path)]
        self.assertEqual(issues, [])

    def test_guard_detects_cross_import_and_build_call(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.py"
            path.write_text('import scripts.manim.production\n'
                            'subprocess.run(["scripts/manim/render.ps1"])\n', encoding="utf-8")
            self.assertEqual(len(violations("static_cards", "C999_example", path)), 2)
            path = Path(directory) / "bad.ps1"
            path.write_text('.\\scripts\\static_cards\\render.ps1 -Uid C999\n', encoding="utf-8")
            self.assertEqual(len(violations("manim", "C999_example", path)), 1)
            path = Path(directory) / "other_uid.py"
            path.write_text('from C001_example.manim import math_model\n', encoding="utf-8")
            self.assertEqual(len(violations("manim", "C999_example", path)), 1)


if __name__ == "__main__":
    unittest.main()
