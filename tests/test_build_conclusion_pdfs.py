from __future__ import annotations

import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import build_conclusion_pdfs as builder


class BuildConclusionPdfsIdRangeTests(unittest.TestCase):
    def test_range_includes_both_endpoints(self) -> None:
        self.assertEqual(
            builder.normalize_ids(["F017-F025"]),
            [f"F{number:03d}" for number in range(17, 26)],
        )

    def test_mixed_ranges_and_ids_keep_order_without_duplicates(self) -> None:
        self.assertEqual(
            builder.normalize_ids(["f019,f017-f020", "C001-C002", "F020-F021"]),
            ["F019", "F017", "F018", "F020", "C001", "C002", "F021"],
        )

    def test_equal_endpoints_and_zero_padding(self) -> None:
        self.assertEqual(builder.normalize_ids(["F009-F010", "F010-F010"]), ["F009", "F010"])

    def test_empty_and_single_ids_still_work(self) -> None:
        self.assertEqual(builder.normalize_ids(None), [])
        self.assertEqual(builder.normalize_ids([]), [])
        self.assertEqual(builder.normalize_ids(["s001,I001", "S001"]), ["S001", "I001"])

    def test_range_accepts_whitespace_around_separator(self) -> None:
        self.assertEqual(builder.normalize_ids([" F017 - F018 "]), ["F017", "F018"])

    def test_descending_range_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Start must be less than or equal to end"):
            builder.normalize_ids(["F025-F017"])

    def test_cross_prefix_range_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "same prefix"):
            builder.normalize_ids(["F017-C025"])

    def test_malformed_ranges_are_rejected(self) -> None:
        for value in ["F17-F25", "F017-025", "F017-", "F017-F025-F030", "F017_F025"]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Expected an ID"):
                builder.normalize_ids([value])

    def test_cli_range_selects_only_requested_ids_without_building_in_dry_run(self) -> None:
        items = [
            builder.ConclusionItem("01_function", f"F{n:03d}_test", Path(f"01_function/F{n:03d}_test"), f"F{n:03d}")
            for n in range(16, 27)
        ]
        for id_args in [["F017-F025"], ["--ids", "F017-F025"]]:
            with self.subTest(id_args=id_args):
                output = io.StringIO()
                with mock.patch("sys.argv", [
                    "build_conclusion_pdfs.py", "--output-to-conclusion-pdfs",
                    "--overwrite", "--dry-run", *id_args,
                ]), mock.patch.object(
                    builder, "resolve_modules", return_value=(["01_function"], "test")
                ), mock.patch.object(
                    builder, "discover_conclusions", return_value=items
                ), mock.patch.object(builder, "compile_one") as compile_one, mock.patch.object(
                    builder, "write_json"
                ) as write_json, redirect_stdout(output):
                    self.assertEqual(builder.main(), 0)
                text = output.getvalue()
                self.assertIn("Selected conclusions: 9", text)
                self.assertIn("F017:", text)
                self.assertIn("F025:", text)
                self.assertNotIn("F016:", text)
                self.assertNotIn("F026:", text)
                compile_one.assert_not_called()
                write_json.assert_not_called()


class BuildConclusionPdfsOutputTests(unittest.TestCase):
    def test_default_cli_keeps_central_output(self) -> None:
        with mock.patch("sys.argv", ["build_conclusion_pdfs.py", "S001"]):
            args = builder.parse_args()

        self.assertFalse(args.output_to_conclusion_pdfs)
        self.assertEqual(args.output_dir, str(builder.DEFAULT_OUTPUT_DIR))

    def test_conclusion_output_flag_is_explicit(self) -> None:
        with mock.patch(
            "sys.argv",
            ["build_conclusion_pdfs.py", "S001", "--output-to-conclusion-pdfs"],
        ):
            args = builder.parse_args()

        self.assertTrue(args.output_to_conclusion_pdfs)

    def test_output_dir_and_conclusion_mode_are_mutually_exclusive(self) -> None:
        with mock.patch(
            "sys.argv",
            [
                "build_conclusion_pdfs.py",
                "S001",
                "--output-dir",
                "custom",
                "--output-to-conclusion-pdfs",
            ],
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                builder.parse_args()

    def test_resolve_output_dir_preserves_default_and_supports_source_pdfs(self) -> None:
        item = builder.ConclusionItem(
            module="00_set",
            folder_name="S001_Subset_Count",
            folder_path=Path("00_set/S001_Subset_Count"),
            conclusion_id="S001",
        )
        central = Path("build/conclusion_pdfs")

        self.assertEqual(
            builder.resolve_pdf_output_dir(item, central, False),
            central,
        )
        self.assertEqual(
            builder.resolve_pdf_output_dir(item, central, True),
            item.folder_path / "pdfs",
        )

    def test_main_passes_each_conclusion_pdfs_directory_to_compiler(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "S001_Subset_Count"
            source.mkdir()
            item = builder.ConclusionItem(
                module="00_set",
                folder_name=source.name,
                folder_path=source,
                conclusion_id="S001",
            )
            args = argparse.Namespace(
                modules=["00_set"],
                ids=None,
                positional_ids=[],
                conclusions=None,
                output_dir=str(builder.DEFAULT_OUTPUT_DIR),
                output_to_conclusion_pdfs=True,
                map_json=str(Path(temp_dir) / "map.json"),
                pdf_name_mode="folder",
                overwrite=False,
                dry_run=False,
            )
            captured_output_dirs: list[Path] = []

            def fake_compile_one(**kwargs):
                captured_output_dirs.append(kwargs["output_dir"])
                return builder.BuildResult(
                    item=kwargs["item"],
                    pdf_name=builder.build_pdf_name(
                        kwargs["item"], kwargs["pdf_name_mode"]
                    ),
                    status="success",
                )

            with mock.patch.object(builder, "parse_args", return_value=args), mock.patch.object(
                builder,
                "resolve_modules",
                return_value=(["00_set"], "test"),
            ), mock.patch.object(
                builder,
                "discover_conclusions",
                return_value=[item],
            ), mock.patch.object(
                builder,
                "compile_one",
                side_effect=fake_compile_one,
            ), mock.patch.object(builder, "write_json"), redirect_stdout(io.StringIO()):
                exit_code = builder.main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(captured_output_dirs, [source / "pdfs"])
            self.assertTrue((source / "pdfs").is_dir())


if __name__ == "__main__":
    unittest.main()
