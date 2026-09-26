from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.zhishu.content_package import build_package, diff_packages, validate_package
from scripts.zhishu.runtime_mapping import map_runtime
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository


def meta_record(
    source_id: str,
    title: str,
    *,
    related_ids: list[str] | None = None,
    keyword: str = "关键词",
) -> dict[str, object]:
    return {
        "id": source_id,
        "core": {
            "title": title,
            "alias": [],
            "summary": f"{title}摘要",
            "difficulty": 3,
            "category": "解析几何",
            "tags": [],
        },
        "search": {
            "keywords": [keyword],
            "synonyms": [],
            "intents": [],
            "query_templates": [],
            "ocrKeywords": [],
            "latex_patterns": [],
            "formulaTokens": [],
            "pinyin": "",
            "pinyinAbbr": "",
        },
        "searchmeta": {},
        "ranking": {},
        "relations": {
            "prerequisites": [],
            "related_ids": related_ids or [],
            "similar": [],
        },
        "knowledgeNode": "解析几何-圆锥曲线-椭圆",
        "altNodes": [],
    }


class ContentPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project_root = self.root / "source"
        self.packages = self.root / "packages"
        for module_name in MODULE_NAMES:
            (self.project_root / module_name).mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_source(self, record: dict[str, object]) -> Path:
        source_id = str(record["id"])
        source = self.project_root / "03_conic" / f"{source_id}_source"
        source.mkdir()
        (source / "images").mkdir()
        (source / "pdfs").mkdir()
        (source / "meta.json").write_text(
            json.dumps(record, ensure_ascii=False), encoding="utf-8"
        )
        return source

    def build(self, name: str):
        scan_result = scan_repository(self.project_root)
        mapping_result = map_runtime(scan_result)
        self.assertEqual(mapping_result.errors, ())
        result = build_package(scan_result, mapping_result, self.packages / name)
        self.assertEqual(result.errors, ())
        return result

    @staticmethod
    def package_bytes(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def test_repeated_packages_are_byte_identical_and_versions_stable(self) -> None:
        self.create_source(meta_record("C001", "结论一"))

        first = self.build("first")
        second = self.build("second")

        self.assertEqual(first.content_version, second.content_version)
        self.assertEqual(first.package_hash, second.package_hash)
        self.assertEqual(self.package_bytes(first.output_dir), self.package_bytes(second.output_dir))
        self.assertEqual(diff_packages(first.output_dir, second.output_dir).entries, ())

    def test_package_structure_and_asset_uri_are_valid(self) -> None:
        source = self.create_source(meta_record("C006", "离心率"))
        (source / "images" / "01.png").write_bytes(b"image")
        (source / "pdfs" / "01.pdf").write_bytes(b"pdf")

        result = self.build("package")
        root = result.output_dir

        for name in ("manifest.json", *[name for name in (
            "knowledge-nodes.json",
            "knowledge-relations.json",
            "knowledge-assets.json",
            "search-documents.json",
        )]):
            self.assertTrue((root / name).is_file())
        self.assertTrue((root / "resources/images/C006/01.png").is_file())
        self.assertTrue((root / "resources/pdfs/C006/01.pdf").is_file())
        self.assertEqual(validate_package(root), ())

    def test_title_and_search_changes_are_updates(self) -> None:
        source = self.create_source(meta_record("C001", "旧标题", keyword="旧关键词"))
        previous = self.build("previous")
        data = meta_record("C001", "新标题", keyword="新关键词")
        (source / "meta.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        current = self.build("current")

        diff = diff_packages(previous.output_dir, current.output_dir)

        self.assertIn(("KnowledgeNode", "UPDATE", "C001"), {(e.entity_type, e.operation, e.entity_id) for e in diff.entries})
        self.assertIn(("SearchDocument", "UPDATE", "C001"), {(e.entity_type, e.operation, e.entity_id) for e in diff.entries})

    def test_asset_content_add_and_delete_diff(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        image = source / "images" / "01.png"
        image.write_bytes(b"old")
        previous = self.build("previous")

        image.write_bytes(b"new")
        added = source / "images" / "02.png"
        added.write_bytes(b"two")
        changed = self.build("changed")
        changed_diff = diff_packages(previous.output_dir, changed.output_dir)
        entries = {(e.operation, e.entity_id) for e in changed_diff.entries if e.entity_type == "KnowledgeAsset"}
        self.assertIn(("UPDATE", "C001:image:01.png"), entries)
        self.assertIn(("ADD", "C001:image:02.png"), entries)

        image.unlink()
        added.unlink()
        removed = self.build("removed")
        removed_diff = diff_packages(changed.output_dir, removed.output_dir)
        deleted = {(e.operation, e.entity_id) for e in removed_diff.entries if e.entity_type == "KnowledgeAsset"}
        self.assertEqual(deleted, {("DELETE", "C001:image:01.png"), ("DELETE", "C001:image:02.png")})

    def test_add_and_delete_conclusion_and_relation(self) -> None:
        first_source = self.create_source(meta_record("C001", "结论一"))
        previous = self.build("previous")
        self.create_source(meta_record("C002", "结论二", related_ids=["C001"]))
        added = self.build("added")
        added_entries = {(e.entity_type, e.operation, e.entity_id) for e in diff_packages(previous.output_dir, added.output_dir).entries}
        self.assertIn(("KnowledgeNode", "ADD", "C002"), added_entries)
        self.assertIn(("SearchDocument", "ADD", "C002"), added_entries)
        self.assertTrue(any(item[0] == "KnowledgeRelation" and item[1] == "ADD" for item in added_entries))

        shutil.rmtree(first_source)
        second_source = self.project_root / "03_conic" / "C002_source"
        second_data = meta_record("C002", "结论二")
        (second_source / "meta.json").write_text(json.dumps(second_data, ensure_ascii=False), encoding="utf-8")
        deleted = self.build("deleted")
        deleted_entries = {(e.entity_type, e.operation, e.entity_id) for e in diff_packages(added.output_dir, deleted.output_dir).entries}
        self.assertIn(("KnowledgeNode", "DELETE", "C001"), deleted_entries)
        self.assertIn(("SearchDocument", "DELETE", "C001"), deleted_entries)
        self.assertTrue(any(item[0] == "KnowledgeRelation" and item[1] == "DELETE" for item in deleted_entries))

    def test_rebuild_removes_old_resources(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        image = source / "images" / "old.png"
        image.write_bytes(b"old")
        first = self.build("package")
        self.assertTrue((first.output_dir / "resources/images/C001/old.png").exists())

        image.unlink()
        second = self.build("package")

        self.assertFalse((second.output_dir / "resources/images/C001/old.png").exists())
        self.assertEqual(validate_package(second.output_dir), ())

    def test_validation_detects_missing_and_unregistered_resources(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        (source / "images" / "01.png").write_bytes(b"image")
        result = self.build("package")

        (result.output_dir / "resources/images/C001/01.png").unlink()
        errors = validate_package(result.output_dir)
        self.assertTrue(any("resource is missing" in error.message for error in errors))

        extra = result.output_dir / "resources/images/C001/extra.png"
        extra.write_bytes(b"extra")
        errors = validate_package(result.output_dir)
        self.assertTrue(any("do not exactly match" in error.message for error in errors))


if __name__ == "__main__":
    unittest.main()
