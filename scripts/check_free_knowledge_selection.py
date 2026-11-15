"""Audit editorial free selection against canonical sources and actual exports.

Read-only: this tool never assigns classifications or changes source metadata.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

if __package__:
    from .zhishu import content_package as full
    from .zhishu import module_package as module
    from .zhishu.runtime_mapping import parse_is_pro
    from .zhishu.source_discovery import scan_repository
else:
    from zhishu import content_package as full
    from zhishu import module_package as module
    from zhishu.runtime_mapping import parse_is_pro
    from zhishu.source_discovery import scan_repository


class SelectionError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise SelectionError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validate_sources(root: Path, selection_path: Path):
    selection = read_json(selection_path)
    scan = scan_repository(root)
    require(not scan.errors, str([(str(e.path), e.message) for e in scan.errors]))
    records = {}
    module_stats = {}
    inventory = []
    for group in scan.modules:
        counts = Counter(total=0, free=0, licensed=0)
        for source in group.sources:
            m = read_json(source.meta_json_path)
            uid = m.get("id")
            require(isinstance(uid, str) and re.fullmatch(r"[A-Z]\d{3}", uid), f"invalid conclusion ID: {source.meta_json_path}")
            require(source.conclusion_dir_name.startswith(uid + "_"), f"ID/directory mismatch: {source.meta_json_path}")
            require(uid not in records, f"duplicate source ID: {uid}")
            require(isinstance(m.get("core"), dict) and isinstance(m["core"].get("title"), str) and m["core"]["title"].strip(), f"missing title: {uid}")
            require(isinstance(m.get("knowledgeNode"), str) and m["knowledgeNode"].strip(), f"missing chapter: {uid}")
            try:
                flag = parse_is_pro(m.get("isPro"))
            except ValueError as exc:
                raise SelectionError(f"{source.meta_json_path}: {exc}") from exc
            records[uid] = {"data": m, "source": source, "module": group.module_name}
            counts["total"] += 1
            counts["free" if flag == 0 else "licensed"] += 1
            inventory.append({"id":uid,"title":m["core"]["title"],"module":group.module_name,"chapter":m["knowledgeNode"],"isPro":flag,"source":source.meta_json_path.relative_to(root).as_posix()})
        module_stats[group.module_name] = dict(counts)
    require(len(records) == selection["baselineTotal"], f"source total changed: actual={len(records)} selection={selection['baselineTotal']}; review the target before reclassifying")
    chosen = selection["conclusions"]
    require(len(chosen) == selection["targetFree"], "free list count mismatch")
    ids = [row["id"] for row in chosen]
    require(len(ids) == len(set(ids)), "duplicate free ID")
    require(set(ids) <= set(records), f"unknown free IDs: {set(ids)-set(records)}")
    categories = Counter()
    path_members = {}
    paths = selection["learningPaths"]
    require(len({p["id"] for p in paths}) == len(paths), "duplicate path ID")
    for path in paths:
        require(path["rationale"].strip(), f"missing path rationale: {path['id']}")
        require(path["steps"], f"empty path: {path['id']}")
        require(set(path.get('supportingFreeIds', [])) <= set(ids), f"path supporting knowledge is not free: {path['id']}")
        for step in path["steps"]:
            require(step["id"] not in path_members, f"repeated path member: {step['id']}")
            require(step["role"].strip(), f"missing learning role: {step['id']}")
            path_members[step["id"]] = path["id"]
    for row in chosen:
        uid = row["id"]
        src = records[uid]
        require(row["title"] == src["data"]["core"]["title"], f"stale title: {uid}")
        require(row["module"] == src["module"], f"wrong source module: {uid}")
        require(row["chapter"] == src["data"]["knowledgeNode"], f"wrong chapter: {uid}")
        require(row["category"] in ("A", "B", "C"), f"invalid free category: {uid}")
        require(isinstance(row["reason"], str) and row["reason"].strip(), f"empty free reason: {uid}")
        if row["category"] == "A":
            require(path_members.get(uid) == row["pathId"], f"path membership mismatch: {uid}")
        else:
            require(row["pathId"] is None and uid not in path_members, f"non-A path member: {uid}")
        categories[row["category"]] += 1
    require(set(path_members) == {r["id"] for r in chosen if r["category"] == "A"}, "path/list coverage mismatch")
    require(dict(categories) == selection["categories"], "A/B/C quota mismatch")
    free = set(ids)
    for uid, src in records.items():
        require(src["data"]["isPro"] == (0 if uid in free else 1), f"source/list isPro mismatch: {uid}")
    return records, {"total":len(records),"free":len(free),"licensed":len(records)-len(free),"categories":dict(categories),"modules":module_stats,"inventory":inventory}


def validate_nodes(rows, records, expected_ids, label):
    nodes = {}
    for row in rows:
        require(row["id"] not in nodes, f"{label}: duplicate node ID {row['id']}")
        nodes[row["id"]] = row
    knowledge = {uid:row for uid,row in nodes.items() if row["type"] == "knowledge"}
    require(set(knowledge) == set(expected_ids), f"{label}: knowledge coverage mismatch")
    for uid,row in nodes.items():
        if row["type"] != "knowledge":
            require("isPro" not in row, f"{label}: structural node has isPro: {uid}")
            continue
        try:
            flag = parse_is_pro(row.get("isPro"))
        except ValueError as exc:
            raise SelectionError(f"{label}/{uid}: {exc}") from exc
        require(flag == records[uid]["data"]["isPro"], f"{label}: exported/source flag mismatch: {uid}")
    return {"total":len(knowledge),"free":sum(r["isPro"]==0 for r in knowledge.values()),"licensed":sum(r["isPro"]==1 for r in knowledge.values()),"structural":len(nodes)-len(knowledge)}


def validate_exports(records, full_root, modules_root):
    # The existing Full loader validates every resource and all five arrays.
    # Reuse that immutable, validated snapshot for each module's unchanged
    # provenance validator, rather than decoding all Full videos 14 times.
    source = module.load_full(full_root)
    data = source[1]
    result = {"full":validate_nodes(data["knowledgeNodes"], records, set(records), "Full")}
    if modules_root:
        slugs = module.discover_modules(data)
        require({p.stem for p in modules_root.glob('*.zip')} == set(slugs), "module ZIP set mismatch")
        union = set()
        result["modules"] = {}
        for slug in slugs:
            archive = modules_root / (slug + ".zip")
            with module.temporary_directory() as extracted:
                module._extract(archive, extracted)
                module._validate_directory(extracted, source)
            with zipfile.ZipFile(archive) as z:
                rows = json.loads(z.read('knowledge-nodes.json'), object_pairs_hook=unique_object)
            expected = {r['id'] for r in module.select(data,slug)['knowledgeNodes'] if r['type']=='knowledge'}
            require(not union.intersection(expected), f"conclusion duplicated across module ZIPs: {slug}")
            union.update(expected)
            result['modules'][slug] = validate_nodes(rows,records,expected,slug)
        require(union == set(records), "module union omits source conclusions")
        require(sum(r['free'] for r in result['modules'].values()) == result['full']['free'], "module free count differs from Full")
        require(sum(r['licensed'] for r in result['modules'].values()) == result['full']['licensed'], "module licensed count differs from Full")
    return result


def validate_unchanged(root, records, baseline_path):
    baseline = read_json(baseline_path)
    require(set(baseline['records']) == set(records), "source IDs added or removed")
    changed = []
    for uid,old in baseline['records'].items():
        current = dict(records[uid]['data']);previous = dict(old['data'])
        current.pop('isPro');previous.pop('isPro')
        require(current == previous, f"unrelated source metadata changed: {uid}")
        raw = records[uid]['source'].meta_json_path.read_bytes()
        restored, matches = re.subn(rb'("isPro"\s*:\s*)[01](?=\s*[,}])',
                                   lambda m: m[1]+str(old['data']['isPro']).encode('ascii'), raw)
        require(matches == 1 and hashlib.sha256(restored).hexdigest() == old['sha256'],
                f"metadata bytes beyond isPro changed: {uid}")
        if old['data']['isPro'] != records[uid]['data']['isPro']:
            changed.append(old['path'])
    for relative,digest in baseline['protected'].items():
        path = root / relative
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest, f"protected content changed: {relative}")
    return {"changedMetadata":changed,"protectedFilesVerified":len(baseline['protected']),"unrelatedMetadataUnchanged":True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--selection',type=Path,default=Path('data/content/free-knowledge-selection.json'))
    parser.add_argument('--full',type=Path)
    parser.add_argument('--modules',type=Path)
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        require(not args.modules or args.full, '--modules requires --full')
        root=args.root.resolve();selection=args.selection if args.selection.is_absolute() else root/args.selection
        records,result=validate_sources(root,selection)
        if args.baseline:result['preservation']=validate_unchanged(root,records,args.baseline)
        if args.full:result['exports']=validate_exports(records,args.full,args.modules)
        if args.baseline and args.full:
            old=read_json(args.baseline)['runtime']
            for group in ('knowledgeNodes','knowledgeRelations','searchDocuments'):
                rows=read_json(args.full/full.JSON_FILES[group])
                if group=='knowledgeNodes':
                    for row in rows:row.pop('isPro',None)
                require(rows==old[group],f'pre-existing runtime fields changed: {group}')
            result['preservation']['runtimeNodeRelationSearchFieldsUnchanged']=True
        result['status']='PASS'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k not in ('inventory','preservation')},ensure_ascii=False,indent=2))
        return 0
    except (SelectionError,OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile) as exc:
        print(f'SELECTION AUDIT FAILED: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
