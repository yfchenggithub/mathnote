from __future__ import annotations

import binascii
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from scripts.zhishu.asset_preparation import (
    RuntimeAssetPreparationError,
    WORKER_PATH,
    prepare_runtime_images,
    verify_prepared_runtime_images,
)
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_rgb_png(path: Path, width: int, height: int, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = b"\x00" + bytes(color) * width
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += _png_chunk(b"IDAT", zlib.compress(row * height, 9))
    payload += _png_chunk(b"IEND", b"")
    path.write_bytes(payload)


class RuntimeImagePreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for module in MODULE_NAMES:
            (self.root / module).mkdir()
        self.source = self.root / "03_conic/C001_source"
        (self.source / "images").mkdir(parents=True)
        (self.source / "pdfs").mkdir()
        (self.source / "meta.json").write_text(
            json.dumps({"id": "C001"}), encoding="utf-8"
        )
        self.output = self.root / "build/zhishu-runtime-assets"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def prepare(self):
        scan = scan_repository(self.root)
        return prepare_runtime_images(
            scan,
            self.output,
            project_root=self.root,
            worker_path=WORKER_PATH,
        )

    def test_full_runtime_image_contract_and_freshness_lifecycle(self) -> None:
        normal = self.source / "images/001.png"
        wide = self.source / "images/002.png"
        pdf = self.source / "pdfs/C001.pdf"
        write_rgb_png(normal, 941, 20, (255, 255, 255))
        write_rgb_png(wide, 1600, 100, (20, 40, 200))
        pdf.write_bytes(b"pdf-stays-byte-identical")
        original_normal = normal.read_bytes()
        original_wide = wide.read_bytes()
        original_pdf = pdf.read_bytes()

        first = self.prepare()
        outputs = {asset["output"]: asset for asset in first["assets"]}
        normal_output = self.output / "images/C001/001.webp"
        wide_output = self.output / "images/C001/002.webp"
        self.assertEqual(first["contract"]["quality"], 85)
        self.assertEqual(first["contract"]["maxWidth"], 1440)
        self.assertFalse(first["contract"]["upscale"])
        self.assertEqual(outputs["images/C001/001.webp"]["width"], 941)
        self.assertEqual(outputs["images/C001/002.webp"]["width"], 1440)
        self.assertEqual(outputs["images/C001/002.webp"]["height"], 90)
        self.assertEqual(normal_output.read_bytes()[:4], b"RIFF")
        self.assertEqual(normal_output.read_bytes()[8:12], b"WEBP")
        self.assertEqual(normal.read_bytes(), original_normal)
        self.assertEqual(wide.read_bytes(), original_wide)
        self.assertEqual(pdf.read_bytes(), original_pdf)

        first_snapshot = {
            path.relative_to(self.output).as_posix(): path.read_bytes()
            for path in self.output.rglob("*")
            if path.is_file()
        }
        second = self.prepare()
        second_snapshot = {
            path.relative_to(self.output).as_posix(): path.read_bytes()
            for path in self.output.rglob("*")
            if path.is_file()
        }
        self.assertEqual(first, second)
        self.assertEqual(first_snapshot, second_snapshot)

        previous_hash = outputs["images/C001/001.webp"]["outputSha256"]
        write_rgb_png(normal, 941, 20, (0, 0, 0))
        changed = self.prepare()
        changed_asset = next(asset for asset in changed["assets"] if asset["output"].endswith("001.webp"))
        self.assertNotEqual(changed_asset["outputSha256"], previous_hash)

        wide.unlink()
        added = self.source / "images/003.png"
        write_rgb_png(added, 10, 10, (200, 30, 30))
        final = self.prepare()
        self.assertFalse(wide_output.exists())
        self.assertTrue((self.output / "images/C001/003.webp").is_file())
        self.assertEqual(len(final["assets"]), 2)
        self.assertEqual(pdf.read_bytes(), original_pdf)
        verify_prepared_runtime_images(
            scan_repository(self.root), self.output, project_root=self.root
        )

        write_rgb_png(added, 10, 10, (10, 200, 10))
        with self.assertRaisesRegex(RuntimeAssetPreparationError, "source hash is stale"):
            verify_prepared_runtime_images(
                scan_repository(self.root), self.output, project_root=self.root
            )


if __name__ == "__main__":
    unittest.main()
