from __future__ import annotations

import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import build_conclusion_pdfs as builder


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
