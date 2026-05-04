from __future__ import annotations

import json
import shutil
import unittest
from collections import defaultdict
from pathlib import Path

from scripts import build_search_bundle_js as builder


def _postings(*doc_ids: str) -> dict[str, builder.PostingAccumulator]:
    return {
        doc_id: builder.PostingAccumulator(score=10, field_mask=1) for doc_id in doc_ids
    }


class PrefixGovernanceUnitTests(unittest.TestCase):
    def test_semantic_prefix_keeps_meaningful_boundaries(self) -> None:
        prefixes = builder.prefix_terms(
            "柯西不等式推广",
            cjk_prefix_mode="semantic",
            cjk_prefix_min_len=2,
        )
        self.assertEqual(prefixes, ["柯西", "柯西不等式", "柯西不等式推广"])
        self.assertNotIn("柯西不等", prefixes)
        self.assertNotIn("柯西不等式推", prefixes)

    def test_unclosed_structure_is_filtered(self) -> None:
        self.assertFalse(builder.is_structurally_complete_text("柯西不等式特例(分"))
        self.assertTrue(builder.is_structurally_complete_text("柯西不等式特例(分式)"))
        prefixes = builder.prefix_terms(
            "柯西不等式特例(分",
            cjk_prefix_mode="semantic",
            cjk_prefix_min_len=2,
        )
        self.assertIn("柯西不等式特例", prefixes)
        self.assertNotIn("柯西不等式特例(分", prefixes)

    def test_prune_prefix_index_drops_truncated_candidates(self) -> None:
        prefix_index: defaultdict[str, dict[str, builder.PostingAccumulator]] = defaultdict(dict)
        prefix_index["柯西"] = _postings("I002")
        prefix_index["柯西不等"] = _postings("I001")
        prefix_index["柯西不等式"] = _postings("I001")
        prefix_index["柯西不等式推"] = _postings("I001")
        prefix_index["柯西不等式推广"] = _postings("I001")
        prefix_index["柯西不等式特例(分"] = _postings("I001")
        prefix_index["am-gm"] = _postings("I003")
        prefix_index["am-gm不等式"] = _postings("I003")
        prefix_index["c-s"] = _postings("I004")
        prefix_index["c-s方法"] = _postings("I004")
        prefix_index["kx"] = _postings("I002")
        prefix_index["kexi"] = _postings("I002")

        term_index = {
            "柯西": _postings("I002"),
            "柯西不等式": _postings("I001"),
            "柯西不等式推广": _postings("I001"),
            "am-gm": _postings("I003"),
            "c-s": _postings("I004"),
            "kx": _postings("I002"),
            "kexi": _postings("I002"),
        }
        governance = builder.PrefixGovernanceStats()
        whitelist = {"柯西", "am-gm", "c-s"}

        builder.prune_prefix_index(
            prefix_index,
            term_index,
            whitelist,
            governance,
            cjk_prefix_min_len=2,
        )

        self.assertIn("柯西", prefix_index)
        self.assertIn("柯西不等式", prefix_index)
        self.assertIn("柯西不等式推广", prefix_index)
        self.assertNotIn("柯西不等", prefix_index)
        self.assertNotIn("柯西不等式推", prefix_index)
        self.assertNotIn("柯西不等式特例(分", prefix_index)
        self.assertIn("am-gm", prefix_index)
        self.assertIn("c-s", prefix_index)
        self.assertIn("kx", prefix_index)
        self.assertIn("kexi", prefix_index)
        self.assertGreater(
            governance.dropped.get("prefix_stop_tail", 0)
            + governance.dropped.get("prefix_same_docset_strict_prefix", 0),
            0,
        )

    def test_prune_suggestions_drops_bad_candidates(self) -> None:
        suggestions = {
            "s1": {"display": "柯西", "docId": "I002", "score": 100},
            "s2": {"display": "柯西不等", "docId": "I001", "score": 90},
            "s3": {"display": "柯西不等式", "docId": "I001", "score": 92},
            "s4": {"display": "柯西不等式推", "docId": "I001", "score": 89},
            "s5": {"display": "柯西不等式推广", "docId": "I001", "score": 110},
            "s6": {"display": "柯西不等式特例(分", "docId": "I001", "score": 70},
            "s7": {"display": "AM-GM", "docId": "I003", "score": 50},
            "s8": {"display": "C-S", "docId": "I004", "score": 51},
        }
        term_index = {
            "柯西": _postings("I002"),
            "柯西不等式": _postings("I001"),
            "柯西不等式推广": _postings("I001"),
            "am-gm": _postings("I003"),
            "c-s": _postings("I004"),
        }
        governance = builder.PrefixGovernanceStats()
        whitelist = {"柯西", "am-gm", "c-s"}

        kept = builder.prune_suggestions(
            suggestions,
            term_index,
            whitelist,
            governance,
        )
        displays = {row["display"] for row in kept.values()}

        self.assertIn("柯西", displays)
        self.assertIn("柯西不等式", displays)
        self.assertIn("柯西不等式推广", displays)
        self.assertNotIn("柯西不等", displays)
        self.assertNotIn("柯西不等式推", displays)
        self.assertNotIn("柯西不等式特例(分", displays)
        self.assertIn("AM-GM", displays)
        self.assertIn("C-S", displays)
        self.assertGreaterEqual(governance.dropped.get("suggest_unclosed_structure", 0), 1)


