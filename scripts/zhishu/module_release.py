"""Audit and publish the complete registered v4 module set through existing slicer.

No source discovery, rendering, Sync or Android writes. Existing differing files
are preserved and block promotion; two staging builds remain available to inspect.
"""
from __future__ import annotations

import argparse
import shutil
import time
import zipfile
from collections import Counter
from pathlib import Path

if __package__:
    from . import module_package as m
else:
    import module_package as m


def fingerprint(root: Path) -> dict[str, str]:
    return {name: m.full._sha256_file(path) for name, path in m.inventory(root).items()}


def keyed(rows, field):
    result = {r[field]: r for r in rows}
    m.require(len(result) == len(rows), f"duplicate {field}")
    return result


def audit_modules(source_root: Path, packages: Path) -> tuple[dict, dict]:
    """Read real ZIPs, independently walk parent chains and compare entire records."""
    started = time.perf_counter()
    source = m.load_full(source_root)
    data = source[1]
    slugs = m.discover_modules(data)
    m.require({p.name for p in packages.glob('*.zip')} == {s + '.zip' for s in slugs},
              "release ZIP set mismatch")
    nodes = keyed(data['knowledgeNodes'], 'id')
    owners = {}
    # Upward traversal is independent of the slicer's downward subtree collection.
    registry = {r[2]: slug for slug, r in m.MODULES.items()}
    for node in nodes.values():
        if node['id'] == m.ROOT:
            continue
        current = node
        while current.get('parentId') != m.ROOT:
            current = nodes[current['parentId']]
        owners[node['id']] = registry[current['id']]
    merged = {k: {} for k in ('knowledgeNodes', 'searchDocuments', 'knowledgeAssets', 'animationShares')}
    occurrences = {k: Counter() for k in merged}
    cores, declarations, shared_resources = {}, Counter(), {}
    internal = external = media_files = 0
    entries = []
    for slug in slugs:
        archive = packages / (slug + '.zip')
        with m.temporary_directory() as root:
            m._extract(archive, root)
            manifest = m._validate_directory(root, source)
            local = {k: m.read_json(root / name) for k, name in m.FILES.items()}
            expected_nodes = {m.ROOT} | {id for id, owner in owners.items() if owner == slug}
            m.require({r['id'] for r in local['knowledgeNodes']} == expected_nodes,
                      f"parent-chain module boundary mismatch: {slug}")
            for group in merged:
                field = m.ID_FIELDS[group]
                for row in local[group]:
                    id = row[field]
                    m.require(id not in merged[group] or merged[group][id] == row,
                              f"conflicting shared entity: {group}/{id}")
                    merged[group][id] = row
                    occurrences[group][id] += 1
                    if group == 'knowledgeNodes' and row['type'] == 'knowledge':
                        m.require(occurrences[group][id] == 1, f"duplicate knowledge owner: {id}")
                    if group in ('knowledgeAssets', 'animationShares'):
                        m.require(owners.get(row['knowledgeId']) == slug, f"illegal media owner: {id}")
            for group in ('knowledgeRelations', 'externalRelations'):
                for row in local[group]:
                    core = {k: v for k, v in row.items() if k not in m.EXT_FIELDS}
                    id = core['id']
                    m.require(id not in cores or cores[id] == core, f"conflicting relation core: {id}")
                    cores[id] = core
                    declarations[id] += 1
                    a, b = core['sourceId'], core['targetId']
                    m.require(a in owners and b in owners and nodes[a]['type'] == nodes[b]['type'] == 'knowledge',
                              f"unresolved relation: {a} -> {b}")
                    same = owners[a] == owners[b]
                    m.require(same == (group == 'knowledgeRelations'), f"incorrect relation scope: {id}")
                    if not same:
                        absent = b if owners[a] == slug else a
                        hint = row['targetPackageId']
                        m.require(row['externalEndpointId'] == absent and
                                  hint in (None, m.MODULES[owners[absent]][0]), f"wrong external target: {id}")
            internal += len(local['knowledgeRelations'])
            external += len(local['externalRelations'])
            media_files += len(manifest['resources'])
            for uri, resource in manifest['resources'].items():
                previous = shared_resources.setdefault(uri, {'metadata': resource, 'modules': []})
                m.require(previous['metadata'] == resource, f"conflicting resource URI: {uri}")
                previous['modules'].append(slug)
                m.require(m.full._sha256_file(source_root / uri) == resource['sha256'],
                          f"source media byte mismatch: {uri}")
            with zipfile.ZipFile(archive) as stream:
                infos = stream.infolist()
                m.require(stream.namelist() == sorted(stream.namelist(), key=lambda s: s.encode('utf8')),
                          f"nondeterministic ZIP order: {slug}")
                m.require(not stream.comment and all(i.date_time == (1980, 1, 1, 0, 0, 0)
                          and not i.extra and not i.comment and i.compress_type == zipfile.ZIP_STORED
                          for i in infos), f"nondeterministic ZIP metadata: {slug}")
            entries.append({
                'slug': slug, 'moduleId': manifest['moduleId'], 'packageId': manifest['packageId'],
                'name': nodes[manifest['moduleRootNodeId']]['title'], 'zipFile': archive.name,
                'bytes': archive.stat().st_size, 'sha256': m.full._sha256_file(archive),
                'contentVersion': manifest['contentVersion'], 'packageHash': manifest['packageHash'],
                'packageVersion': manifest['packageVersion'], 'knowledgeCount': len(local['searchDocuments']),
                'nodeCount': len(local['knowledgeNodes']), 'searchDocumentCount': len(local['searchDocuments']),
                'mediaCount': len(manifest['resources']), 'imageCount': manifest['counts']['imageAssets'],
                'pdfCount': manifest['counts']['pdfAssets'], 'videoCount': manifest['counts']['videoAssets'],
                'pdfBytes': sum(r['bytes'] for r in manifest['resources'].values() if r['kind'] == 'pdf'),
                'internalRelationCount': len(local['knowledgeRelations']),
                'externalRelationCount': len(local['externalRelations']),
            })
    for group in merged:
        m.require(merged[group] == keyed(data[group], m.ID_FIELDS[group]), f"global coverage mismatch: {group}")
        if group != 'knowledgeNodes':
            m.require(all(v == 1 for v in occurrences[group].values()), f"duplicate module entity: {group}")
    m.tree(list(merged['knowledgeNodes'].values()))
    source_cores = keyed(data['knowledgeRelations'], 'id')
    m.require(cores == source_cores, 'global relation coverage mismatch')
    for id, core in cores.items():
        expected = 1 if owners[core['sourceId']] == owners[core['targetId']] else 2
        m.require(declarations[id] == expected, f"missing/duplicate endpoint declarations: {id}")
    source_uris = {r['uri'] for r in data['knowledgeAssets'] + data['animationShares']}
    m.require(set(shared_resources) == source_uris, 'global resource coverage mismatch')
    entries.sort(key=lambda r: r['packageId'])
    index = {'sourceContentVersion': source[0]['contentVersion'], 'modules': entries}
    audit = {
        'sourceManifest': source[0], 'sourceFileHashes': fingerprint(source_root),
        'moduleCount': len(entries), 'knowledgeCount': len(m.tree(data['knowledgeNodes'])),
        'nodeCount': len(nodes), 'searchDocumentCount': len(merged['searchDocuments']),
        'missingKnowledge': [], 'duplicateKnowledge': [], 'unresolvedRelations': [], 'invalidTargets': [],
        'sharedCategories': {id: count for id, count in occurrences['knowledgeNodes'].items() if count > 1},
        'sourceRelationRecords': len(data['knowledgeRelations']), 'internalRelationRecords': internal,
        'externalRelationRecords': external, 'canonicalRelations': len(cores),
        'duplicateSourceRecords': len(data['knowledgeRelations']) - len(source_cores),
        'duplicateEndpointDeclarations': sum(declarations.values()) - len(cores),
        'crossModuleUniqueRelations': external // 2,
        'mediaUniqueIds': len(merged['knowledgeAssets']) + len(merged['animationShares']),
        'moduleMediaReferences': media_files, 'physicalMediaFiles': media_files,
        'sharedResources': {uri: row for uri, row in shared_resources.items() if len(row['modules']) > 1},
        'uniqueMediaBytes': sum(r['metadata']['bytes'] for r in shared_resources.values()),
        'pdfBytes': sum(r['metadata']['bytes'] for r in shared_resources.values() if r['metadata']['kind'] == 'pdf'),
        'totalZipBytes': sum(r['bytes'] for r in entries), 'missingMedia': [], 'unreferencedMedia': [],
        'knowledgeIds': sorted(id for id, row in nodes.items() if row['type'] == 'knowledge'),
        'moduleOwners': owners, 'relationCores': cores, 'validationSeconds': time.perf_counter() - started,
    }
    return index, audit


