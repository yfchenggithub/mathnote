from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.zhishu.runtime_mapping import (
    _canonical_related_pair,
    map_runtime,
    structural_node_id,
)
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
        self.prepared_assets = self.project_root / "build/zhishu-runtime-assets"
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

    def map(self, scan_result=None):
        shutil.rmtree(self.prepared_assets, ignore_errors=True)
        for source_image in self.project_root.rglob("images/*"):
            if not source_image.is_file() or source_image.suffix.lower() not in {".png", ".gif"}:
                continue
            source_id = json.loads(
                (source_image.parent.parent / "meta.json").read_text(encoding="utf-8")
            )["id"]
            output_suffix = ".webp" if source_image.suffix.lower() == ".png" else ".gif"
            output = self.prepared_assets / "images" / source_id / f"{source_image.stem}{output_suffix}"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(source_image.read_bytes())
        return map_runtime(
            scan_result or scan_repository(self.project_root), self.prepared_assets
        )

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

    def test_single_related_metadata_is_canonical(self) -> None:
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
                ("C002", "related", "C003"),
            },
        )
        self.assertEqual(result.relations[0].id, "C002:related:C003")
        self.assertEqual(result.errors, ())

    def test_reverse_single_related_metadata_has_same_canonical_identity(self) -> None:
        first = self.create_source(
            meta_record("C001", "一", "解析几何-甲", related_ids=["C002"])
        )
        second = self.create_source(meta_record("C002", "二", "解析几何-乙"))
        forward = self.map().relations

        first.joinpath("meta.json").write_text(
            json.dumps(
                meta_record("C001", "一", "解析几何-甲"), ensure_ascii=False
            ),
            encoding="utf-8",
        )
        second.joinpath("meta.json").write_text(
            json.dumps(
                meta_record(
                    "C002", "二", "解析几何-乙", related_ids=["C001"]
                ),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        reverse = self.map().relations

        self.assertEqual(forward, reverse)
        self.assertEqual(forward[0].id, "C001:related:C002")

    def test_related_metadata_duplicates_collapse_to_one_relation(self) -> None:
        self.create_source(
            meta_record(
                "C001", "一", "解析几何-甲", related_ids=["C002", "C002"]
            )
        )
        self.create_source(
            meta_record(
                "C002", "二", "解析几何-乙", related_ids=["C001", "C001"]
            )
        )

        result = self.map()

        self.assertEqual(result.errors, ())
        self.assertEqual(len(result.relations), 1)
        self.assertEqual(result.relations[0].id, "C001:related:C002")

    def test_distinct_related_pairs_are_not_merged(self) -> None:
        self.create_source(
            meta_record(
                "C001", "一", "解析几何-甲", related_ids=["C002", "C003"]
            )
        )
        self.create_source(
            meta_record("C002", "二", "解析几何-乙", related_ids=["C003"])
        )
        self.create_source(meta_record("C003", "三", "解析几何-丙"))

        result = self.map()

        self.assertEqual(result.errors, ())
        self.assertEqual(
            [relation.id for relation in result.relations],
            [
                "C001:related:C002",
                "C001:related:C003",
                "C002:related:C003",
            ],
        )

    def test_related_self_relation_is_rejected(self) -> None:
        self.create_source(
            meta_record("C001", "一", "解析几何-甲", related_ids=["C001"])
        )

        result = self.map()

        self.assertTrue(
            any("self relation is not allowed" in issue.message for issue in result.errors)
        )

    def test_directed_relation_endpoints_are_not_canonicalized(self) -> None:
        self.assertEqual(_canonical_related_pair("C002", "C001"), ("C001", "C002"))
        self.create_source(meta_record("C001", "一", "解析几何-甲"))
        self.create_source(
            meta_record(
                "C002", "二", "解析几何-乙", prerequisites=["C001"]
            )
        )

        with mock.patch(
            "scripts.zhishu.runtime_mapping.RELATION_FIELDS",
            (("prerequisites", "prerequisite"),),
        ):
            result = self.map()

        self.assertEqual(result.errors, ())
        self.assertEqual(
            (result.relations[0].sourceId, result.relations[0].targetId),
            ("C002", "C001"),
        )

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
            "C006:image:1.webp",
            "C006:image:2.webp",
            "C006:image:10.webp",
        ])
        self.assertEqual([asset.sortOrder for asset in images], [10, 20, 30])
        self.assertEqual(images[0].uri, "resources/images/C006/1.webp")
        self.assertEqual(pdf.uri, "resources/pdfs/C006/01.pdf")

    def test_webp_and_gif_with_the_same_basename_remain_distinct_assets(self) -> None:
        source = self.create_source(meta_record("C007", "混合图片", "解析几何-椭圆"))
        (source / "images" / "001.png").write_bytes(b"static")
        (source / "images" / "001.gif").write_bytes(b"animated")

        result = self.map()
        images = [asset for asset in result.assets if asset.type == "image"]

        self.assertEqual(result.errors, ())
        self.assertEqual(
            {asset.id for asset in images},
            {"C007:image:001.webp", "C007:image:001.gif"},
        )
        self.assertEqual(
            {asset.uri for asset in images},
            {"resources/images/C007/001.webp", "resources/images/C007/001.gif"},
        )

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

        first = self.map(scan_result)
        second = self.map(scan_result)

        self.assertEqual(first, second)

    def test_conclusion_and_search_counts_match_discovery(self) -> None:
        self.create_source(meta_record("C001", "一", "解析几何-甲"))
        self.create_source(meta_record("C002", "二", "解析几何-乙"))
        scan_result = scan_repository(self.project_root)

        result = self.map(scan_result)

        self.assertEqual(result.source_conclusion_count, 2)
        self.assertEqual(result.conclusion_node_count, 2)
        self.assertEqual(len(result.search_documents), 2)
        self.assertEqual(result.errors, ())


if __name__ == "__main__":
    unittest.main()
