"""Share text travels through the real mapper, Full writer and v4 ZIP slicer."""
from __future__ import annotations

import json
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path

from scripts.zhishu import content_package as full
from scripts.zhishu import module_package as module
from scripts.zhishu.runtime_mapping import map_runtime
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository
from tests.test_zhishu_content_package import meta_record


class ShareConfigExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = module.temporary_directory()
        self.root = self.temporary.__enter__()
        self.project = self.root / "source"
        self.paths = {}
        for name in MODULE_NAMES:
            (self.project / name).mkdir(parents=True)
        for uid, title, category in (
            ("C001", "原始数学标题一", "解析几何-圆锥曲线-椭圆"),
            ("C002", "原始数学标题二", "解析几何-圆锥曲线-椭圆"),
            ("F001", "原始函数标题", "函数-性质-单调性"),
        ):
            folder = self.project / ("01_function" if uid[0] == "F" else "03_conic") / (uid + "_fixture")
            folder.mkdir()
            (folder / "images").mkdir()
            (folder / "pdfs").mkdir()
            self.paths[uid] = folder / "meta.json"
            self.write(uid, meta_record(uid, title, knowledge_node=category))

    def tearDown(self):
        self.temporary.__exit__(None, None, None)

    def read(self, uid):
        return json.loads(self.paths[uid].read_text(encoding="utf-8"))

    def write(self, uid, record):
        self.paths[uid].write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")

    def configure(self, uid, value):
        record = self.read(uid)
        record["shareConfig"] = value
        self.write(uid, record)

    def mapped(self):
        scan = scan_repository(self.project)
        return scan, map_runtime(scan, self.root / "prepared")

    def build(self, name, version=1):
        scan, runtime = self.mapped()
        self.assertEqual(runtime.errors, ())
        source = self.root / name / "full"
        result = full.build_package(scan, runtime, source, self.root / "prepared")
        self.assertEqual(result.errors, ())
        self.assertEqual(full.validate_package(source), ())
        output = self.root / name / "modules"
        module.slice_modules(source, output, ["analytic-geometry", "functions"], version)
        for slug in ("analytic-geometry", "functions"):
            self.assertEqual(module.validate_module(output / (slug + ".zip"), source), ())
        return source, output

    def nodes(self, output, slug="analytic-geometry"):
        with zipfile.ZipFile(output / (slug + ".zip")) as archive:
            return {row["id"]: row for row in json.loads(archive.read("knowledge-nodes.json"))}

    def manifest(self, output, slug="analytic-geometry"):
        with zipfile.ZipFile(output / (slug + ".zip")) as archive:
            return json.loads(archive.read("manifest.json"))

    def test_complete_config_and_two_sources_reach_actual_zip_without_cross_talk(self):
        first = {"title": "切线：已知切点就少联立！", "shareDesc": "保留中文标点、≤、α²、∑，以及 e\u0301。\n下一行。"}
        second = {"title": "另一个知识点的标题", "shareDesc": "第二条自己的描述。"}
        self.configure("C001", first)
        self.configure("C002", second)
        before = {uid: path.read_bytes() for uid, path in self.paths.items()}
        source, output = self.build("complete")
        nodes = self.nodes(output)
        self.assertEqual(nodes["C001"]["shareConfig"], first)
        self.assertEqual(nodes["C002"]["shareConfig"], second)
        self.assertEqual(nodes["C001"]["title"], "原始数学标题一")
        self.assertEqual(nodes["C001"]["id"], "C001")
        search = module.read_json(source / "search-documents.json")
        self.assertEqual(next(r for r in search if r["knowledgeNodeId"] == "C001")["summary"], "原始数学标题一摘要")
        self.assertEqual(before, {uid: path.read_bytes() for uid, path in self.paths.items()})
        self.assertTrue(all("shareConfig" not in n for n in nodes.values() if n["type"] != "knowledge"))

    def test_legacy_optional_forms_survive_full_and_zip(self):
        for index, (value, expected) in enumerate((
            ({"title": "只有标题"}, {"title": "只有标题"}),
            ({"shareDesc": "只有描述"}, {"shareDesc": "只有描述"}),
            (None, None), ({}, None),
            ({"title": None, "shareDesc": None}, None),
            ({"title": None, "shareDesc": "保留描述"}, {"shareDesc": "保留描述"}),
            ({"title": "", "shareDesc": " \t\n　"}, {"title": "", "shareDesc": " \t\n　"}),
            ({"title": "  不要修剪  ", "imageUrl": "legacy.png"}, {"title": "  不要修剪  "}),
        )):
            with self.subTest(value=value):
                self.configure("C001", value)
                source, output = self.build("optional-" + str(index))
                self.assertEqual(self.nodes(output)["C001"].get("shareConfig"), expected)
                self.assertEqual(next(r for r in module.read_json(source / "knowledge-nodes.json") if r["id"] == "C001").get("shareConfig"), expected)

    def test_absent_config_stays_absent_in_final_zip(self):
        _, output = self.build("absent")
        self.assertNotIn("shareConfig", self.nodes(output)["C001"])

    def test_invalid_source_types_are_path_qualified_errors_and_block_build(self):
        for value in ("bad", 1, False, [], {"title": 2}, {"title": []}, {"shareDesc": {}}, {"shareDesc": False}):
            with self.subTest(value=value):
                self.configure("C001", value)
                scan, runtime = self.mapped()
                self.assertTrue(any("shareConfig" in e.message and e.path == Path("03_conic/C001_fixture/meta.json") for e in runtime.errors))
                target = self.root / "invalid"
                result = full.build_package(scan, runtime, target, self.root / "prepared")
                self.assertTrue(result.errors)
                self.assertFalse(target.exists())

    def test_package_validators_reject_invalid_share_fields(self):
        source, output = self.build("corrupt")
        for value in (7, [], {"title": 1}, {"shareDesc": ["not text"]}):
            with self.subTest(value=value):
                rows = module.read_json(source / "knowledge-nodes.json")
                rows[-1]["shareConfig"] = value
                full._write_json(source / "knowledge-nodes.json", rows)
                self.assertTrue(any("shareConfig" in e.message for e in full.validate_package(source)))
                directory = output / "analytic-geometry"
                rows = module.read_json(directory / "knowledge-nodes.json")
                rows[-1]["shareConfig"] = value
                module.write_json(directory / "knowledge-nodes.json", rows)
                self.assertIn("shareConfig", " ".join(module.validate_module(directory)))

    def test_only_share_change_updates_entity_file_package_and_local_content_hash(self):
        self.configure("C001", {"title": "原分享标题", "shareDesc": "原描述"})
        source1, output1 = self.build("before")
        self.configure("C001", {"title": "原分享标题", "shareDesc": "只更新描述≤2"})
        source2, output2 = self.build("after", version=2)
        old, new = self.manifest(output1), self.manifest(output2)
        self.assertNotEqual(old["entityHashes"]["knowledgeNodes"]["C001"], new["entityHashes"]["knowledgeNodes"]["C001"])
        self.assertEqual(old["entityHashes"]["knowledgeNodes"]["C002"], new["entityHashes"]["knowledgeNodes"]["C002"])
        for key in ("packageHash", "contentVersion"):
            self.assertNotEqual(old[key], new[key])
        self.assertNotEqual(old["fileHashes"]["knowledgeNodes"], new["fileHashes"]["knowledgeNodes"])
        self.assertEqual(self.manifest(output1, "functions")["contentVersion"], self.manifest(output2, "functions")["contentVersion"])
        self.assertNotEqual(module.read_json(source1 / "manifest.json")["contentVersion"], module.read_json(source2 / "manifest.json")["contentVersion"])
        self.assertEqual(old["requiredCapabilities"], new["requiredCapabilities"])
        self.assertEqual(new["schemaVersion"], 4)
        before_nodes, after_nodes = self.nodes(output1), self.nodes(output2)
        for nodes in (before_nodes, after_nodes):
            nodes["C001"].pop("shareConfig")
        self.assertEqual(before_nodes, after_nodes)
        self.assertEqual((source1 / "search-documents.json").read_bytes(), (source2 / "search-documents.json").read_bytes())

    def test_same_source_produces_identical_json_hashes_and_zip_bytes(self):
        self.configure("C001", {"title": "确定性：α ≤ β", "shareDesc": "原样保留，重复导出。"})
        source1, output1 = self.build("repeat-one")
        source2, output2 = self.build("repeat-two")
        for name in ("manifest.json", *full.JSON_FILES.values(), full.SHARE_FILE):
            self.assertEqual((source1 / name).read_bytes(), (source2 / name).read_bytes())
        for slug in ("analytic-geometry", "functions"):
            self.assertEqual((output1 / (slug + ".zip")).read_bytes(), (output2 / (slug + ".zip")).read_bytes())

    def test_existing_short_title_survives_dto_serialization(self):
        _, runtime = self.mapped()
        original = next(n for n in runtime.knowledge_nodes if n.id == "C001")
        replacement = replace(original, shortTitle="已有短标题", shareConfig={"title": "独立分享标题"})
        result = replace(runtime, knowledge_nodes=tuple(replacement if n.id == original.id else n for n in runtime.knowledge_nodes))
        node = next(n for n in full._runtime_entities(result)["knowledgeNodes"] if n["id"] == "C001")
        self.assertEqual(node["shortTitle"], "已有短标题")
        self.assertEqual(node["title"], original.title)


if __name__ == "__main__":
    unittest.main()