def validate_index(source_root: Path, packages: Path) -> dict:
    expected, audit = audit_modules(source_root, packages)
    m.require(m.read_json(packages / 'release-index.json') == expected, 'release index mismatch')
    return audit


def produce_release(source_root: Path, staging: Path, output: Path | None = None,
                    expected_count: int = 14) -> dict:
    source_root, staging = source_root.resolve(), staging.resolve()
    m._no_links(staging)
    m.require(not staging.is_relative_to(source_root) and not source_root.is_relative_to(staging),
              'source/staging directories must be isolated')
    if output is not None:
        output = output.resolve()
        m._no_links(output)
        project = Path(__file__).resolve().parents[2]
        m.require(not project.is_relative_to(output) and output != project / 'build/zhishu-content-package',
                  'refusing protected output')
        m.require(all(not a.is_relative_to(b) and not b.is_relative_to(a)
                      for a, b in ((output, source_root), (output, staging))), 'output directories must be isolated')
    m.require(not staging.exists(), 'staging already exists; use a fresh evidence directory')
    frozen = fingerprint(source_root)
    source = m.load_full(source_root)
    slugs = m.discover_modules(source[1])
    m.require(len(slugs) == expected_count, f'expected {expected_count} real modules, found {len(slugs)}')
    staging.mkdir(parents=True)
    runs = []
    for round, order in enumerate((slugs, list(reversed(slugs))), 1):
        root = staging / f'round-{round}'
        started = time.perf_counter()
        results = m.slice_modules(source_root, root, order)
        build_seconds = time.perf_counter() - started
        index, audit = audit_modules(source_root, root)
        m.write_json(root / 'release-index.json', index)
        runs.append({'buildSeconds': build_seconds, 'modules': results, 'audit': audit})
        m.require(fingerprint(source_root) == frozen, 'frozen source changed')
        m.write_json(staging / f'round-{round}-audit.json', runs[-1])
    first, second = staging / 'round-1', staging / 'round-2'
    m.require(fingerprint(first) == fingerprint(second), 'two builds differ at byte level')
    result = {'status': 'STAGING PASS', 'byteIdentical': True, 'index': index, 'runs': runs}
    m.write_json(staging / 'production.json', result)
    if output is not None:
        promote_release(source_root, first, output, frozen)
        result['status'] = 'PRODUCTION PASS'
        m.write_json(staging / 'production.json', result)
    return result


