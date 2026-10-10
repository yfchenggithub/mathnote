from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.zhishu.content_package import build_package, diff_packages, validate_package
from scripts.zhishu.runtime_mapping import map_runtime
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository
from tests.test_zhishu_content_package import meta_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_MP4 = PROJECT_ROOT / "03_conic/C002_ellipse_point_line_distance_extrema/videos/ellipse_line_distance.mp4"


class ShareVideoPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source_root = self.root / "source"
        for module in MODULE_NAMES:
            (self.source_root / module).mkdir(parents=True)
        self.uid_root = self.source_root / "03_conic/C002_fixture"
        for directory in ("images", "pdfs", "videos"):
            (self.uid_root / directory).mkdir(parents=True)
        (self.uid_root / "meta.json").write_text(
            json.dumps(meta_record("C002", "动画测试"), ensure_ascii=False), encoding="utf-8"
        )
        self.prepared = self.root / "prepared"
        (self.prepared / "images/C002").mkdir(parents=True)
        self.add_pair("first")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_pair(self, name: str) -> None:
        gif = b"GIF89a-test-" + name.encode("ascii")
        (self.uid_root / f"images/{name}.gif").write_bytes(gif)
        (self.prepared / f"images/C002/{name}.gif").write_bytes(gif)
        video = self.uid_root / f"videos/{name}.mp4"
        shutil.copyfile(REAL_MP4, video)
        registry_path = self.uid_root / "videos/share_assets.json"
        data = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {
            "schemaVersion": 1, "knowledgeId": "C002", "associations": [],
        }
        data["associations"].append({
            "displayAssetId": f"C002:image:{name}.gif",
            "displayAssetUri": f"resources/images/C002/{name}.gif",
            "displaySource": f"images/{name}.gif",
            "displaySha256": hashlib.sha256(gif).hexdigest(),
            "shareAssetId": f"C002:share-video:{name}.mp4",
            "shareAssetUri": f"resources/videos/C002/{name}.mp4",
            "shareSource": f"videos/{name}.mp4",
            "shareMimeType": "video/mp4",
            "shareBytes": video.stat().st_size,
            "shareSha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        })
        registry_path.write_text(json.dumps(data), encoding="utf-8")

    def registry(self) -> dict:
        return json.loads((self.uid_root / "videos/share_assets.json").read_text(encoding="utf-8"))

    def write_registry(self, data: dict) -> None:
        (self.uid_root / "videos/share_assets.json").write_text(json.dumps(data), encoding="utf-8")

    def build(self, name: str, *, video: bool = True, allow_video_removal: bool = False):
        scan = scan_repository(self.source_root)
        mapping = map_runtime(scan, self.prepared)
        self.assertEqual(mapping.errors, ())
        kwargs = {"schema_version": 1} if not video else {}
        return build_package(
            scan, mapping, self.root / name, self.prepared,
            allow_video_removal=allow_video_removal, **kwargs,
        )

    def test_no_video_default_is_valid_v2_with_empty_registry(self) -> None:
        (self.uid_root / "videos/first.mp4").unlink()
        (self.uid_root / "videos/share_assets.json").unlink()
        package = self.build("no-video")
        self.assertEqual(package.errors, ())
        self.assertEqual(validate_package(package.output_dir), ())
        manifest = json.loads((package.output_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["counts"]["animationShares"], 0)
        self.assertEqual(manifest["counts"]["videoAssets"], 0)
        self.assertEqual(manifest["shareAssetHashes"], {})
        self.assertEqual((package.output_dir / "animation-shares.json").read_text(encoding="utf-8"), "[]\n")
        self.assertFalse((package.output_dir / "resources/videos").exists())

    def test_second_uid_is_discovered_without_publisher_change(self) -> None:
        second = self.source_root / "03_conic/C003_fixture"
        for directory in ("images", "pdfs", "videos"):
            (second / directory).mkdir(parents=True)
        (second / "meta.json").write_text(
            json.dumps(meta_record("C003", "第二组动画"), ensure_ascii=False), encoding="utf-8"
        )
        gif = b"GIF89a-c003"
        (second / "images/other.gif").write_bytes(gif)
        (self.prepared / "images/C003").mkdir()
        (self.prepared / "images/C003/other.gif").write_bytes(gif)
        video = second / "videos/other_share.mp4"
        shutil.copyfile(REAL_MP4, video)
        (second / "videos/share_assets.json").write_text(json.dumps({
            "schemaVersion": 1, "knowledgeId": "C003", "associations": [{
                "displayAssetId": "C003:image:other.gif",
                "displayAssetUri": "resources/images/C003/other.gif",
                "displaySource": "images/other.gif",
                "displaySha256": hashlib.sha256(gif).hexdigest(),
                "shareAssetId": "C003:share-video:other_share.mp4",
                "shareAssetUri": "resources/videos/C003/other_share.mp4",
                "shareSource": "videos/other_share.mp4",
                "shareMimeType": "video/mp4", "shareBytes": video.stat().st_size,
                "shareSha256": hashlib.sha256(video.read_bytes()).hexdigest(),
            }],
        }), encoding="utf-8")
        package = self.build("two-uids")
        self.assertEqual(package.errors, ())
        shares = json.loads((package.output_dir / "animation-shares.json").read_text(encoding="utf-8"))
        self.assertEqual({row["knowledgeId"] for row in shares}, {"C002", "C003"})
        self.assertTrue((package.output_dir / "resources/videos/C003/other_share.mp4").is_file())

    def test_failed_rebuild_keeps_previous_video_and_requires_explicit_removal(self) -> None:
        first = self.build("published")
        self.assertEqual(first.errors, ())
        original = (first.output_dir / "manifest.json").read_bytes()
        repeated = self.build("published")
        self.assertEqual(repeated.errors, ())
        self.assertEqual((repeated.output_dir / "manifest.json").read_bytes(), original)
        (self.uid_root / "videos/first.mp4").unlink()
        missing = self.build("published")
        self.assertTrue(missing.errors)
        self.assertEqual((first.output_dir / "manifest.json").read_bytes(), original)
        self.assertTrue((first.output_dir / "resources/videos/C002/first.mp4").is_file())
        (self.uid_root / "videos/share_assets.json").unlink()
        removed = self.build("published")
        self.assertTrue(any("--allow-video-removal" in issue.message for issue in removed.errors))
        self.assertEqual((first.output_dir / "manifest.json").read_bytes(), original)
        approved = self.build("published", allow_video_removal=True)
        self.assertEqual(approved.errors, ())
        self.assertEqual(approved.counts["videoAssets"], 0)

    def test_orphan_mp4_without_registry_fails(self) -> None:
        (self.uid_root / "videos/share_assets.json").unlink()
        result = self.build("orphan-source")
        self.assertTrue(any("lacks formal share registry" in issue.message for issue in result.errors))
        self.assertFalse(result.output_dir.exists())

    def test_legacy_v1_cannot_target_formal_default_output(self) -> None:
        scan = scan_repository(self.source_root)
        mapping = map_runtime(scan, self.prepared)
        with self.assertRaisesRegex(ValueError, "isolated output"):
            build_package(
                scan, mapping, PROJECT_ROOT / "build/zhishu-content-package",
                self.prepared, schema_version=1,
            )

    def test_v2_package_is_registered_and_deterministic(self) -> None:
        first = self.build("first-package")
        second = self.build("second-package")
        self.assertEqual(first.errors, ())
        self.assertEqual(second.errors, ())
        self.assertEqual(first.content_version, second.content_version)
        self.assertEqual(validate_package(first.output_dir), ())
        manifest = json.loads((first.output_dir / "manifest.json").read_text(encoding="utf-8"))
        shares = json.loads((first.output_dir / "animation-shares.json").read_text(encoding="utf-8"))
        assets = json.loads((first.output_dir / "knowledge-assets.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["counts"]["videoAssets"], 1)
        self.assertEqual(manifest["files"]["animationShares"], "animation-shares.json")
        self.assertEqual(manifest["shareAssetHashes"][shares[0]["shareAssetId"]], shares[0]["sha256"])
        self.assertEqual(shares[0]["displayAssetId"], "C002:image:first.gif")
        self.assertEqual([asset["type"] for asset in assets], ["image"])
        self.assertEqual([asset["sortOrder"] for asset in assets], [10])
        self.assertEqual((first.output_dir / shares[0]["uri"]).read_bytes(), REAL_MP4.read_bytes())
        self.assertEqual(diff_packages(first.output_dir, second.output_dir).entries, ())

    def test_legacy_v1_package_still_valid_and_has_no_video(self) -> None:
        legacy = self.build("legacy", video=False)
        self.assertEqual(legacy.errors, ())
        self.assertEqual(validate_package(legacy.output_dir), ())
        manifest = json.loads((legacy.output_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], 1)
        self.assertNotIn("shareAssetHashes", manifest)
        self.assertFalse((legacy.output_dir / "animation-shares.json").exists())
        self.assertFalse((legacy.output_dir / "resources/videos").exists())

    def test_missing_mp4_and_wrong_hash_fail_before_package_output(self) -> None:
        video = self.uid_root / "videos/first.mp4"
        video.unlink()
        missing = self.build("missing-video")
        self.assertTrue(any("MP4 source is missing" in issue.message for issue in missing.errors))
        self.assertFalse(missing.output_dir.exists())
        shutil.copyfile(REAL_MP4, video)
        data = self.registry()
        data["associations"][0]["shareSha256"] = "0" * 64
        self.write_registry(data)
        wrong_hash = self.build("wrong-hash")
        self.assertTrue(any("MP4 source is missing or changed" in issue.message for issue in wrong_hash.errors))

    def test_cross_animation_and_wrong_type_are_rejected(self) -> None:
        self.add_pair("second")
        data = self.registry()
        data["associations"][1]["displayAssetId"] = "C002:image:first.gif"
        self.write_registry(data)
        crossed = self.build("crossed")
        self.assertTrue(any("duplicate or cross-linked" in issue.message for issue in crossed.errors))
        data = self.registry()
        data["associations"][1]["displayAssetId"] = "C002:image:second.gif"
        data["associations"][0]["displayAssetId"] = "C002:image:second.gif"
        data["associations"][1]["displayAssetId"] = "C002:image:first.gif"
        self.write_registry(data)
        swapped = self.build("swapped")
        self.assertTrue(any("GIF asset identity mismatch" in issue.message for issue in swapped.errors))
        data = self.registry()
        data["associations"][0]["displayAssetId"] = "C002:image:first.gif"
        data["associations"][1]["displayAssetId"] = "C002:image:second.gif"
        data["associations"][1]["shareMimeType"] = "image/gif"
        self.write_registry(data)
        wrong_type = self.build("wrong-type")
        self.assertTrue(any("share video identity mismatch" in issue.message for issue in wrong_type.errors))

    def test_two_gifs_have_separate_video_relations(self) -> None:
        self.add_pair("second")
        package = self.build("two-pairs")
        self.assertEqual(package.errors, ())
        shares = json.loads((package.output_dir / "animation-shares.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [(row["displayAssetId"], row["shareAssetId"]) for row in shares],
            [
                ("C002:image:first.gif", "C002:share-video:first.mp4"),
                ("C002:image:second.gif", "C002:share-video:second.mp4"),
            ],
        )

    def test_v2_manifest_and_video_resource_tampering_are_rejected(self) -> None:
        package = self.build("valid").output_dir
        video = package / "resources/videos/C002/first.mp4"
        extra = video.with_name("orphan.mp4")
        extra.write_bytes(b"orphan")
        self.assertTrue(any("do not exactly match" in issue.message for issue in validate_package(package)))
        extra.unlink()
        video.unlink()
        self.assertTrue(any("share video resource is missing" in issue.message for issue in validate_package(package)))
        shutil.copyfile(REAL_MP4, video)
        manifest_path = package / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["shareAssetHashes"] = {}
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("share asset hashes" in issue.message for issue in validate_package(package)))
        manifest["shareAssetHashes"] = {
            "C002:share-video:first.mp4": hashlib.sha256(video.read_bytes()).hexdigest()
        }
        manifest["files"].pop("animationShares")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("files.animationShares" in issue.message for issue in validate_package(package)))

    def test_packaged_share_cannot_be_disguised_as_image(self) -> None:
        package = self.build("valid").output_dir
        path = package / "animation-shares.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        rows[0]["mimeType"] = "image/gif"
        path.write_text(json.dumps(rows), encoding="utf-8")
        self.assertTrue(any("invalid MP4 identity or type" in issue.message for issue in validate_package(package)))

    def test_v1_to_v2_diff_reports_share_addition_only(self) -> None:
        legacy = self.build("legacy", video=False)
        updated = self.build("updated")
        diff = diff_packages(legacy.output_dir, updated.output_dir)
        self.assertEqual(diff.errors, ())
        self.assertEqual(
            [(entry.entity_type, entry.operation, entry.entity_id) for entry in diff.entries],
            [("AnimationShare", "ADD", "C002:image:first.gif")],
        )


if __name__ == "__main__":
    unittest.main()
