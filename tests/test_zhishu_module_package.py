"""Module contract, adversarial ZIP, version isolation and transaction tests.

All mutable content below is synthetic; no formal mathematical asset is edited.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import stat
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from scripts.zhishu import content_package as full
from scripts.zhishu import module_package as module


class ModulePackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = module.temporary_directory()
        self.root = self.temporary.__enter__()
        self.source = self.root / "full"
        self.source.mkdir()
        self.output = self.root / "modules"
        self.data = {
            "knowledgeNodes": [
                {"id": module.ROOT, "title": "高中数学", "sortOrder": 0, "type": "root"},
                {"id": "struct:集合", "title": "集合", "parentId": module.ROOT, "sortOrder": 140, "type": "chapter"},
                {"id": "struct:解析几何", "title": "解析几何", "parentId": module.ROOT, "sortOrder": 120, "type": "chapter"},
                {"id": "struct:逻辑用语", "title": "逻辑用语", "parentId": module.ROOT, "sortOrder": 130, "type": "chapter"},
                {"id": "S001", "title": "Synthetic set", "parentId": "struct:集合", "sortOrder": 10, "type": "knowledge"},
                {"id": "C001", "title": "Synthetic geometry", "parentId": "struct:解析几何", "sortOrder": 10, "type": "knowledge"},
                {"id": "C002", "title": "Synthetic geometry two", "parentId": "struct:解析几何", "sortOrder": 20, "type": "knowledge"},
                {"id": "A001", "title": "Synthetic logic", "parentId": "struct:逻辑用语", "sortOrder": 10, "type": "knowledge"},
            ],
            "knowledgeRelations": [
                {"id": "A001:related:S001", "sourceId": "A001", "targetId": "S001", "type": "related"},
                {"id": "C001:related:C002", "sourceId": "C001", "targetId": "C002", "type": "related"},
                {"id": "C001:related:S001", "sourceId": "C001", "targetId": "S001", "type": "related"},
            ],
            "knowledgeAssets": [], "searchDocuments": [], "animationShares": [],
        }
        for uid in ("S001", "C001", "C002", "A001"):
            node = next(row for row in self.data["knowledgeNodes"] if row["id"] == uid)
            self.data["searchDocuments"].append({"knowledgeNodeId": uid, "title": node["title"], "summary": "fixture"})
            for kind, extension in (("image", ".webp"), ("pdf", ".pdf")):
                uri = f"resources/{'images' if kind == 'image' else 'pdfs'}/{uid}/fixture{extension}"
                path = self.source / uri
                path.parent.mkdir(parents=True, exist_ok=True)
                if kind == "image":
                    Image.new("RGB", (2, 3), "white").save(path, format="WEBP")
                else:
                    path.write_bytes(b"%PDF-1.4\n% synthetic fixture, not a teaching PDF\n")
                self.data["knowledgeAssets"].append({"id": f"{uid}:{kind}:fixture{extension}",
                                                     "knowledgeId": uid, "type": kind,
                                                     "uri": uri, "sortOrder": 10})
        self.write_full()
        self.assertEqual(full.validate_package(self.source), ())
        module.slice_modules(self.source, self.output, ["sets", "analytic-geometry"])

    def tearDown(self):
        self.temporary.__exit__(None, None, None)

    def write_full(self):
        files = {**full.JSON_FILES, "animationShares": full.SHARE_FILE}
        for key, name in files.items():
            full._write_json(self.source / name, self.data[key])
        entities = full._entity_hashes(self.data)
        assets = {row["id"]: full._sha256_file(self.source / row["uri"]) for row in self.data["knowledgeAssets"]}
        counts = {key: len(rows) for key, rows in self.data.items()}
        counts.update(imageAssets=sum(r['type'] == 'image' for r in self.data['knowledgeAssets']),
                      pdfAssets=sum(r['type'] == 'pdf' for r in self.data['knowledgeAssets']), videoAssets=0)
        package_hash = full._package_hash(entities, assets, schema_version=2, share_asset_hashes={})
        full._write_json(self.source / "manifest.json", {
            "schemaVersion": 2, "files": files, "counts": counts, "entityHashes": entities,
            "assetHashes": assets, "shareAssetHashes": {}, "packageHash": package_hash,
            "contentVersion": "sha256:" + package_hash,
            "fileHashes": {key: full._sha256_file(self.source / name) for key, name in files.items()},
        })

    def manifest(self, slug="sets", output=None):
        return module.read_json((output or self.output) / slug / "manifest.json")

    def mutate(self, name, change, slug="sets", reseal=False):
        root = self.output / slug
        value = module.read_json(root / name)
        change(value)
        module.write_json(root / name, value)
        if reseal:
            old = self.manifest(slug)
            data = {k: module.read_json(root / v) for k, v in module.FILES.items()}
            module.write_json(root / "manifest.json", module.make_manifest(root, data, slug,
                              old["sourcePackage"]["contentVersion"], old["packageVersion"]))

    def rejected(self, fragment=None, slug="sets", source=False):
        issues = module.validate_module(self.output / slug, self.source if source else None)
        self.assertTrue(issues, "corruption must be rejected")
        if fragment:
            self.assertIn(fragment, " ".join(issues))

    def zip_attack(self, name, payload=b"attack", mode=None, expected=""):
        archive = self.root / "attack.zip"
        shutil.copyfile(self.output / "sets.zip", archive)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(archive, "a") as stream:
                info = zipfile.ZipInfo(name)
                if mode is not None:
                    info.create_system = 3
                    info.external_attr = mode << 16
                stream.writestr(info, payload)
        issues = module.validate_module(archive)
        self.assertTrue(issues)
        self.assertIn(expected, " ".join(issues))

    def output_hashes(self):
        return {k: full._sha256_file(v) for k, v in module.inventory(self.output).items()}

    def test_both_zip_and_directory_independently_and_against_full(self):
        for slug in ("sets", "analytic-geometry"):
            for path in (self.output / slug, self.output / (slug + ".zip")):
                self.assertEqual(module.validate_module(path), ())
                self.assertEqual(module.validate_module(path, self.source), ())
        a = {r["id"] for r in module.read_json(self.output / "sets/knowledge-nodes.json") if r["type"] == "knowledge"}
        b = {r["id"] for r in module.read_json(self.output / "analytic-geometry/knowledge-nodes.json") if r["type"] == "knowledge"}
        self.assertFalse(a & b)

    def test_external_canonical_source_outside_and_core_dedup(self):
        a = module.read_json(self.output / "sets/external-relations.json")
        b = module.read_json(self.output / "analytic-geometry/external-relations.json")
        edge = next(r for r in a if r["sourceId"] == "A001")
        self.assertEqual(edge["externalEndpointId"], "A001")
        shared_a = next(r for r in a if r["id"] == "C001:related:S001")
        self.assertEqual(shared_a["externalEndpointId"], "C001")
        self.assertEqual(b[0]["externalEndpointId"], "S001")
        core = lambda r: {k: v for k, v in r.items() if k not in module.EXT_FIELDS}
        self.assertEqual(module.digest(core(shared_a)), module.digest(core(b[0])))

    def test_deterministic_zip_bytes_manifest_lists_and_input_unchanged(self):
        before = {k: full._sha256_file(v) for k, v in module.inventory(self.source).items()}
        second = self.root / "second"
        module.slice_modules(self.source, second, ["analytic-geometry", "sets"])
        self.assertEqual(self.output_hashes(), {k: full._sha256_file(v) for k, v in module.inventory(second).items()})
        self.assertEqual(before, {k: full._sha256_file(v) for k, v in module.inventory(self.source).items()})
        module.slice_modules(self.source, self.output, ["sets"])
        self.assertTrue((self.output / "analytic-geometry.zip").is_file())
        with zipfile.ZipFile(self.output / "sets.zip") as stream:
            self.assertEqual(stream.namelist(), sorted(stream.namelist(), key=lambda n: n.encode("utf-8")))
            for info in stream.infolist():
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)

    def test_unrelated_full_change_and_release_ordinal_do_not_change_sets_content(self):
        old_set = self.manifest()
        old_geometry = self.manifest("analytic-geometry")
        next(r for r in self.data["knowledgeNodes"] if r["id"] == "C001")["title"] += " changed"
        self.write_full()
        second = self.root / "second"
        module.slice_modules(self.source, second, ["sets", "analytic-geometry"], 2)
        new_set = self.manifest(output=second)
        self.assertNotEqual(new_set["sourcePackage"], old_set["sourcePackage"])
        self.assertNotEqual(new_set["packageHash"], old_set["packageHash"])
        self.assertEqual(new_set["contentVersion"], old_set["contentVersion"])
        self.assertNotEqual(self.manifest("analytic-geometry", second)["contentVersion"], old_geometry["contentVersion"])

    def test_delete_knowledge_node(self):
        self.mutate("knowledge-nodes.json", lambda r: r.pop())
        self.rejected()

    def test_changed_parent(self):
        self.mutate("knowledge-nodes.json", lambda r: r[-1].update(parentId="missing"), reseal=True)
        self.rejected("unknown parentId")

    def test_tree_cycle(self):
        self.mutate("knowledge-nodes.json", lambda r: r[-1].update(parentId=r[-1]["id"]), reseal=True)
        self.rejected()

    def test_missing_pdf(self):
        (self.output / "sets/resources/pdfs/S001/fixture.pdf").unlink()
        self.rejected("missing/extra")

    def test_tampered_image(self):
        (self.output / "sets/resources/images/S001/fixture.webp").write_bytes(b"corrupt")
        self.rejected()

    def test_tampered_manifest_hash(self):
        self.mutate("manifest.json", lambda r: r.update(packageHash="0" * 64))
        self.rejected("integrity hash mismatch")

    def test_zip_path_traversal(self):
        self.zip_attack("../escape.txt", expected="unsafe path")

    def test_internal_unknown_endpoint(self):
        self.mutate("knowledge-relations.json", lambda r: r.append({"id": "S001:related:Z999", "sourceId": "S001", "targetId": "Z999", "type": "related"}), reseal=True)
        self.rejected("internal relation unknown endpoint")

    def test_duplicate_knowledge_id(self):
        self.mutate("knowledge-nodes.json", lambda r: r.append(copy.deepcopy(r[-1])), reseal=True)
        self.rejected("duplicate ID")

    def test_incomplete_search_documents(self):
        self.mutate("search-documents.json", lambda r: r.clear(), reseal=True)
        self.rejected("coverage mismatch")

    def test_wrong_package_type(self):
        self.mutate("manifest.json", lambda r: r.update(packageKind="collection"))
        self.rejected("package type")

    def test_wrong_schema(self):
        self.mutate("manifest.json", lambda r: r.update(schemaVersion=3))
        self.rejected("schemaVersion")

    def test_external_edge_wrongly_internal(self):
        root = self.output / "sets"
        ext = module.read_json(root / "external-relations.json")
        row = ext.pop()
        row = {k: v for k, v in row.items() if k not in module.EXT_FIELDS}
        module.write_json(root / "external-relations.json", ext)
        module.write_json(root / "knowledge-relations.json", [row])
        self.rejected("internal relation unknown endpoint")

    def test_damaged_full_input_rejected_old_output_preserved(self):
        before = self.output_hashes()
        (self.source / "resources/pdfs/S001/fixture.pdf").write_bytes(b"bad")
        with self.assertRaisesRegex(module.ModuleError, "Full v2 validation failed"):
            module.slice_modules(self.source, self.output, ["sets"])
        self.assertEqual(before, self.output_hashes())

    def test_consistently_rehashed_omission_detected_against_full(self):
        self.mutate("knowledge-relations.json", lambda r: r.clear(), "analytic-geometry", reseal=True)
        self.assertEqual(module.validate_module(self.output / "analytic-geometry"), ())
        self.rejected("Full v2 consistency mismatch", "analytic-geometry", source=True)

    def test_consistently_rehashed_content_change_detected_against_full(self):
        self.mutate("knowledge-nodes.json", lambda r: r[-1].update(title="wrong"), reseal=True)
        self.rejected("Full v2 consistency mismatch", source=True)

    def test_consistently_rehashed_whole_knowledge_omission_detected(self):
        slug = "analytic-geometry"
        root = self.output / slug
        old = self.manifest(slug)
        data = {key: module.read_json(root / name) for key, name in module.FILES.items()}
        removed = [r for r in data["knowledgeAssets"] if r["knowledgeId"] == "C002"]
        data["knowledgeNodes"] = [r for r in data["knowledgeNodes"] if r["id"] != "C002"]
        data["searchDocuments"] = [r for r in data["searchDocuments"] if r["knowledgeNodeId"] != "C002"]
        data["knowledgeAssets"] = [r for r in data["knowledgeAssets"] if r["knowledgeId"] != "C002"]
        data["knowledgeRelations"] = []
        for row in removed:
            (root / row["uri"]).unlink()
        for key, name in module.FILES.items():
            module.write_json(root / name, data[key])
        module.write_json(root / "manifest.json", module.make_manifest(root, data, slug,
                          old["sourcePackage"]["contentVersion"], 1))
        self.assertEqual(module.validate_module(root), ())
        self.rejected("Full v2 consistency mismatch", slug, source=True)

    def test_external_missing_or_wrong_missing_endpoint(self):
        self.mutate("external-relations.json", lambda r: r[0].update(externalEndpointId="S001"), reseal=True)
        self.rejected("invalid external")

    def test_failed_second_module_keeps_all_previous_outputs(self):
        before = self.output_hashes()
        original = module.write_zip
        def fail_second(root, destination):
            if root.name == "analytic-geometry":
                raise OSError("injected second-module disk failure")
            return original(root, destination)
        with patch.object(module, "write_zip", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "injected"):
                module.slice_modules(self.source, self.output, ["sets", "analytic-geometry"])
        self.assertEqual(before, self.output_hashes())
        self.assertFalse(list(self.root.glob(".modules.tmp-*")))

    def test_commit_rename_failure_restores_previous_output(self):
        before = self.output_hashes()
        original = os.replace
        calls = 0
        def fail_commit(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected commit failure")
            return original(src, dst)
        with patch.object(module.os, "replace", side_effect=fail_commit):
            with self.assertRaisesRegex(OSError, "injected"):
                module.slice_modules(self.source, self.output, ["sets"])
        self.assertEqual(before, self.output_hashes())

    def test_version_reuse_and_downgrade_rejected(self):
        before = self.output_hashes()
        self.data["knowledgeNodes"][-1]["title"] += " unrelated change"
        self.write_full()
        with self.assertRaisesRegex(module.ModuleError, "VERSION_REUSE"):
            module.slice_modules(self.source, self.output, ["sets"])
        self.assertEqual(before, self.output_hashes())
        module.slice_modules(self.source, self.output, ["sets"], 2)
        with self.assertRaisesRegex(module.ModuleError, "downgrade"):
            module.slice_modules(self.source, self.output, ["sets"], 1)

    def test_input_output_overlap_refused(self):
        for output in (self.source, self.source / "child", self.root):
            with self.assertRaisesRegex(module.ModuleError, "isolated"):
                module.slice_modules(self.source, output, ["sets"])

    def test_unrelated_output_file_not_removed(self):
        path = self.output / "important.txt"
        path.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(module.ModuleError, "unrelated files"):
            module.slice_modules(self.source, self.output, ["sets"])
        self.assertEqual(path.read_text(), "keep")

    def test_zip_duplicate_entry(self):
        self.zip_attack("manifest.json", expected="duplicate/conflicting")

    def test_zip_case_collision(self):
        self.zip_attack("MANIFEST.JSON", expected="duplicate/conflicting")

    def test_zip_link(self):
        self.zip_attack("link", b"manifest.json", stat.S_IFLNK | 0o777, "link/non-regular")

    def test_zip_undeclared_resource(self):
        self.zip_attack("resources/pdfs/S001/extra.pdf", expected="missing/extra")

    def test_zip_windows_reserved_filename(self):
        self.zip_attack("resources/pdfs/S001/CON.pdf", expected="unsafe path")

    def test_zip_file_directory_conflict(self):
        self.zip_attack("manifest.json/child", expected="file/directory conflict")

    def test_zip_json_size_limit(self):
        with patch.object(module, "MAX_JSON_BYTES", 16):
            self.assertIn("JSON size limit", " ".join(module.validate_module(self.output / "sets.zip")))

    def test_duplicate_json_object_key(self):
        path = self.output / "sets/manifest.json"
        path.write_bytes(b'{"schemaVersion":4,"schemaVersion":4}')
        self.rejected("duplicate JSON key")

    def test_boolean_count_is_not_integer(self):
        self.mutate("manifest.json", lambda r: r["counts"].update(externalRelations=True))
        self.rejected("counts integer")

    def test_boolean_resource_bytes_is_not_integer(self):
        self.mutate("manifest.json", lambda r: next(iter(r["resources"].values())).update(bytes=True))
        self.rejected("bytes integer")

    def test_manifest_unknown_field_and_nonfinite_numbers(self):
        self.mutate("manifest.json", lambda r: r.update(unrecognized="field"))
        self.rejected("unknown fields")
        path = self.output / "sets/manifest.json"
        path.write_bytes(b'{"schemaVersion":NaN}')
        self.rejected("non-finite")


if __name__ == "__main__":
    unittest.main()