def promote_release(source_root: Path, staged: Path, output: Path, frozen: dict) -> None:
    # Recheck at the last boundary; never replace a different accepted pilot/package.
    source_root, staged, output = source_root.resolve(), staged.resolve(), output.resolve()
    m._no_links(output)
    project = Path(__file__).resolve().parents[2]
    m.require(not project.is_relative_to(output) and output != project / 'build/zhishu-content-package',
              'refusing protected output')
    m.require(all(not a.is_relative_to(b) and not b.is_relative_to(a)
                  for a, b in ((output, source_root), (output, staged))), 'output directories must be isolated')
    validate_index(source_root, staged)
    m.require(fingerprint(source_root) == frozen, 'frozen source changed before promotion')
    expected = fingerprint(staged)
    old = fingerprint(output) if output.exists() else None
    if old is not None:
        m.require(all(name in expected and expected[name] == value for name, value in old.items()),
                  'EXISTING_OUTPUT_CHANGED: preserved official output; inspect staging before replacement')
        allowed = {*m.MODULES, *(s + '.zip' for s in m.MODULES), 'release-index.json'}
        m.require(all(p.name in allowed for p in output.iterdir()), 'unrelated official output entry')
    output.parent.mkdir(parents=True, exist_ok=True)
    with m.temporary_directory(output.parent, f'.{output.name}.release-') as prepared:
        shutil.copytree(staged, prepared, dirs_exist_ok=True)
        m.require(fingerprint(prepared) == expected, 'promotion copy mismatch')
        m.require((fingerprint(output) if output.exists() else None) == old,
                  'official output changed during promotion')
        m.require(fingerprint(source_root) == frozen, 'frozen source changed during promotion')
        m.replace_output(prepared, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--staging', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='promote only after complete validation; otherwise stage only')
    args = parser.parse_args()
    try:
        result = produce_release(args.input, args.staging, args.output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'MODULE RELEASE FAILED: {exc}\n')
    print(f"{result['status']}: {len(result['index']['modules'])} ZIPs; byteIdentical={result['byteIdentical']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
