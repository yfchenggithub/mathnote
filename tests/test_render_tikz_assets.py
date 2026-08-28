from __future__ import annotations

import json
import shutil
import subprocess
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = PROJECT_ROOT / "scripts" / "render_tikz_assets.mjs"


class RenderTikzAssetsProtocolTests(unittest.TestCase):
    def test_migrates_legacy_tikz_block_and_only_sanitizes_rendered_source(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node is unavailable")

        source = "assets/tikz/R032_overview.tex"
        untouched_source = "assets/tikz/R999_not_rendered.tex"
        fixture = {
            "R032": {
                "content": {
                    "sections": [
                        {
                            "key": "statement",
                            "blocks": [
                                {
                                    "id": "statement-image-1",
                                    "type": "image_block",
                                    "src": "/static/tikz/R032/overview.hash@3x.png",
                                    "source": source,
                                    "width_px": 900,
                                    "height_px": 450,
                                    "display_width_px": 300,
                                    "display_height_px": 150,
                                    "scale": 3,
                                }
                            ],
                        }
                    ],
                    "plain": {"statement": f"before\n{source}\nafter"},
                }
            },
            "R999": {
                "content": {
                    "sections": [],
                    "plain": {"statement": f"before\n{untouched_source}\nafter"},
                }
            },
        }

        temp_root = PROJECT_ROOT / ".tmp" / f"test_render_tikz_assets_{uuid.uuid4().hex}"
        temp_root.mkdir(parents=True, exist_ok=False)
        try:
            input_path = temp_root / "input.json"
            output_path = temp_root / "output.json"
            report_path = temp_root / "report.json"
            input_path.write_text(
                json.dumps(fixture, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "node",
                    str(RENDER_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--out-dir",
                    str(temp_root / "tikz"),
                    "--report",
                    str(report_path),
                    "--fail-on-error",
                    "true",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            rendered = json.loads(output_path.read_text(encoding="utf-8"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

        migrated_block = rendered["R032"]["content"]["sections"][0]["blocks"][0]
        self.assertEqual(migrated_block["type"], "tikz_image")
        self.assertNotIn(source, rendered["R032"]["content"]["plain"]["statement"])
        self.assertIn(
            untouched_source,
            rendered["R999"]["content"]["plain"]["statement"],
        )
        self.assertEqual(report["migrated"], 1)
        self.assertEqual(report["sanitizedPlainFields"], 1)


if __name__ == "__main__":
    unittest.main()
