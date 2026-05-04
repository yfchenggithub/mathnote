from __future__ import annotations

import argparse
import json
import logging
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
META_FILENAME = "meta.json"
DEFAULT_OUTPUT = Path("data/search_engine/domain_topic_map.json")
DEFAULT_ALIASES_FILE = Path("data/search_engine/aliases_overrides.json")

IGNORED_TOP_LEVEL_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    ".tmp",
    "assets",
    "build",
    "data",
    "misc",
    "node_modules",
    "scripts",
    "search_engine",
    "templates",
    "reports",
}

ALT_NODE_SPLIT_RE = re.compile(r"[,，;；、/|]+")
WHITESPACE_RE = re.compile(r"\s+")
COURSE_TAG_RE = re.compile(r"[（(](?:选修|必修)[)）]\s*$")
DOC_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*\d+$")

LOGGER = logging.getLogger("build_domain_topic_map")


class BuildError(RuntimeError):
    """Raised when the build cannot continue safely."""


@dataclass(frozen=True)
class BuildConfig:
    base_dir: Path
    modules: tuple[str, ...]
    output: Path
    aliases_file: Path
    dry_run: bool
    strict: bool
    pretty: bool
    log_level: str


@dataclass
class TopicInfo:
    docs: set[str] = field(default_factory=set)
    aliases: set[str] = field(default_factory=set)


@dataclass
class DomainInfo:
    topics: dict[str, TopicInfo] = field(default_factory=dict)
    aliases: set[str] = field(default_factory=set)


@dataclass
class BuildStats:
    scanned_meta_files: int = 0
    indexed_docs: int = 0
    invalid_json_files: int = 0
    docs_without_id: int = 0
    docs_without_nodes: int = 0
    node_paths_seen: int = 0


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build domain_topic_map.json from meta.json knowledgeNode/altNodes."
    )
    parser.add_argument(
        "--base-dir",
        default=str(PROJECT_ROOT),
        help="Project root directory (default: script parent).",
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        help="Only scan the given top-level module(s). Can be repeated.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output file path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--aliases-file",
        default=str(DEFAULT_ALIASES_FILE),
        help=(
            "Optional aliases override JSON. Missing file is allowed "
            f"(default: {DEFAULT_ALIASES_FILE})."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and print stats without writing output file.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on invalid JSON and missing modules.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print output JSON.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging level.",
    )
    return parser.parse_args()


def resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def build_config(args: argparse.Namespace) -> BuildConfig:
    base_dir = Path(args.base_dir).resolve()
    return BuildConfig(
        base_dir=base_dir,
        modules=tuple(args.modules or ()),
        output=resolve_path(base_dir, str(args.output)),
        aliases_file=resolve_path(base_dir, str(args.aliases_file)),
        dry_run=bool(args.dry_run),
        strict=bool(args.strict),
        pretty=bool(args.pretty),
        log_level=str(args.log_level).upper(),
    )


def module_contains_content(module_dir: Path) -> bool:
    try:
        for child in module_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / META_FILENAME).exists() or (child / "01_statement.tex").exists():
                return True
    except OSError:
        return False
    return False


def discover_modules(base_dir: Path) -> list[str]:
    modules: list[str] = []
    for path in sorted(base_dir.iterdir()):
        if not path.is_dir():
            continue
        if path.name in IGNORED_TOP_LEVEL_DIRS:
            continue
        if module_contains_content(path):
            modules.append(path.name)
    return modules


def resolve_target_modules(config: BuildConfig) -> list[str]:
    if not config.modules:
        discovered = discover_modules(config.base_dir)
        if not discovered:
            raise BuildError("No buildable modules found.")
        return discovered

    resolved: list[str] = []
    missing: list[str] = []
    for module_name in config.modules:
        module_dir = config.base_dir / module_name
        if module_dir.is_dir():
            resolved.append(module_name)
        else:
            missing.append(module_name)
    if missing and config.strict:
        raise BuildError(f"Module(s) not found: {', '.join(missing)}")
    if missing:
        LOGGER.warning("Skip missing module(s): %s", ", ".join(missing))
    if not resolved:
        raise BuildError("No valid modules to scan.")
    return resolved


def iter_meta_files(base_dir: Path, modules: Sequence[str]) -> list[Path]:
    files: list[Path] = []
    for module_name in modules:
        module_dir = base_dir / module_name
        for item in sorted(module_dir.iterdir()):
            if not item.is_dir():
                continue
            meta_path = item / META_FILENAME
            if meta_path.exists():
                files.append(meta_path)
    return files


def read_json_file(path: Path, strict: bool) -> dict[str, object]:
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except Exception as exc:
        if strict:
            raise BuildError(f"Failed to read JSON: {path}") from exc
        LOGGER.warning("Invalid JSON skipped: %s", path)
        return {}
    if not isinstance(data, dict):
        if strict:
            raise BuildError(f"JSON root must be an object: {path}")
        LOGGER.warning("JSON root is not object, skipped: %s", path)
        return {}
    return data


