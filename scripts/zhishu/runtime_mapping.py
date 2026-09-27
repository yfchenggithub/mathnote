"""Deterministic mapping from discovered sources to Zhishu runtime DTOs."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

if __package__:
    from .asset_preparation import DEFAULT_OUTPUT as DEFAULT_RUNTIME_ASSET_OUTPUT
    from .source_discovery import ConclusionSource, ScanResult
else:
    from asset_preparation import DEFAULT_OUTPUT as DEFAULT_RUNTIME_ASSET_OUTPUT
    from source_discovery import ConclusionSource, ScanResult


STRUCTURAL_PREFIX = "struct:"
ROOT_NODE_ID = "root-high-school-math"
NODE_TYPES = frozenset(("root", "chapter", "section", "knowledge"))
RELATION_TYPES = frozenset(("prerequisite", "related", "next"))
ASSET_TYPES = frozenset(("image", "pdf"))
RELATION_FIELDS = (
    ("related_ids", "related"),
)


@dataclass(frozen=True)
class KnowledgeNode:
    id: str
    title: str
    parentId: str | None
    sortOrder: int
    type: str
    shortTitle: str | None = None


@dataclass(frozen=True)
class KnowledgeRelation:
    id: str
    sourceId: str
    targetId: str
    type: str
    sortOrder: int | None = None


@dataclass(frozen=True)
class KnowledgeAsset:
    id: str
    knowledgeId: str
    type: str
    uri: str
    sortOrder: int
    title: str | None = None


@dataclass(frozen=True)
class SearchDocument:
    knowledgeNodeId: str
    title: str
    aliases: tuple[str, ...]
    summary: str
    difficulty: int | float | None
    category: str
    tags: tuple[str, ...]
    keywords: tuple[str, ...]
    synonyms: tuple[str, ...]
    intents: tuple[str, ...]
    query_templates: tuple[str, ...]
    ocr_keywords: tuple[str, ...]
    latex_patterns: tuple[str, ...]
    formula_tokens: tuple[str, ...]
    pinyin: str
    pinyin_abbr: str
    title_weight: int | float | None
    keyword_weight: int | float | None
    synonym_weight: int | float | None
    formula_weight: int | float | None
    search_boost: int | float | None
    hot_score: int | float | None
    click_rate: int | float | None
    success_rate: int | float | None


@dataclass(frozen=True)
class MappingIssue:
    path: Path
    message: str


@dataclass(frozen=True)
class RuntimeMappingResult:
    source_conclusion_count: int
    knowledge_nodes: tuple[KnowledgeNode, ...]
    relations: tuple[KnowledgeRelation, ...]
    assets: tuple[KnowledgeAsset, ...]
    search_documents: tuple[SearchDocument, ...]
    errors: tuple[MappingIssue, ...]
    warnings: tuple[MappingIssue, ...]

    @property
    def structural_node_count(self) -> int:
        return sum(node.type != "knowledge" for node in self.knowledge_nodes)

    @property
    def conclusion_node_count(self) -> int:
        return sum(node.type == "knowledge" for node in self.knowledge_nodes)

    def relation_count(self, relation_type: str) -> int:
        return sum(relation.type == relation_type for relation in self.relations)

    def asset_count(self, asset_type: str) -> int:
        return sum(asset.type == asset_type for asset in self.assets)


@dataclass(frozen=True)
class _MappedSource:
    source: ConclusionSource
    data: Mapping[str, Any]
    id: str
    title: str
    primary_path: str


def structural_node_id(full_path: str) -> str:
    return f"{STRUCTURAL_PREFIX}{full_path}"


def _canonical_related_pair(source_id: str, target_id: str) -> tuple[str, str]:
    """Return the stable endpoint order for one symmetric related relation."""

    return min(source_id, target_id), max(source_id, target_id)


def _source_path(source: ConclusionSource, suffix: str = "meta.json") -> Path:
    return Path(source.module_name) / source.conclusion_dir_name / suffix


def _natural_key(value: str) -> tuple[tuple[int, int | str], ...]:
    parts: list[tuple[int, int | str]] = []
    for part in re.split(r"(\d+)", value.casefold()):
        if part.isdigit():
            parts.append((0, int(part)))
        else:
            parts.append((1, part))
    return tuple(parts)


def _string_tuple(
    value: Any,
    field_name: str,
    source: ConclusionSource,
    errors: list[MappingIssue],
    *,
    allow_scalar: bool = False,
) -> tuple[str, ...]:
    if isinstance(value, str) and not value.strip():
        return ()
    if allow_scalar and isinstance(value, str):
        return (value,)
    if not isinstance(value, list):
        errors.append(
            MappingIssue(_source_path(source), f"{field_name} must be an array of strings")
        )
        return ()
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(
            MappingIssue(
                _source_path(source),
                f"{field_name} contains a non-string or empty value",
            )
        )
        return tuple(item for item in value if isinstance(item, str) and item.strip())
    return tuple(value)


def _optional_string(value: Any, field_name: str, source: ConclusionSource, errors: list[MappingIssue]) -> str:
    if value is None:
        return ""
    if isinstance(value, list) and all(
        isinstance(item, str) and item.strip() for item in value
    ):
        return " ".join(value)
    if not isinstance(value, str):
        errors.append(MappingIssue(_source_path(source), f"{field_name} must be a string"))
        return ""
    return value


def _number(value: Any, field_name: str, source: ConclusionSource, errors: list[MappingIssue]) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(MappingIssue(_source_path(source), f"{field_name} must be a number"))
        return None
    return value


def _path_prefixes(full_path: str) -> tuple[str, ...]:
    components = full_path.split("-")
    return tuple("-".join(components[:index]) for index in range(1, len(components) + 1))


def _load_sources(scan_result: ScanResult, errors: list[MappingIssue]) -> tuple[_MappedSource, ...]:
    mapped: list[_MappedSource] = []
    seen_ids: set[str] = set()
    for module in scan_result.modules:
        for source in module.sources:
            try:
                data = json.loads(source.meta_json_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(MappingIssue(_source_path(source), f"could not load meta.json: {exc}"))
                continue
            if not isinstance(data, dict):
                errors.append(MappingIssue(_source_path(source), "meta.json root must be an object"))
                continue

            source_id = data.get("id")
            core = data.get("core")
            primary_path = data.get("knowledgeNode")
            if not isinstance(source_id, str) or not source_id.strip():
                errors.append(MappingIssue(_source_path(source), "id must be a non-empty string"))
                continue
            if source_id in seen_ids:
                errors.append(MappingIssue(_source_path(source), f"duplicate conclusion id: {source_id}"))
                continue
            if not isinstance(core, dict):
                errors.append(MappingIssue(_source_path(source), "core must be an object"))
                continue
            title = core.get("title")
            if not isinstance(title, str) or not title.strip():
                errors.append(MappingIssue(_source_path(source), "core.title must be a non-empty string"))
                continue
            if not isinstance(primary_path, str) or not primary_path.strip():
                errors.append(MappingIssue(_source_path(source), "knowledgeNode must be a non-empty string"))
                continue
            if any(not component.strip() for component in primary_path.split("-")):
                errors.append(MappingIssue(_source_path(source), "knowledgeNode contains an empty path component"))
                continue

            seen_ids.add(source_id)
            mapped.append(
                _MappedSource(
                    source=source,
                    data=data,
                    id=source_id,
                    title=title,
                    primary_path=primary_path,
                )
            )
    return tuple(mapped)


def _build_nodes(mapped_sources: tuple[_MappedSource, ...]) -> tuple[KnowledgeNode, ...]:
    structural_paths: set[str] = set()
    for mapped in mapped_sources:
        structural_paths.update(_path_prefixes(mapped.primary_path))

    specifications: list[tuple[str, str, str | None, str]] = [
        (ROOT_NODE_ID, "高中数学", None, "root")
    ]
    for full_path in structural_paths:
        prefixes = _path_prefixes(full_path)
        parent_id = structural_node_id(prefixes[-2]) if len(prefixes) > 1 else ROOT_NODE_ID
        node_type = "chapter" if len(prefixes) == 1 else "section"
        specifications.append(
            (structural_node_id(full_path), full_path.split("-")[-1], parent_id, node_type)
        )
    for mapped in mapped_sources:
        specifications.append(
            (mapped.id, mapped.title, structural_node_id(mapped.primary_path), "knowledge")
        )

    grouped: dict[str | None, list[tuple[str, str, str | None, str]]] = defaultdict(list)
    for specification in specifications:
        grouped[specification[2]].append(specification)
    sort_orders: dict[str, int] = {}
    for siblings in grouped.values():
        siblings.sort(key=lambda item: (item[3] == "knowledge", item[1].casefold(), item[0]))
        sort_orders.update({item[0]: (index + 1) * 10 for index, item in enumerate(siblings)})
    sort_orders[ROOT_NODE_ID] = 0

    structural_specifications = sorted(
        (item for item in specifications if item[3] != "knowledge"),
        key=lambda item: (item[0].count("-"), item[0]),
    )
    conclusion_specifications = sorted(
        (item for item in specifications if item[3] == "knowledge"),
        key=lambda item: item[0],
    )
    return tuple(
        KnowledgeNode(
            id=node_id,
            title=name,
            parentId=parent_id,
            sortOrder=sort_orders[node_id],
            type=node_type,
        )
        for node_id, name, parent_id, node_type in (
            *structural_specifications,
            *conclusion_specifications,
        )
    )


def _build_relations(
    mapped_sources: tuple[_MappedSource, ...],
    conclusion_ids: frozenset[str],
    errors: list[MappingIssue],
) -> tuple[KnowledgeRelation, ...]:
    relations: dict[str, KnowledgeRelation] = {}
    for mapped in mapped_sources:
        raw_relations = mapped.data.get("relations", {})
        if not isinstance(raw_relations, dict):
            errors.append(MappingIssue(_source_path(mapped.source), "relations must be an object"))
            raw_relations = {}
        for field_name, relation_type in RELATION_FIELDS:
            targets = _string_tuple(
                raw_relations.get(field_name, []),
                f"relations.{field_name}",
                mapped.source,
                errors,
            )
            for target_id in sorted(set(targets)):
                if target_id not in conclusion_ids:
                    errors.append(
                        MappingIssue(
                            _source_path(mapped.source),
                            f"relations.{field_name} target does not exist: {target_id}",
                        )
                    )
                    continue
                source_id, resolved_target_id = mapped.id, target_id
                if relation_type == "related":
                    source_id, resolved_target_id = _canonical_related_pair(
                        source_id, resolved_target_id
                    )
                relation_id = f"{source_id}:{relation_type}:{resolved_target_id}"
                relations[relation_id] = KnowledgeRelation(
                    relation_id, source_id, resolved_target_id, relation_type
                )

    return tuple(
        sorted(relations.values(), key=lambda item: (item.sourceId, item.type, item.targetId))
    )


def _build_assets(
    mapped_sources: tuple[_MappedSource, ...],
    warnings: list[MappingIssue],
    prepared_assets_root: Path,
) -> tuple[KnowledgeAsset, ...]:
    assets: list[KnowledgeAsset] = []
    for mapped in sorted(mapped_sources, key=lambda item: item.id):
        for directory_name, asset_type in (("images", "image"), ("pdfs", "pdf")):
            directory = (
                prepared_assets_root / "images" / mapped.id
                if asset_type == "image"
                else mapped.source.conclusion_path / "pdfs"
            )
            if not directory.is_dir():
                warnings.append(
                    MappingIssue(
                        (
                            Path("build/zhishu-runtime-assets/images") / mapped.id
                            if asset_type == "image"
                            else _source_path(mapped.source, directory_name)
                        ),
                        f"prepared {directory_name} directory is missing; no assets mapped"
                        if asset_type == "image"
                        else f"{directory_name} directory is missing; no assets mapped",
                    )
                )
                continue
            files = sorted(
                (path for path in directory.iterdir() if path.is_file()),
                key=lambda path: (_natural_key(path.name), path.name),
            )
            for sort_order, path in enumerate(files):
                asset_id = f"{mapped.id}:{asset_type}:{path.name}"
                uri = PurePosixPath("resources", directory_name, mapped.id, path.name).as_posix()
                assets.append(
                    KnowledgeAsset(asset_id, mapped.id, asset_type, uri, (sort_order + 1) * 10)
                )
    return tuple(assets)


def _build_search_documents(
    mapped_sources: tuple[_MappedSource, ...], errors: list[MappingIssue]
) -> tuple[SearchDocument, ...]:
    documents: list[SearchDocument] = []
    for mapped in sorted(mapped_sources, key=lambda item: item.id):
        core = mapped.data.get("core", {})
        search = mapped.data.get("search", {})
        searchmeta = mapped.data.get("searchmeta", {})
        ranking = mapped.data.get("ranking", {})
        for field_name, value in (
            ("search", search),
            ("searchmeta", searchmeta),
            ("ranking", ranking),
        ):
            if not isinstance(value, dict):
                errors.append(MappingIssue(_source_path(mapped.source), f"{field_name} must be an object"))
        search = search if isinstance(search, dict) else {}
        searchmeta = searchmeta if isinstance(searchmeta, dict) else {}
        ranking = ranking if isinstance(ranking, dict) else {}
        documents.append(
            SearchDocument(
                knowledgeNodeId=mapped.id,
                title=mapped.title,
                aliases=_string_tuple(core.get("alias", []), "core.alias", mapped.source, errors, allow_scalar=True),
                summary=_optional_string(core.get("summary"), "core.summary", mapped.source, errors),
                difficulty=_number(core.get("difficulty"), "core.difficulty", mapped.source, errors),
                category=_optional_string(core.get("category"), "core.category", mapped.source, errors),
                tags=_string_tuple(core.get("tags", []), "core.tags", mapped.source, errors, allow_scalar=True),
                keywords=_string_tuple(search.get("keywords", []), "search.keywords", mapped.source, errors, allow_scalar=True),
                synonyms=_string_tuple(search.get("synonyms", []), "search.synonyms", mapped.source, errors, allow_scalar=True),
                intents=_string_tuple(search.get("intents", []), "search.intents", mapped.source, errors, allow_scalar=True),
                query_templates=_string_tuple(search.get("query_templates", []), "search.query_templates", mapped.source, errors, allow_scalar=True),
                ocr_keywords=_string_tuple(search.get("ocrKeywords", []), "search.ocrKeywords", mapped.source, errors, allow_scalar=True),
                latex_patterns=_string_tuple(search.get("latex_patterns", []), "search.latex_patterns", mapped.source, errors, allow_scalar=True),
                formula_tokens=_string_tuple(search.get("formulaTokens", []), "search.formulaTokens", mapped.source, errors, allow_scalar=True),
                pinyin=_optional_string(search.get("pinyin"), "search.pinyin", mapped.source, errors),
                pinyin_abbr=_optional_string(search.get("pinyinAbbr"), "search.pinyinAbbr", mapped.source, errors),
                title_weight=_number(searchmeta.get("titleWeight"), "searchmeta.titleWeight", mapped.source, errors),
                keyword_weight=_number(searchmeta.get("keywordWeight"), "searchmeta.keywordWeight", mapped.source, errors),
                synonym_weight=_number(searchmeta.get("synonymWeight"), "searchmeta.synonymWeight", mapped.source, errors),
                formula_weight=_number(searchmeta.get("formulaWeight"), "searchmeta.formulaWeight", mapped.source, errors),
                search_boost=_number(ranking.get("search_boost"), "ranking.search_boost", mapped.source, errors),
                hot_score=_number(ranking.get("hot_score"), "ranking.hot_score", mapped.source, errors),
                click_rate=_number(ranking.get("click_rate"), "ranking.click_rate", mapped.source, errors),
                success_rate=_number(ranking.get("success_rate"), "ranking.success_rate", mapped.source, errors),
            )
        )
    return tuple(documents)


def _duplicate_values(values: Iterable[str]) -> frozenset[str]:
    return frozenset(value for value, count in Counter(values).items() if count > 1)


def _validate_runtime(
    scan_result: ScanResult,
    nodes: tuple[KnowledgeNode, ...],
    relations: tuple[KnowledgeRelation, ...],
    assets: tuple[KnowledgeAsset, ...],
    documents: tuple[SearchDocument, ...],
    errors: list[MappingIssue],
) -> None:
    node_ids = frozenset(node.id for node in nodes)
    for duplicate in sorted(_duplicate_values(node.id for node in nodes)):
        errors.append(MappingIssue(Path("runtime/knowledge-nodes"), f"duplicate node id: {duplicate}"))
    for node in nodes:
        if node.type not in NODE_TYPES:
            errors.append(MappingIssue(Path("runtime/knowledge-nodes"), f"invalid node type: {node.type}"))
        if node.type == "root" and node.parentId is not None:
            errors.append(MappingIssue(Path("runtime/knowledge-nodes"), f"root node has non-null parentId: {node.id}"))
        if node.type != "root" and (node.parentId is None or node.parentId not in node_ids):
            errors.append(MappingIssue(Path("runtime/knowledge-nodes"), f"parentId does not exist: {node.parentId}"))
    root_count = sum(node.type == "root" for node in nodes)
    if root_count != 1:
        errors.append(MappingIssue(Path("runtime/knowledge-nodes"), f"expected exactly one root node, found {root_count}"))
    conclusion_count = sum(node.type == "knowledge" for node in nodes)
    if conclusion_count != scan_result.conclusion_count:
        errors.append(
            MappingIssue(
                Path("runtime/knowledge-nodes"),
                f"conclusion node count {conclusion_count} does not match discovered count {scan_result.conclusion_count}",
            )
        )

    for duplicate in sorted(_duplicate_values(relation.id for relation in relations)):
        errors.append(MappingIssue(Path("runtime/knowledge-relations"), f"duplicate relation id: {duplicate}"))
    for relation in relations:
        if relation.type not in RELATION_TYPES:
            errors.append(MappingIssue(Path("runtime/knowledge-relations"), f"invalid relation type: {relation.type}"))
        if relation.sourceId not in node_ids or relation.targetId not in node_ids:
            errors.append(MappingIssue(Path("runtime/knowledge-relations"), f"relation endpoint does not exist: {relation.id}"))
        if relation.sourceId == relation.targetId:
            errors.append(MappingIssue(Path("runtime/knowledge-relations"), f"self relation is not allowed: {relation.id}"))

    for duplicate in sorted(_duplicate_values(asset.id for asset in assets)):
        errors.append(MappingIssue(Path("runtime/knowledge-assets"), f"duplicate asset id: {duplicate}"))
    for asset in assets:
        if asset.type not in ASSET_TYPES:
            errors.append(MappingIssue(Path("runtime/knowledge-assets"), f"invalid asset type: {asset.type}"))
        if asset.knowledgeId not in node_ids:
            errors.append(MappingIssue(Path("runtime/knowledge-assets"), f"asset knowledge id does not exist: {asset.id}"))
        if "\\" in asset.uri or Path(asset.uri).is_absolute():
            errors.append(MappingIssue(Path("runtime/knowledge-assets"), f"asset URI is not a logical path: {asset.uri}"))

    for duplicate in sorted(_duplicate_values(document.knowledgeNodeId for document in documents)):
        errors.append(MappingIssue(Path("runtime/search-documents"), f"duplicate search document: {duplicate}"))
    for document in documents:
        if document.knowledgeNodeId not in node_ids:
            errors.append(MappingIssue(Path("runtime/search-documents"), f"search knowledge id does not exist: {document.knowledgeNodeId}"))
    if len(documents) != scan_result.conclusion_count:
        errors.append(
            MappingIssue(
                Path("runtime/search-documents"),
                f"search document count {len(documents)} does not match discovered count {scan_result.conclusion_count}",
            )
        )


def map_runtime(
    scan_result: ScanResult,
    prepared_assets_root: Path = DEFAULT_RUNTIME_ASSET_OUTPUT,
) -> RuntimeMappingResult:
    """Map one immutable discovery result into deterministic runtime DTOs."""

    errors = [
        MappingIssue(error.path, f"discovery validation failed: {error.message}")
        for error in scan_result.errors
    ]
    warnings: list[MappingIssue] = []
    if errors:
        return RuntimeMappingResult(
            scan_result.conclusion_count, (), (), (), (), tuple(errors), ()
        )

    mapped_sources = _load_sources(scan_result, errors)
    nodes = _build_nodes(mapped_sources)
    conclusion_ids = frozenset(mapped.id for mapped in mapped_sources)
    relations = _build_relations(mapped_sources, conclusion_ids, errors)
    assets = _build_assets(mapped_sources, warnings, prepared_assets_root.resolve())
    documents = _build_search_documents(mapped_sources, errors)
    _validate_runtime(scan_result, nodes, relations, assets, documents, errors)
    return RuntimeMappingResult(
        source_conclusion_count=scan_result.conclusion_count,
        knowledge_nodes=nodes,
        relations=relations,
        assets=assets,
        search_documents=documents,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
