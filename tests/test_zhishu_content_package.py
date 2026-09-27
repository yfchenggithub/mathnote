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
    knowledge_node: str = "解析几何-圆锥曲线-椭圆",
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
        "knowledgeNode": knowledge_node,
        "altNodes": [],
    }


class ContentPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project_root = self.root / "source"
        self.packages = self.root / "packages"
        self.prepared_assets = self.root / "prepared"
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
        shutil.rmtree(self.prepared_assets, ignore_errors=True)
        for source_image in self.project_root.rglob("images/*.png"):
            source_id = json.loads(
                (source_image.parent.parent / "meta.json").read_text(encoding="utf-8")
            )["id"]
            output = self.prepared_assets / "images" / source_id / f"{source_image.stem}.webp"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(source_image.read_bytes())
        scan_result = scan_repository(self.project_root)
        mapping_result = map_runtime(scan_result, self.prepared_assets)
        self.assertEqual(mapping_result.errors, ())
        result = build_package(
            scan_result, mapping_result, self.packages / name, self.prepared_assets
        )
        self.assertEqual(result.errors, ())
        return result

    @staticmethod
    def package_bytes(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    @staticmethod
    def read_json(path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def write_json(path: Path, value) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def copy_package(self, source: Path, name: str) -> Path:
        destination = self.packages / name
        shutil.copytree(source, destination)
        return destination

    @staticmethod
    def error_messages(package: Path) -> list[str]:
        return [issue.message for issue in validate_package(package)]

    def test_repeated_packages_are_byte_identical_and_versions_stable(self) -> None:
        self.create_source(
            meta_record("C001", "结论一", related_ids=["C002", "C002"])
        )
        self.create_source(
            meta_record("C002", "结论二", related_ids=["C001"])
        )

        first = self.build("first")
        second = self.build("second")

        self.assertEqual(first.content_version, second.content_version)
        self.assertEqual(first.package_hash, second.package_hash)
        self.assertEqual(first.counts["knowledgeRelations"], 1)
        self.assertEqual(
            (first.output_dir / "knowledge-relations.json").read_bytes(),
            (second.output_dir / "knowledge-relations.json").read_bytes(),
        )
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
        self.assertTrue((root / "resources/images/C006/01.webp").is_file())
        self.assertTrue((root / "resources/pdfs/C006/01.pdf").is_file())
        self.assertEqual(validate_package(root), ())
        assets = self.read_json(root / "knowledge-assets.json")
        self.assertTrue(all("uri" in asset for asset in assets))
        self.assertTrue(all("url" not in asset for asset in assets))

    def test_manifest_required_fields_are_explicitly_required(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        pristine = self.build("pristine").output_dir

        for field in ("schemaVersion", "contentVersion", "packageHash", "counts", "files"):
            with self.subTest(field=field):
                package = self.copy_package(pristine, f"missing-{field}")
                manifest_path = package / "manifest.json"
                manifest = self.read_json(manifest_path)
                del manifest[field]
                self.write_json(manifest_path, manifest)

                messages = self.error_messages(package)

                self.assertIn(f"missing required field: {field}", messages)

    def test_manifest_field_types_and_count_types_are_validated(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        pristine = self.build("pristine-types").output_dir
        cases = (
            ("schemaVersion", "1", "schemaVersion must be an integer"),
            ("contentVersion", 1, "contentVersion must be a string"),
            ("packageHash", 1, "packageHash must be a string"),
            ("counts", [], "counts must be an object"),
            ("files", [], "files must be an object"),
        )
        for index, (field, value, expected) in enumerate(cases):
            with self.subTest(field=field):
                package = self.copy_package(pristine, f"wrong-type-{index}")
                manifest_path = package / "manifest.json"
                manifest = self.read_json(manifest_path)
                manifest[field] = value
                self.write_json(manifest_path, manifest)

                self.assertIn(expected, self.error_messages(package))

        package = self.copy_package(pristine, "wrong-count-type")
        manifest_path = package / "manifest.json"
        manifest = self.read_json(manifest_path)
        manifest["counts"]["knowledgeNodes"] = "1"
        self.write_json(manifest_path, manifest)
        self.assertIn(
            "counts.knowledgeNodes must be an integer",
            self.error_messages(package),
        )

    def test_manifest_files_requires_every_runtime_entry(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        package = self.build("missing-runtime-entry").output_dir
        manifest_path = package / "manifest.json"
        manifest = self.read_json(manifest_path)
        del manifest["files"]["knowledgeAssets"]
        self.write_json(manifest_path, manifest)

        self.assertIn(
            "files.knowledgeAssets must be a non-empty string path",
            self.error_messages(package),
        )

    def test_runtime_json_top_level_must_be_array_of_objects(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        package = self.build("bad-runtime-root").output_dir
        self.write_json(package / "knowledge-nodes.json", {})

        self.assertIn(
            "file must contain an array of objects",
            self.error_messages(package),
        )

    def test_malformed_manifest_and_runtime_json_return_structured_errors(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        pristine = self.build("malformed-json-pristine").output_dir

        bad_manifest = self.copy_package(pristine, "bad-manifest-json")
        (bad_manifest / "manifest.json").write_text("{", encoding="utf-8")
        manifest_errors = validate_package(bad_manifest)
        self.assertTrue(manifest_errors)
        self.assertIn("manifest is invalid JSON", manifest_errors[0].message)

        bad_runtime = self.copy_package(pristine, "bad-runtime-json")
        (bad_runtime / "knowledge-nodes.json").write_text("[", encoding="utf-8")
        runtime_errors = validate_package(bad_runtime)
        self.assertTrue(runtime_errors)
        self.assertTrue(any("invalid JSON" in issue.message for issue in runtime_errors))

    def test_runtime_entities_require_identity_and_contract_fields(self) -> None:
        first = self.create_source(meta_record("C001", "结论一"))
        (first / "images" / "01.png").write_bytes(b"image")
        self.create_source(meta_record("C002", "结论二", related_ids=["C001"]))
        pristine = self.build("entity-pristine").output_dir
        cases = {
            "knowledge-nodes.json": ("id",),
            "knowledge-relations.json": ("id", "sourceId", "targetId", "type"),
            "knowledge-assets.json": ("id", "knowledgeId", "type", "uri", "sortOrder"),
            "search-documents.json": ("knowledgeNodeId", "title"),
        }
        case_number = 0
        for file_name, fields in cases.items():
            for field in fields:
                with self.subTest(file=file_name, field=field):
                    package = self.copy_package(pristine, f"entity-{case_number}")
                    case_number += 1
                    path = package / file_name
                    records = self.read_json(path)
                    del records[0][field]
                    self.write_json(path, records)

                    messages = self.error_messages(package)

                    self.assertTrue(
                        any(f"missing required field: {field}" in message for message in messages),
                        messages,
                    )

    def test_validation_rejects_reverse_duplicate_related_pair(self) -> None:
        self.create_source(meta_record("C001", "结论一", related_ids=["C002"]))
        self.create_source(meta_record("C002", "结论二"))
        package = self.build("reverse-duplicate").output_dir
        relations_path = package / "knowledge-relations.json"
        relations = self.read_json(relations_path)
        relations.append(
            {
                "id": "reverse-related-id",
                "sourceId": "C002",
                "targetId": "C001",
                "type": "related",
            }
        )
        self.write_json(relations_path, relations)

        self.assertIn(
            "duplicate symmetric related relation: C001 <-> C002",
            self.error_messages(package),
        )

    def test_validation_rejects_same_direction_duplicate_related_pair(self) -> None:
        self.create_source(meta_record("C001", "结论一", related_ids=["C002"]))
        self.create_source(meta_record("C002", "结论二"))
        package = self.build("same-direction-duplicate").output_dir
        relations_path = package / "knowledge-relations.json"
        relations = self.read_json(relations_path)
        duplicate = dict(relations[0])
        duplicate["id"] = "same-direction-related-id"
        relations.append(duplicate)
        self.write_json(relations_path, relations)

        self.assertIn(
            "duplicate symmetric related relation: C001 <-> C002",
            self.error_messages(package),
        )

    def test_validation_rejects_self_relation(self) -> None:
        self.create_source(meta_record("C001", "结论一"))
        package = self.build("self-relation").output_dir
        relations_path = package / "knowledge-relations.json"
        self.write_json(
            relations_path,
            [
                {
                    "id": "C001:related:C001",
                    "sourceId": "C001",
                    "targetId": "C001",
                    "type": "related",
                }
            ],
        )

        self.assertIn(
            "self relation is not allowed: C001:related:C001",
            self.error_messages(package),
        )

    def test_manifest_counts_tampering_is_detected(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        package = self.build("bad-counts").output_dir
        manifest_path = package / "manifest.json"
        manifest = self.read_json(manifest_path)
        manifest["counts"]["knowledgeNodes"] += 1
        self.write_json(manifest_path, manifest)

        self.assertIn(
            "manifest counts do not match package data",
            self.error_messages(package),
        )

    def test_runtime_file_hash_tampering_is_detected(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        package = self.build("bad-runtime-hash").output_dir
        path = package / "knowledge-nodes.json"
        records = self.read_json(path)
        records[-1]["title"] = "篡改标题"
        self.write_json(path, records)

        self.assertIn(
            "file hashes do not match package JSON files",
            self.error_messages(package),
        )

    def test_asset_hash_tampering_is_detected(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        (source / "images" / "01.png").write_bytes(b"original")
        package = self.build("bad-asset-hash").output_dir
        (package / "resources/images/C001/01.webp").write_bytes(b"tampered")

        self.assertIn(
            "asset hashes do not match resource contents",
            self.error_messages(package),
        )

    def test_package_hash_tampering_is_detected(self) -> None:
        self.create_source(meta_record("C001", "结论"))
        package = self.build("bad-package-hash").output_dir
        manifest_path = package / "manifest.json"
        manifest = self.read_json(manifest_path)
        manifest["packageHash"] = "0" * 64
        self.write_json(manifest_path, manifest)

        self.assertIn("packageHash mismatch", self.error_messages(package))

    def test_diff_rejects_invalid_previous_and_current_packages(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        (source / "images" / "01.png").write_bytes(b"image")
        pristine = self.build("diff-pristine").output_dir

        invalid_previous = self.copy_package(pristine, "invalid-previous")
        manifest = self.read_json(invalid_previous / "manifest.json")
        del manifest["files"]
        self.write_json(invalid_previous / "manifest.json", manifest)
        previous_diff = diff_packages(invalid_previous, pristine)
        self.assertEqual(previous_diff.entries, ())
        self.assertTrue(previous_diff.errors)
        self.assertTrue(all(issue.path.parts[0] == "previous" for issue in previous_diff.errors))

        invalid_current = self.copy_package(pristine, "invalid-current")
        assets_path = invalid_current / "knowledge-assets.json"
        assets = self.read_json(assets_path)
        del assets[0]["id"]
        self.write_json(assets_path, assets)
        current_diff = diff_packages(pristine, invalid_current)
        self.assertEqual(current_diff.entries, ())
        self.assertTrue(current_diff.errors)
        self.assertTrue(all(issue.path.parts[0] == "current" for issue in current_diff.errors))

    def test_runtime_mapping_warnings_are_preserved_in_build_result(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        shutil.rmtree(source / "images")
        shutil.rmtree(source / "pdfs")
        scan_result = scan_repository(self.project_root)
        mapping_result = map_runtime(scan_result, self.prepared_assets)

        result = build_package(
            scan_result,
            mapping_result,
            self.packages / "warnings",
            self.prepared_assets,
        )

        self.assertEqual(result.errors, ())
        self.assertEqual(len(result.warnings), 2)
        self.assertTrue(any("images directory is missing" in issue.message for issue in result.warnings))
        self.assertTrue(any("pdfs directory is missing" in issue.message for issue in result.warnings))

    def test_title_and_search_changes_are_updates(self) -> None:
        source = self.create_source(meta_record("C001", "旧标题", keyword="旧关键词"))
        previous = self.build("previous")
        data = meta_record("C001", "新标题", keyword="新关键词")
        (source / "meta.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        current = self.build("current")

        diff = diff_packages(previous.output_dir, current.output_dir)

        self.assertIn(("KnowledgeNode", "UPDATE", "C001"), {(e.entity_type, e.operation, e.entity_id) for e in diff.entries})
        self.assertIn(("SearchDocument", "UPDATE", "C001"), {(e.entity_type, e.operation, e.entity_id) for e in diff.entries})
        self.assertNotEqual(previous.package_hash, current.package_hash)
        self.assertNotEqual(previous.content_version, current.content_version)

    def test_knowledge_path_and_related_ids_changes_are_precise(self) -> None:
        self.create_source(meta_record("C001", "结论一"))
        self.create_source(meta_record("C002", "结论二"))
        source = self.create_source(meta_record("C003", "结论三", related_ids=["C001"]))
        previous = self.build("previous")

        changed_record = meta_record(
            "C003",
            "结论三",
            related_ids=["C001", "C002"],
            knowledge_node="解析几何-综合-最值问题",
        )
        (source / "meta.json").write_text(
            json.dumps(changed_record, ensure_ascii=False), encoding="utf-8"
        )
        changed = self.build("changed")
        changed_entries = {
            (entry.entity_type, entry.operation, entry.entity_id)
            for entry in diff_packages(previous.output_dir, changed.output_dir).entries
        }

        self.assertIn(("KnowledgeNode", "UPDATE", "C003"), changed_entries)
        self.assertIn(("KnowledgeRelation", "ADD", "C002:related:C003"), changed_entries)

        changed_record["relations"]["related_ids"] = ["C002"]
        (source / "meta.json").write_text(
            json.dumps(changed_record, ensure_ascii=False), encoding="utf-8"
        )
        removed = self.build("removed")
        removed_entries = {
            (entry.entity_type, entry.operation, entry.entity_id)
            for entry in diff_packages(changed.output_dir, removed.output_dir).entries
        }
        self.assertIn(
            ("KnowledgeRelation", "DELETE", "C001:related:C003"),
            removed_entries,
        )

    def test_asset_content_add_and_delete_diff(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        image = source / "images" / "01.png"
        image.write_bytes(b"old")
        previous = self.build("previous")

        image.write_bytes(b"new")
        added = source / "images" / "02.png"
        added.write_bytes(b"two")
        pdf = source / "pdfs" / "01.pdf"
        pdf.write_bytes(b"pdf")
        changed = self.build("changed")
        changed_diff = diff_packages(previous.output_dir, changed.output_dir)
        entries = {(e.operation, e.entity_id) for e in changed_diff.entries if e.entity_type == "KnowledgeAsset"}
        self.assertIn(("UPDATE", "C001:image:01.webp"), entries)
        self.assertIn(("ADD", "C001:image:02.webp"), entries)
        self.assertIn(("ADD", "C001:pdf:01.pdf"), entries)

        image.unlink()
        added.unlink()
        pdf.unlink()
        removed = self.build("removed")
        removed_diff = diff_packages(changed.output_dir, removed.output_dir)
        deleted = {(e.operation, e.entity_id) for e in removed_diff.entries if e.entity_type == "KnowledgeAsset"}
        self.assertEqual(deleted, {
            ("DELETE", "C001:image:01.webp"),
            ("DELETE", "C001:image:02.webp"),
            ("DELETE", "C001:pdf:01.pdf"),
        })

    def test_add_and_delete_conclusion_and_relation(self) -> None:
        first_source = self.create_source(meta_record("C001", "结论一"))
        (first_source / "images" / "01.png").write_bytes(b"image")
        (first_source / "pdfs" / "01.pdf").write_bytes(b"pdf")
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
        self.assertIn(("KnowledgeAsset", "DELETE", "C001:image:01.webp"), deleted_entries)
        self.assertIn(("KnowledgeAsset", "DELETE", "C001:pdf:01.pdf"), deleted_entries)
        self.assertTrue(any(item[0] == "KnowledgeRelation" and item[1] == "DELETE" for item in deleted_entries))
        self.assertFalse((deleted.output_dir / "resources/images/C001").exists())
        self.assertFalse((deleted.output_dir / "resources/pdfs/C001").exists())

    def test_rebuild_removes_old_resources(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        image = source / "images" / "old.png"
        image.write_bytes(b"old")
        first = self.build("package")
        self.assertTrue((first.output_dir / "resources/images/C001/old.webp").exists())

        image.unlink()
        second = self.build("package")

        self.assertFalse((second.output_dir / "resources/images/C001/old.webp").exists())
        self.assertEqual(validate_package(second.output_dir), ())

    def test_validation_detects_missing_and_unregistered_resources(self) -> None:
        source = self.create_source(meta_record("C001", "结论"))
        (source / "images" / "01.png").write_bytes(b"image")
        result = self.build("package")

        (result.output_dir / "resources/images/C001/01.webp").unlink()
        errors = validate_package(result.output_dir)
        self.assertTrue(any("resource is missing" in error.message for error in errors))

        extra = result.output_dir / "resources/images/C001/extra.webp"
        extra.write_bytes(b"extra")
        errors = validate_package(result.output_dir)
        self.assertTrue(any("do not exactly match" in error.message for error in errors))


if __name__ == "__main__":
    unittest.main()
