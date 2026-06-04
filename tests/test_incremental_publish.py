from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from unittest import mock

from scripts import incremental_publish as publisher


class IncrementalPublishConfigTests(unittest.TestCase):
    def test_temp_workspace_is_removed_by_default(self) -> None:
        with mock.patch("sys.argv", ["incremental_publish.py", "R005"]):
            config = publisher.build_config(publisher.parse_args())
        self.assertFalse(config.keep_temp)

    def test_keep_temp_flag_preserves_temp_workspace(self) -> None:
        with mock.patch("sys.argv", ["incremental_publish.py", "R005", "--keep-temp"]):
            config = publisher.build_config(publisher.parse_args())
        self.assertTrue(config.keep_temp)


def _publish_config() -> publisher.PublishConfig:
    root = publisher.PROJECT_ROOT
    return publisher.PublishConfig(
        ids=("R005",),
        dry_run=False,
        strict=False,
        keep_temp=True,
        log_level="INFO",
        canonical_path=root / "data" / "content" / "canonical_content_v2.json",
        backend_index_path=root / "data" / "search_engine" / "backend_search_index.json",
        pdf_map_path=root / "build" / "conclusion_pdf_map.json",
        pdf_output_dir=root / "build" / "conclusion_pdfs",
        backend_repo=root,
        backend_data_dir=root / "app" / "data",
        sync_backend_data=False,
        pull_backend_repo=False,
        backend_git_publish=False,
        backend_git_push=False,
        backend_commit_message="Incremental publish R005",
        formula_min_length=5,
        asset_base="/static/formulas",
        remote_host="example.invalid",
        remote_user="tester",
        remote_password="yfcheng",
        remote_formula_dir="/var/www/ok-shuxue/static/formulas",
        remote_formula_owner="www-data",
        remote_formula_group="www-data",
        remote_backend_root="/root/math_search_backend",
        deploy=False,
        upload_formulas=True,
        remote_pull=False,
        restart=False,
        restart_command="true",
        allow_primary_fallback=False,
        report_path=root / "reports" / "incremental_publish_report.json",
    )


class IncrementalPublishUploadTests(unittest.TestCase):
    def test_formula_upload_uses_project_relative_scp_source(self) -> None:
        fixture_root = (
            publisher.PROJECT_ROOT
            / "tests"
            / ".tmp"
            / "incremental_publish_upload_fixture"
        )
        shutil.rmtree(fixture_root, ignore_errors=True)
        local_formula_dir = fixture_root / "formulas" / "R005"
        local_formula_dir.mkdir(parents=True, exist_ok=True)

        config = _publish_config()
        paths = publisher.create_paths(config)
        paths.tmp_root = fixture_root / "tmp_root"
        paths.formula_out_dir = fixture_root / "formulas"
        stages: list[publisher.StageResult] = []
        calls: list[dict[str, object]] = []

        def fake_run_command(
            name: str,
            command: list[str],
            *,
            cwd: Path = publisher.PROJECT_ROOT,
            stages: list[publisher.StageResult],
            interactive: bool = False,
            env: dict[str, str] | None = None,
            input_text: str | None = None,
        ) -> object:
            calls.append(
                {
                    "name": name,
                    "command": command,
                    "cwd": cwd,
                    "interactive": interactive,
                    "env": env,
                    "input_text": input_text,
                }
            )
            return object()

        try:
            with mock.patch.object(
                publisher,
                "run_command",
                side_effect=fake_run_command,
            ), mock.patch.object(publisher.shutil, "which", return_value=None):
                result = publisher.upload_formula_dirs(config, paths, stages)
        finally:
            shutil.rmtree(fixture_root, ignore_errors=True)

        self.assertFalse(result["skipped"])
        prepare_call = next(
            call for call in calls if call["name"] == "remote prepare formula upload staging"
        )
        self.assertEqual(prepare_call["command"][0:2], ["ssh", "tester@example.invalid"])
        self.assertIn("SSH_ASKPASS", prepare_call["env"])
        self.assertEqual(prepare_call["env"]["SSH_ASKPASS_REQUIRE"], "force")
        self.assertIn("/tmp/", prepare_call["command"][2])
        self.assertIn("/formulas", prepare_call["command"][2])

        upload_call = next(
            call for call in calls if call["name"] == "upload formula dir to staging [R005]"
        )
        self.assertEqual(upload_call["command"][0:2], ["scp", "-r"])
        self.assertIn("SSH_ASKPASS", upload_call["env"])
        source_path = upload_call["command"][2]
        self.assertEqual(
            source_path,
            "tests/.tmp/incremental_publish_upload_fixture/formulas/R005",
        )
        self.assertNotIn(":", source_path)
        self.assertNotIn("\\", source_path)
        self.assertTrue(upload_call["command"][3].endswith("/formulas/"))
        self.assertEqual(upload_call["cwd"], publisher.PROJECT_ROOT)

        install_call = next(
            call for call in calls if call["name"] == "remote install formula dir [R005]"
        )
        self.assertEqual(
            install_call["command"][0:3],
            ["ssh", "-tt", "tester@example.invalid"],
        )
        self.assertIn("sudo -S -p '' -i bash -lc", install_call["command"][3])
        self.assertIn("/var/www/ok-shuxue/static/formulas/R005", install_call["command"][3])
        self.assertIn("www-data:www-data", install_call["command"][3])
        self.assertIn("SSH_ASKPASS", install_call["env"])
        self.assertEqual(install_call["input_text"], "yfcheng\n")
        for call in calls:
            self.assertNotIn("yfcheng", " ".join(call["command"]))


