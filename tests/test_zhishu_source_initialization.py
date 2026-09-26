from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from scripts.zhishu import publish
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository
from scripts.zhishu.source_initialization import initialize_sources


class SourceInitializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        for module_name in MODULE_NAMES:
            (self.project_root / module_name).mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_source(self, source_name: str = "C001") -> Path:
        source_path = self.project_root / "03_conic" / source_name
        source_path.mkdir()
        (source_path / "meta.json").write_text(
            json.dumps({"id": source_name}),
            encoding="utf-8",
        )
        return source_path

    def initialize(self):
        return initialize_sources(scan_repository(self.project_root))

    def test_creates_both_missing_directories(self) -> None:
        source = self.create_source()

        result = self.initialize()

        self.assertTrue((source / "images").is_dir())
        self.assertTrue((source / "pdfs").is_dir())
        self.assertEqual(result.created_images, 1)
        self.assertEqual(result.created_pdfs, 1)
        self.assertEqual(result.errors, ())

    def test_existing_images_and_files_are_preserved(self) -> None:
        source = self.create_source()
        images = source / "images"
        images.mkdir()
        image = images / "01.png"
        image.write_bytes(b"existing image")

        result = self.initialize()

        self.assertEqual(image.read_bytes(), b"existing image")
        self.assertTrue((source / "pdfs").is_dir())
        self.assertEqual(result.created_images, 0)
        self.assertEqual(result.created_pdfs, 1)

    def test_existing_pdfs_and_files_are_preserved(self) -> None:
        source = self.create_source()
        pdfs = source / "pdfs"
        pdfs.mkdir()
        pdf = pdfs / "full.pdf"
        pdf.write_bytes(b"existing pdf")

        result = self.initialize()

        self.assertEqual(pdf.read_bytes(), b"existing pdf")
        self.assertTrue((source / "images").is_dir())
        self.assertEqual(result.created_images, 1)
        self.assertEqual(result.created_pdfs, 0)

    def test_fully_initialized_source_is_unchanged(self) -> None:
        source = self.create_source()
        image = source / "images" / "01.png"
        pdf = source / "pdfs" / "01.pdf"
        image.parent.mkdir()
        pdf.parent.mkdir()
        image.write_bytes(b"image")
        pdf.write_bytes(b"pdf")

        result = self.initialize()

        self.assertEqual(image.read_bytes(), b"image")
        self.assertEqual(pdf.read_bytes(), b"pdf")
        self.assertEqual(result.created_images, 0)
        self.assertEqual(result.created_pdfs, 0)
        self.assertEqual(result.already_initialized, 1)

    def test_repeated_initialization_is_idempotent(self) -> None:
        source = self.create_source()

        first = self.initialize()
        first_state = sorted(path.relative_to(source).as_posix() for path in source.rglob("*"))
        second = self.initialize()
        second_state = sorted(path.relative_to(source).as_posix() for path in source.rglob("*"))

        self.assertEqual(first.created_images, 1)
        self.assertEqual(first.created_pdfs, 1)
        self.assertEqual(second.created_images, 0)
        self.assertEqual(second.created_pdfs, 0)
        self.assertEqual(first_state, second_state)

    def test_all_existing_files_are_preserved(self) -> None:
        source = self.create_source()
        files = {
            source / "images" / "01.png": b"one",
            source / "images" / "02.png": b"two",
            source / "pdfs" / "full.pdf": b"full",
        }
        for path, content in files.items():
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(content)

        self.initialize()

        self.assertEqual({path: path.read_bytes() for path in files}, files)

    def test_images_file_is_reported_and_preserved(self) -> None:
        source = self.create_source()
        images = source / "images"
        images.write_bytes(b"do not replace")

        result = self.initialize()

        self.assertEqual(images.read_bytes(), b"do not replace")
        self.assertFalse((source / "pdfs").exists())
        self.assertEqual(len(result.errors), 1)
        self.assertIn("images exists but is not a directory", result.errors[0].message)

    def test_pdfs_file_is_reported_and_preserved(self) -> None:
        source = self.create_source()
        pdfs = source / "pdfs"
        pdfs.write_bytes(b"do not replace")

        result = self.initialize()

        self.assertEqual(pdfs.read_bytes(), b"do not replace")
        self.assertFalse((source / "images").exists())
        self.assertEqual(len(result.errors), 1)
        self.assertIn("pdfs exists but is not a directory", result.errors[0].message)

    def test_only_discovered_sources_are_initialized_without_recursion(self) -> None:
        source = self.create_source()
        nested = source / "nested" / "C999"
        unrelated = self.project_root / "tmp" / "C998"
        nested.mkdir(parents=True)
        unrelated.mkdir(parents=True)

        result = self.initialize()

        self.assertEqual(result.conclusion_count, 1)
        self.assertTrue((source / "images").is_dir())
        self.assertTrue((source / "pdfs").is_dir())
        self.assertFalse((nested / "images").exists())
        self.assertFalse((nested / "pdfs").exists())
        self.assertFalse((unrelated / "images").exists())
        self.assertFalse((unrelated / "pdfs").exists())

    def test_discovery_errors_prevent_all_initialization(self) -> None:
        valid_source = self.create_source("C001")
        (self.project_root / "03_conic" / "C002").mkdir()

        result = self.initialize()

        self.assertNotEqual(result.errors, ())
        self.assertFalse((valid_source / "images").exists())
        self.assertFalse((valid_source / "pdfs").exists())

    def test_cli_returns_nonzero_for_initialization_error(self) -> None:
        source = self.create_source()
        (source / "images").write_text("occupied", encoding="utf-8")
        output = io.StringIO()

        with mock.patch.object(publish, "PROJECT_ROOT", self.project_root), redirect_stdout(output):
            exit_code = publish.main(["init-source"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Errors: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