class BundleRegressionTests(unittest.TestCase):
    def _write_meta(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _make_config(self, root: Path, cjk_prefix_mode: str) -> builder.BuildConfig:
        return builder.BuildConfig(
            project_root=root,
            output_file=root / "data" / "search_engine" / "search_bundle.js",
            audit_report_file=None,
            target_modules=("07_inequality",),
            target_items=(),
            dry_run=True,
            debug=False,
            strict=True,
            pretty=False,
            embed_debug=False,
            enable_cjk_ngrams=False,
            enable_statement_fragments=False,
            enable_summary_terms=False,
            enable_usage_terms=False,
            enable_ocr_terms=False,
            enable_knowledge_node_terms=False,
            enable_formula_token_terms=False,
            enable_formula_terms=False,
            enable_query_template_terms=False,
            pinyin_prefix_mode="syllable",
            cjk_prefix_mode=cjk_prefix_mode,
            cjk_prefix_min_len=2,
            prefix_whitelist_file=None,
            prefix_whitelist_terms=(),
            prefix_governance_debug=False,
            prefix_doc_limit=32,
            suggestion_limit=500,
            debug_docs=(),
            debug_terms=(),
        )

    def test_term_index_recall_stays_stable(self) -> None:
        root = builder.PROJECT_ROOT / "tests" / ".tmp" / "prefix_governance_fixture"
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            self._write_meta(
                root / "07_inequality" / "I001" / "meta.json",
                {
                    "id": "I001",
                    "module": "07_inequality",
                    "core": {"title": "柯西不等式推广"},
                    "alias": ["柯西不等式", "柯西不等式特例(分", "柯西不等式特例(分式)"],
                    "search": {
                        "suggestTerms": [
                            "柯西不等式推广",
                            "柯西不等式推",
                            "柯西不等式特例(分",
                        ]
                    },
                },
            )
            self._write_meta(
                root / "07_inequality" / "I002" / "meta.json",
                {
                    "id": "I002",
                    "module": "07_inequality",
                    "core": {"title": "柯西"},
                },
            )
            self._write_meta(
                root / "07_inequality" / "I003" / "meta.json",
                {
                    "id": "I003",
                    "module": "07_inequality",
                    "core": {"title": "AM-GM"},
                },
            )
            self._write_meta(
                root / "07_inequality" / "I004" / "meta.json",
                {
                    "id": "I004",
                    "module": "07_inequality",
                    "core": {"title": "C-S"},
                },
            )

            bundle_char = builder.run_build(self._make_config(root, "char"))
            bundle_semantic = builder.run_build(self._make_config(root, "semantic"))

            self.assertEqual(bundle_char["termIndex"], bundle_semantic["termIndex"])

            semantic_prefix_keys = set(bundle_semantic["prefixIndex"].keys())
            self.assertIn("柯西", semantic_prefix_keys)
            self.assertIn("柯西不等式", semantic_prefix_keys)
            self.assertIn("柯西不等式推广", semantic_prefix_keys)
            self.assertIn("kx", semantic_prefix_keys)
            self.assertNotIn("柯西不等", semantic_prefix_keys)
            self.assertNotIn("柯西不等式推", semantic_prefix_keys)
            self.assertNotIn("柯西不等式特例(分", semantic_prefix_keys)

            semantic_suggest_displays = {
                row[0] for row in bundle_semantic["suggestions"]  # type: ignore[index]
            }
            self.assertIn("柯西不等式推广", semantic_suggest_displays)
            self.assertIn("柯西", semantic_suggest_displays)
            self.assertIn("AM-GM", semantic_suggest_displays)
            self.assertIn("C-S", semantic_suggest_displays)
            self.assertNotIn("柯西不等式推", semantic_suggest_displays)
            self.assertNotIn("柯西不等式特例(分", semantic_suggest_displays)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