class IncrementalPublishBackendSyncTests(unittest.TestCase):
    def test_backend_data_sync_does_not_write_backup_files(self) -> None:
        fixture_root = (
            publisher.PROJECT_ROOT
            / "tests"
            / ".tmp"
            / "incremental_publish_backend_sync_fixture"
        )
        shutil.rmtree(fixture_root, ignore_errors=True)

        source_data = fixture_root / "source"
        source_pdfs = fixture_root / "pdfs"
        backend_data = fixture_root / "backend" / "app" / "data"
        source_data.mkdir(parents=True, exist_ok=True)
        source_pdfs.mkdir(parents=True, exist_ok=True)
        backend_data.mkdir(parents=True, exist_ok=True)

        source_files = {
            "canonical_content_v2.json": '{"new": "canonical"}\n',
            "backend_search_index.json": '{"new": "index"}\n',
            "conclusion_pdf_map.json": '{"R005": "R005.pdf"}\n',
        }
        for filename, text in source_files.items():
            (source_data / filename).write_text(text, encoding="utf-8")
            (backend_data / filename).write_text("old\n", encoding="utf-8")
        (source_pdfs / "R005.pdf").write_bytes(b"new pdf")
        (backend_data / "pdfs").mkdir(exist_ok=True)
        (backend_data / "pdfs" / "R005.pdf").write_bytes(b"old pdf")

        config = _publish_config()
        config.canonical_path = source_data / "canonical_content_v2.json"
        config.backend_index_path = source_data / "backend_search_index.json"
        config.pdf_map_path = source_data / "conclusion_pdf_map.json"
        config.pdf_output_dir = source_pdfs
        config.backend_data_dir = backend_data
        config.sync_backend_data = True
        stages: list[publisher.StageResult] = []

        try:
            with mock.patch.object(
                publisher,
                "backup_file",
                side_effect=AssertionError("backend sync must not write backups"),
            ):
                result = publisher.sync_backend_data(config, {"R005": "R005.pdf"}, stages)

            self.assertFalse(result["skipped"])
            self.assertEqual(
                (backend_data / "canonical_content_v2.json").read_text(encoding="utf-8"),
                source_files["canonical_content_v2.json"],
            )
            self.assertEqual((backend_data / "pdfs" / "R005.pdf").read_bytes(), b"new pdf")
            self.assertEqual(list(backend_data.glob("*.bak_*")), [])
            self.assertEqual(list((backend_data / "pdfs").glob("*.bak_*")), [])
        finally:
            shutil.rmtree(fixture_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
