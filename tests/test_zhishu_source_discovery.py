from __future__ import annotations

import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from scripts.zhishu import source_discovery as discovery
from scripts.zhishu import publish


class SourceDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        for module_name in discovery.MODULE_NAMES:
            (self.project_root / module_name).mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_source(self, module_name: str, source_name: str) -> Path:
        source_path = self.project_root / module_name / source_name
        source_path.mkdir()
        (source_path / "meta.json").write_text(
            json.dumps({"id": source_name}),
            encoding="utf-8",
        )
        return source_path

    def test_normal_scan_is_sorted_and_repeatable(self) -> None:
        self.create_source("03_conic", "C003")
        self.create_source("03_conic", "C001")
        self.create_source("03_conic", "C002")

        first = discovery.scan_repository(self.project_root)
        second = discovery.scan_repository(self.project_root)

        names = [source.conclusion_dir_name for source in first.modules[3].sources]
        self.assertEqual(names, ["C001", "C002", "C003"])
        self.assertEqual(first, second)
        self.assertEqual(first.errors, ())

    def test_only_direct_child_directories_are_discovered(self) -> None:
        source_path = self.create_source("03_conic", "C001")
        (source_path / "nested" / "C999").mkdir(parents=True)
        (self.project_root / "03_conic" / "README.md").write_text("notes", encoding="utf-8")
        (self.project_root / "03_conic" / "data.json").write_text("{}", encoding="utf-8")

        result = discovery.scan_repository(self.project_root)

        names = [source.conclusion_dir_name for source in result.modules[3].sources]
        self.assertEqual(names, ["C001"])

    def test_only_fixed_modules_are_scanned(self) -> None:
        extra_module = self.project_root / "11_new_module"
        extra_module.mkdir()
        extra_source = extra_module / "X001"
        extra_source.mkdir()
        (extra_source / "meta.json").write_text("{}", encoding="utf-8")

        result = discovery.scan_repository(self.project_root)

        self.assertEqual(
            [module.module_name for module in result.modules],
            list(discovery.MODULE_NAMES),
        )
        self.assertEqual(result.conclusion_count, 0)

    def test_missing_meta_is_reported_without_hiding_source(self) -> None:
        (self.project_root / "03_conic" / "C001").mkdir()

        result = discovery.scan_repository(self.project_root)

        self.assertEqual(result.modules[3].sources[0].conclusion_dir_name, "C001")
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].message, "missing meta.json")

    def test_non_file_meta_is_reported(self) -> None:
        source_path = self.project_root / "03_conic" / "C001"
        (source_path / "meta.json").mkdir(parents=True)

        result = discovery.scan_repository(self.project_root)

        self.assertEqual(result.errors[0].message, "meta.json is not a regular file")

    def test_invalid_json_is_reported_without_modifying_file(self) -> None:
        source_path = self.create_source("03_conic", "C001")
        meta_path = source_path / "meta.json"
        invalid_json = '{"id": '
        meta_path.write_text(invalid_json, encoding="utf-8")

        result = discovery.scan_repository(self.project_root)

        self.assertEqual(len(result.errors), 1)
        self.assertTrue(result.errors[0].message.startswith("invalid JSON:"))
        self.assertEqual(meta_path.read_text(encoding="utf-8"), invalid_json)

    def test_missing_fixed_module_is_reported(self) -> None:
        (self.project_root / "06_probability-stat").rmdir()

        result = discovery.scan_repository(self.project_root)

        error = next(error for error in result.errors if error.path.as_posix() == "06_probability-stat")
        self.assertEqual(error.message, "module directory is missing")

    def test_report_contains_stable_totals(self) -> None:
        self.create_source("00_set", "S001")
        result = discovery.scan_repository(self.project_root)

        report = publish.format_scan_result(result)

        self.assertIn("00_set                  1", report)
        self.assertIn("Modules: 11", report)
        self.assertIn("Conclusions: 1", report)
        self.assertIn("Errors: 0", report)

    def test_scan_command_returns_nonzero_when_validation_fails(self) -> None:
        (self.project_root / "03_conic" / "C001").mkdir()
        output = io.StringIO()

        with mock.patch.object(publish, "PROJECT_ROOT", self.project_root), redirect_stdout(output):
            exit_code = publish.main(["scan"])

        self.assertEqual(exit_code, 1)
        self.assertIn("03_conic/C001/meta.json: missing meta.json", output.getvalue())

    def test_scan_command_succeeds_when_validation_passes(self) -> None:
        self.create_source("03_conic", "C001")
        output = io.StringIO()

        with mock.patch.object(publish, "PROJECT_ROOT", self.project_root), redirect_stdout(output):
            exit_code = publish.main(["scan"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Modules: 11", output.getvalue())
        self.assertIn("Errors: 0", output.getvalue())


if __name__ == "__main__":
    unittest.main()
