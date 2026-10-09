"""Safety boundaries for UID discovery and formal asset writes."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import production
from verify_gif import verify_gif


class ProductionSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        base = production.ROOT / "build" / "manim" / "freeze-validation" / "tests"
        base.mkdir(parents=True, exist_ok=True)
        self.root = base / f"fixture-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        for module, uid in (("00_set", "C777"), ("03_conic", "C002")):
            manim = self.root / module / f"{uid}_example" / "manim"
            manim.mkdir(parents=True)
            (manim / "scene.py").write_text("class Example(Scene):\n    pass\n", encoding="utf-8")
            (manim.parent / "images").mkdir()
        (self.root / "build" / "manim").mkdir(parents=True)
        self.patcher = patch.object(production, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def args(self, uid="C777", **kwargs):
        values = dict(uid=uid, scene=None, scene_file=None, name=None,
                      build_root="build/manim", asset_name=None, rebuild=False,
                      publish=False, overwrite=False)
        values.update(kwargs)
        return argparse.Namespace(**values)

    def test_cross_module_exact_uid_and_case(self):
        self.assertEqual(production.conclusion("c777").parent.name, "00_set")
        self.assertEqual(production.conclusion("C002").parent.name, "03_conic")
        with self.assertRaisesRegex(ValueError, "invalid UID"):
            production.conclusion("C00")
        with self.assertRaisesRegex(ValueError, "invalid UID"):
            production.conclusion("C7777")
        with self.assertRaisesRegex(ValueError, "found 0"):
            production.conclusion("C778")

    def test_duplicate_uid_and_scene_ambiguity(self):
        second = self.root / "03_conic" / "C777_duplicate"
        second.mkdir()
        with self.assertRaisesRegex(ValueError, "found 2"):
            production.conclusion("C777")
        second.rmdir()
        scene_file = self.root / "00_set" / "C777_example" / "manim" / "scene.py"
        scene_file.write_text("class A(Scene): pass\nclass B(Scene): pass\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            production.location(self.args())

    def test_build_root_and_name_cannot_escape(self):
        with self.assertRaisesRegex(ValueError, "build root"):
            production.location(self.args(build_root="../outside"))
        with self.assertRaisesRegex(ValueError, "invalid output name"):
            production.location(self.args(name="../C002"))
        with self.assertRaisesRegex(ValueError, "scene-file"):
            production.location(self.args(scene_file="../scene.py"))

    def test_scene_identity_cannot_be_reused(self):
        uid, _folder, source, scene, work = production.location(self.args(name="one"))
        production.identity(work, uid, source, scene)
        with self.assertRaisesRegex(ValueError, "different scene"):
            production.identity(work, uid, source, "Other")

    def test_existing_formal_gif_rejected_before_ffmpeg(self):
        image = self.root / "00_set" / "C777_example" / "images" / "frozen.gif"
        image.write_bytes(b"frozen")
        with self.assertRaisesRegex(ValueError, "explicit -Overwrite"):
            production.export(self.args(name="one", asset_name="frozen.gif", publish=True))
        self.assertEqual(image.read_bytes(), b"frozen")

    def test_ffmpeg_unavailable_and_corrupt_gif_fail(self):
        args = self.args(name="one")
        uid, _folder, source, scene, work = production.location(args)
        production.identity(work, uid, source, scene)
        (work / "one.mp4").write_bytes(b"dummy")
        with patch.object(production.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "FFmpeg unavailable"):
                production.export(args)
        corrupt = work / "corrupt.gif"
        corrupt.write_bytes(b"not a GIF" * 10)
        with self.assertRaisesRegex(ValueError, "invalid GIF header"):
            verify_gif(corrupt)

    def test_mock_render_isolates_modules_and_preserves_previous_mp4_on_failure(self):
        def fake_manim(command, **_kwargs):
            media = Path(command[command.index("--media_dir") + 1])
            name = command[command.index("--output_file") + 1]
            video = media / "videos" / "fixture" / "1024p24" / name
            video.parent.mkdir(parents=True)
            video.write_bytes(name.encode())

        with patch.object(production.subprocess, "run", side_effect=fake_manim):
            first = production.render(self.args("C777", name="first"))
            second = production.render(self.args("C002", name="first"))
        self.assertNotEqual(first.parent, second.parent)
        self.assertEqual(first.read_bytes(), b"first.mp4")
        with patch.object(production.subprocess, "run",
                          side_effect=subprocess.CalledProcessError(9, "manim")):
            with self.assertRaises(subprocess.CalledProcessError):
                production.render(self.args("C777", name="first"))
        self.assertEqual(first.read_bytes(), b"first.mp4")

    def test_gif_checker_accepts_other_valid_dimensions_and_duration(self):
        path = self.root / "short.gif"
        first = Image.new("RGB", (8, 6), "red")
        second = Image.new("RGB", (8, 6), "blue")
        first.save(path, save_all=True, append_images=[second], duration=[100, 100], loop=0)
        info = verify_gif(path)
        self.assertEqual((info["width"], info["height"]), (8, 6))
        self.assertEqual(info["frame_count"], 2)


if __name__ == "__main__":
    unittest.main()
