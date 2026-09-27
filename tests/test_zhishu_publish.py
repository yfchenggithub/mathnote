from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.zhishu import publish
from scripts.zhishu.content_package import PackageBuildResult, PackageIssue


class ZhishuPublishParserTests(unittest.TestCase):
    def test_build_package_uses_repository_default_output(self) -> None:
        args = publish.build_parser().parse_args(["build-package"])

        self.assertEqual(args.output, publish.DEFAULT_PACKAGE_OUTPUT)
        self.assertEqual(
            args.output,
            publish.PROJECT_ROOT / "build" / "zhishu-content-package",
        )

    def test_build_package_allows_explicit_output_override(self) -> None:
        override = Path("custom-package")

        args = publish.build_parser().parse_args(
            ["build-package", "--output", str(override)]
        )

        self.assertEqual(args.output, override)

    def test_diff_invalid_packages_returns_nonzero_without_traceback(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            exit_code = publish.main(
                ["diff", "missing-previous-package", "missing-current-package"]
            )

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Errors:", output.getvalue())
        self.assertIn("manifest file is missing", output.getvalue())

    def test_build_package_validation_failure_returns_nonzero(self) -> None:
        failed = PackageBuildResult(
            output_dir=Path("failed-package"),
            content_version="",
            package_hash="",
            package_size=0,
            counts={},
            errors=(PackageIssue(Path("manifest.json"), "validation failed"),),
            warnings=(),
        )
        output = StringIO()
        with (
            patch.object(publish, "scan_repository", return_value=object()),
            patch.object(publish, "map_runtime", return_value=object()),
            patch.object(publish, "build_package", return_value=failed),
            redirect_stdout(output),
        ):
            exit_code = publish.main(["build-package", "--output", "failed-package"])

        self.assertNotEqual(exit_code, 0)
        self.assertIn("validation failed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