def get_path(data: Mapping[str, object], path: str) -> object:
    current: object = data
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def flatten_strings(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple, set)):
        result: list[str] = []
        for item in value:
            result.extend(flatten_strings(item))
        return result
    return []


def dedupe_keep_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def normalize_display(text: str) -> str:
    return WHITESPACE_RE.sub(" ", unicodedata.normalize("NFKC", text)).strip()


def normalize_node_part(text: str) -> str:
    value = normalize_display(text)
    value = COURSE_TAG_RE.sub("", value).strip()
    return value


def normalize_alias(text: str) -> str:
    return normalize_display(text)


def split_alt_nodes(raw_alt: str) -> list[str]:
    return [part.strip() for part in ALT_NODE_SPLIT_RE.split(raw_alt) if part.strip()]


def parse_node_path(node_path: str) -> tuple[str, str] | None:
    parts = [normalize_node_part(part) for part in node_path.split("-")]
    cleaned = [part for part in parts if part]
    if not cleaned:
        return None
    return cleaned[0], cleaned[-1]


def extract_node_paths(meta: Mapping[str, object]) -> list[str]:
    paths: list[str] = []
    paths.extend(flatten_strings(get_path(meta, "knowledgeNode")))
    paths.extend(flatten_strings(get_path(meta, "core.knowledgeNode")))
    alt_values = []
    alt_values.extend(flatten_strings(get_path(meta, "altNodes")))
    alt_values.extend(flatten_strings(get_path(meta, "core.altNodes")))
    for raw_alt in alt_values:
        paths.extend(split_alt_nodes(raw_alt))
    return dedupe_keep_order(paths)


def first_string(meta: Mapping[str, object], *keys: str) -> str:
    for key in keys:
        value = get_path(meta, key)
        items = flatten_strings(value)
        if items:
            return normalize_display(items[0])
    return ""


def add_mapping(
    domains: dict[str, DomainInfo], domain_name: str, topic_name: str, doc_id: str
) -> None:
    domain = domains.setdefault(domain_name, DomainInfo())
    topic = domain.topics.setdefault(topic_name, TopicInfo())
    topic.docs.add(doc_id)


def load_alias_overrides(path: Path, strict: bool) -> dict[str, object]:
    if not path.exists():
        LOGGER.info("Aliases file not found, skip: %s", path)
        return {}
    data = read_json_file(path, strict=strict)
    if not isinstance(data, dict):
        if strict:
            raise BuildError(f"Aliases file must be JSON object: {path}")
        LOGGER.warning("Aliases file is not object, ignored: %s", path)
        return {}
    return data


def iter_topics(domains: dict[str, DomainInfo]) -> list[tuple[str, str, TopicInfo]]:
    result: list[tuple[str, str, TopicInfo]] = []
    for domain_name, domain_info in domains.items():
        for topic_name, topic_info in domain_info.topics.items():
            result.append((domain_name, topic_name, topic_info))
    return result


def apply_aliases_overrides(
    domains: dict[str, DomainInfo], overrides: Mapping[str, object]
) -> None:
    domain_aliases_raw = overrides.get("domain_aliases")
    if isinstance(domain_aliases_raw, Mapping):
        for domain_name, alias_value in domain_aliases_raw.items():
            if not isinstance(domain_name, str):
                continue
            target = domains.get(normalize_node_part(domain_name))
            if target is None:
                continue
            for alias in flatten_strings(alias_value):
                normalized = normalize_alias(alias)
                if normalized and normalized != normalize_node_part(domain_name):
                    target.aliases.add(normalized)

    topic_aliases_raw = overrides.get("topic_aliases")
    if not isinstance(topic_aliases_raw, Mapping):
        return

    all_topics = iter_topics(domains)
    for key, alias_value in topic_aliases_raw.items():
        if not isinstance(key, str):
            continue
        aliases = [normalize_alias(a) for a in flatten_strings(alias_value)]
        aliases = [a for a in aliases if a]
        if not aliases:
            continue

        key_normalized = normalize_display(key)
        target_topics: list[TopicInfo] = []

        if "::" in key_normalized:
            domain_key, topic_key = key_normalized.split("::", 1)
            domain_key = normalize_node_part(domain_key)
            topic_key = normalize_node_part(topic_key)
            domain = domains.get(domain_key)
            if domain is not None:
                topic = domain.topics.get(topic_key)
                if topic is not None:
                    target_topics.append(topic)
        elif DOC_ID_RE.fullmatch(key_normalized):
            for _, _, topic_info in all_topics:
                if key_normalized in topic_info.docs:
                    target_topics.append(topic_info)
        else:
            topic_key = normalize_node_part(key_normalized)
            for _, topic_name, topic_info in all_topics:
                if normalize_node_part(topic_name) == topic_key:
                    target_topics.append(topic_info)

        for topic in target_topics:
            for alias in aliases:
                if alias:
                    topic.aliases.add(alias)


