from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.zhishu.runtime_mapping import map_runtime, structural_node_id
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository


def meta_record(
    source_id: str,
    title: str,
    knowledge_node: str,
    *,
    alt_nodes: list[str] | None = None,
    prerequisites: list[str] | None = None,
    related_ids: list[str] | None = None,
    similar: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": source_id,
        "core": {
            "title": title,
            "alias": [f"{title}别名"],
            "summary": f"{title}摘要",
            "difficulty": 3,
            "category": "解析几何",
            "tags": ["标签"],
        },
        "search": {
            "keywords": ["关键词"],
            "synonyms": ["同义词"],
            "intents": ["证明"],
            "query_templates": ["怎么用"],
            "ocrKeywords": ["识别词"],
            "latex_patterns": ["x^2"],
            "formulaTokens": ["x"],
            "pinyin": "tuo yuan",
            "pinyinAbbr": "ty",
        },
        "searchmeta": {
            "titleWeight": 10,
            "keywordWeight": 8,
            "synonymWeight": 6,
            "formulaWeight": 7,
        },
        "ranking": {
            "search_boost": 0.5,
            "hot_score": 98,
            "click_rate": 0,
            "success_rate": 0,
        },
        "relations": {
            "prerequisites": prerequisites or [],
            "related_ids": related_ids or [],
            "similar": similar or [],
        },
        "knowledgeNode": knowledge_node,
        "altNodes": alt_nodes or [],
    }


class RuntimeMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        for module_name in MODULE_NAMES:
            (self.project_root / module_name).mkdir()

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

    def map(self):
        return map_runtime(scan_repository(self.project_root))

    def test_path_splitting_merges_structural_nodes_and_sets_parent(self) -> None:
        self.create_source(meta_record("C001", "结论一", "解析几何-圆锥曲线-椭圆"))
        self.create_source(meta_record("C002", "结论二", "解析几何-圆锥曲线-双曲线"))

        result = self.map()
        structures = {node.id: node for node in result.knowledge_nodes if node.type != "knowledge"}
        conclusions = {node.id: node for node in result.knowledge_nodes if node.type == "knowledge"}

        self.assertEqual(len(structures), 5)
        self.assertEqual(
            structures[structural_node_id("解析几何-圆锥曲线")].parentId,
            structural_node_id("解析几何"),
        )
        self.assertEqual(structures[structural_node_id("解析几何")].type, "chapter")
        self.assertEqual(
            conclusions["C001"].parentId,
            structural_node_id("解析几何-圆锥曲线-椭圆"),
        )

    def test_conclusion_id_is_meta_id_and_alt_nodes_are_ignored(self) -> None:
        self.create_source(
            meta_record(
                "C006",
                "离心率",
                "解析几何-圆锥曲线-椭圆",
                alt_nodes=["解析几何-综合-最值问题", "解析几何-综合-最值问题"],
            )
        )

        result = self.map()

        conclusion_nodes = [node for node in result.knowledge_nodes if node.type == "knowledge"]
        self.assertEqual([node.id for node in conclusion_nodes], ["C006"])
        self.assertFalse(any(node.id == structural_node_id("解析几何-综合-最值问题") for node in result.knowledge_nodes))
        self.assertEqual(result.errors, ())

    def test_related_ids_resolve_without_reverse_edges(self) -> None:
        self.create_source(meta_record("C001", "一", "解析几何-甲"))
        self.create_source(meta_record("C002", "二", "解析几何-乙"))
        self.create_source(
            meta_record(
                "C003",
                "三",
                "解析几何-丙",
                prerequisites=["not-considered"],
                related_ids=["C002"],
                similar=["not-considered"],
            )
        )

        result = self.map()

        edges = {(item.sourceId, item.type, item.targetId) for item in result.relations}
        self.assertEqual(
            edges,
            {
                ("C003", "related", "C002"),
            },
        )
        self.assertEqual(result.errors, ())

    def test_similar_relation_is_ignored(self) -> None:
        self.create_source(meta_record("C001", "一", "解析几何-甲"))
        self.create_source(meta_record("C002", "二", "解析几何-乙", similar=["C001"]))

        result = self.map()

        self.assertEqual(result.errors, ())
        self.assertFalse(any(item.type == "similar" for item in result.relations))

    def test_missing_relation_target_is_mapping_error(self) -> None:
        self.create_source(
            meta_record("C001", "一", "解析几何-甲", related_ids=["C999"])
        )

        result = self.map()

        self.assertTrue(any("target does not exist: C999" in issue.message for issue in result.errors))
        self.assertEqual(result.relation_count("related"), 0)

    def test_assets_have_stable_ids_natural_order_and_logical_urls(self) -> None:
        source = self.create_source(meta_record("C006", "离心率", "解析几何-椭圆"))
        for name in ("10.png", "2.png", "1.png"):
            (source / "images" / name).write_bytes(name.encode("ascii"))
        (source / "pdfs" / "01.pdf").write_bytes(b"pdf")

        result = self.map()
        images = [asset for asset in result.assets if asset.type == "image"]
        pdf = next(asset for asset in result.assets if asset.type == "pdf")

        self.assertEqual([asset.id for asset in images], [
            "C006:image:1.png",
            "C006:image:2.png",
            "C006:image:10.png",
        ])
        self.assertEqual([asset.sortOrder for asset in images], [10, 20, 30])
        self.assertEqual(images[0].uri, "resources/images/C006/1.png")
        self.assertEqual(pdf.uri, "resources/pdfs/C006/01.pdf")

    def test_search_document_maps_all_declared_fields(self) -> None:
        self.create_source(meta_record("C006", "离心率", "解析几何-椭圆"))

        result = self.map()
        document = result.search_documents[0]

        self.assertEqual(document.knowledgeNodeId, "C006")
        self.assertEqual(document.title, "离心率")
        self.assertEqual(document.aliases, ("离心率别名",))
        self.assertEqual(document.formula_tokens, ("x",))
        self.assertEqual(document.title_weight, 10)
        self.assertEqual(document.search_boost, 0.5)

    def test_legacy_search_shapes_are_mapped_without_source_mutation(self) -> None:
        record = meta_record("C006", "离心率", "解析几何-椭圆")
        record["relations"]["related_ids"] = ""
        record["search"]["latex_patterns"] = "x^2"
        record["search"]["pinyin"] = ["li xin lv", "tuo yuan"]
        record["search"]["pinyinAbbr"] = ["lxl", "ty"]
        source = self.create_source(record)
        before = (source / "meta.json").read_bytes()

        result = self.map()
        document = result.search_documents[0]

        self.assertEqual(result.errors, ())
        self.assertEqual(document.latex_patterns, ("x^2",))
        self.assertEqual(document.pinyin, "li xin lv tuo yuan")
        self.assertEqual(document.pinyin_abbr, "lxl ty")
        self.assertEqual((source / "meta.json").read_bytes(), before)

    def test_repeated_mapping_is_identical(self) -> None:
        source = self.create_source(meta_record("C006", "离心率", "解析几何-椭圆"))
        (source / "images" / "2.png").write_bytes(b"two")
        (source / "images" / "1.png").write_bytes(b"one")
        scan_result = scan_repository(self.project_root)

        first = map_runtime(scan_result)
        second = map_runtime(scan_result)

        self.assertEqual(first, second)

    def test_conclusion_and_search_counts_match_discovery(self) -> None:
        self.create_source(meta_record("C001", "一", "解析几何-甲"))
        self.create_source(meta_record("C002", "二", "解析几何-乙"))
        scan_result = scan_repository(self.project_root)

        result = map_runtime(scan_result)

        self.assertEqual(result.source_conclusion_count, 2)
        self.assertEqual(result.conclusion_node_count, 2)
        self.assertEqual(len(result.search_documents), 2)
        self.assertEqual(result.errors, ())


if __name__ == "__main__":
    unittest.main()