def serialize_domains(domains: dict[str, DomainInfo]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for domain_name in sorted(domains):
        domain_info = domains[domain_name]
        topics_payload: dict[str, object] = {}
        for topic_name in sorted(domain_info.topics):
            topic_info = domain_info.topics[topic_name]
            topic_aliases = sorted(
                alias
                for alias in topic_info.aliases
                if normalize_node_part(alias) != normalize_node_part(topic_name)
            )
            topics_payload[topic_name] = {
                "aliases": topic_aliases,
                "docs": sorted(topic_info.docs),
            }
        domain_aliases = sorted(
            alias
            for alias in domain_info.aliases
            if normalize_node_part(alias) != normalize_node_part(domain_name)
        )
        payload[domain_name] = {
            "aliases": domain_aliases,
            "topics": topics_payload,
        }
    return payload


def build_domain_topic_map(config: BuildConfig) -> dict[str, object]:
    modules = resolve_target_modules(config)
    meta_files = iter_meta_files(config.base_dir, modules)

    stats = BuildStats()
    domains: dict[str, DomainInfo] = {}
    docs_with_any_node: set[str] = set()

    for meta_path in meta_files:
        stats.scanned_meta_files += 1
        meta = read_json_file(meta_path, strict=config.strict)
        if not meta:
            stats.invalid_json_files += 1
            continue

        doc_id = first_string(meta, "id", "core.id")
        if not doc_id:
            stats.docs_without_id += 1
            if config.strict:
                raise BuildError(f"meta.json missing id: {meta_path}")
            LOGGER.warning("meta.json missing id, skipped: %s", meta_path)
            continue

        node_paths = extract_node_paths(meta)
        if not node_paths:
            stats.docs_without_nodes += 1
            continue

        added_for_doc = False
        for raw_node in node_paths:
            parsed = parse_node_path(raw_node)
            if parsed is None:
                continue
            domain_name, topic_name = parsed
            if not domain_name or not topic_name:
                continue
            add_mapping(domains, domain_name, topic_name, doc_id)
            stats.node_paths_seen += 1
            added_for_doc = True
        if added_for_doc:
            docs_with_any_node.add(doc_id)

    overrides = load_alias_overrides(config.aliases_file, strict=config.strict)
    apply_aliases_overrides(domains, overrides)

    stats.indexed_docs = len(docs_with_any_node)
    serialized_domains = serialize_domains(domains)
    domain_count = len(serialized_domains)
    topic_count = sum(
        len(domain_payload["topics"])  # type: ignore[index]
        for domain_payload in serialized_domains.values()
    )

    payload = {
        "meta": {
            "source": "auto-generated from knowledgeNode + altNodes",
            "generated_at": datetime.now(timezone.utc)
            .astimezone()
            .isoformat(timespec="seconds"),
            "version": 1,
        },
        "stats": {
            "modules": modules,
            "scannedMetaFiles": stats.scanned_meta_files,
            "indexedDocs": stats.indexed_docs,
            "docsWithoutNodes": stats.docs_without_nodes,
            "invalidJsonFiles": stats.invalid_json_files,
            "docsWithoutId": stats.docs_without_id,
            "nodePathsSeen": stats.node_paths_seen,
            "domainCount": domain_count,
            "topicCount": topic_count,
        },
        "domains": serialized_domains,
    }
    return payload


def write_json(path: Path, payload: dict[str, object], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fp:
        json.dump(
            payload,
            fp,
            ensure_ascii=False,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        )
        fp.write("\n")


def main() -> int:
    args = parse_args()
    config = build_config(args)
    configure_logging(config.log_level)

    LOGGER.info("Base dir | %s", config.base_dir)
    LOGGER.info("Aliases file | %s", config.aliases_file)
    LOGGER.info("Dry run | %s", config.dry_run)

    try:
        payload = build_domain_topic_map(config)
        stats = payload.get("stats", {})
        LOGGER.info(
            "Build summary | scanned=%s indexed=%s domains=%s topics=%s",
            stats.get("scannedMetaFiles"),
            stats.get("indexedDocs"),
            stats.get("domainCount"),
            stats.get("topicCount"),
        )
        if config.dry_run:
            LOGGER.info("[dry-run] Skip writing output: %s", config.output)
            return 0
        write_json(config.output, payload, pretty=config.pretty)
        LOGGER.info("domain_topic_map written: %s", config.output)
        return 0
    except Exception as exc:
        LOGGER.error("Build failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
