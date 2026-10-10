"""Command-line entry point for the Zhishu publisher."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

if __package__:
    from .asset_preparation import (
        DEFAULT_OUTPUT as DEFAULT_RUNTIME_ASSET_OUTPUT,
        RuntimeAssetPreparationError,
        prepare_runtime_images,
        verify_prepared_runtime_images,
    )
    from .content_package import (
        PackageBuildResult,
        PackageDiff,
        build_package,
        diff_packages,
    )
    from .runtime_mapping import RuntimeMappingResult, map_runtime
    from .source_discovery import ScanResult, scan_repository
    from .source_initialization import InitializationResult, initialize_sources
else:
    from asset_preparation import (
        DEFAULT_OUTPUT as DEFAULT_RUNTIME_ASSET_OUTPUT,
        RuntimeAssetPreparationError,
        prepare_runtime_images,
        verify_prepared_runtime_images,
    )
    from content_package import PackageBuildResult, PackageDiff, build_package, diff_packages
    from runtime_mapping import RuntimeMappingResult, map_runtime
    from source_discovery import ScanResult, scan_repository
    from source_initialization import InitializationResult, initialize_sources


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_OUTPUT = PROJECT_ROOT / "build" / "zhishu-content-package"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="publish.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="discover and validate conclusion sources")
    subparsers.add_parser(
        "init-source",
        help="ensure images/ and pdfs/ exist for discovered sources",
    )
    map_runtime_parser = subparsers.add_parser(
        "map-runtime", help="map discovered sources to runtime DTOs"
    )
    map_runtime_parser.add_argument(
        "--prepared-assets",
        type=Path,
        default=DEFAULT_RUNTIME_ASSET_OUTPUT,
        help=f"prepared runtime asset directory (default: {DEFAULT_RUNTIME_ASSET_OUTPUT})",
    )
    prepare_parser = subparsers.add_parser(
        "prepare-assets", help="build the generated runtime image mirror"
    )
    prepare_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RUNTIME_ASSET_OUTPUT,
        help=f"prepared runtime asset directory (default: {DEFAULT_RUNTIME_ASSET_OUTPUT})",
    )
    build_package_parser = subparsers.add_parser(
        "build-package", help="build a package from already prepared runtime images"
    )
    build_package_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PACKAGE_OUTPUT,
        help=f"package output directory (default: {DEFAULT_PACKAGE_OUTPUT})",
    )
    build_package_parser.add_argument(
        "--prepared-assets",
        type=Path,
        default=DEFAULT_RUNTIME_ASSET_OUTPUT,
        help=f"prepared runtime asset directory (default: {DEFAULT_RUNTIME_ASSET_OUTPUT})",
    )
    build_package_parser.add_argument(
        "--share-video-uid", choices=("C002",),
        help="opt in to the isolated v2 video package for this UID",
    )
    build_content_parser = subparsers.add_parser(
        "build-content", help="prepare runtime images, then build the canonical package"
    )
    build_content_parser.add_argument(
        "--prepared-assets",
        type=Path,
        default=DEFAULT_RUNTIME_ASSET_OUTPUT,
        help=f"prepared runtime asset directory (default: {DEFAULT_RUNTIME_ASSET_OUTPUT})",
    )
    build_content_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PACKAGE_OUTPUT,
        help=f"package output directory (default: {DEFAULT_PACKAGE_OUTPUT})",
    )
    build_content_parser.add_argument(
        "--share-video-uid", choices=("C002",),
        help="opt in to the isolated v2 video package for this UID",
    )
    diff_parser = subparsers.add_parser("diff", help="compare two content packages")
    diff_parser.add_argument("previous", type=Path)
    diff_parser.add_argument("current", type=Path)
    return parser


def format_scan_result(result: ScanResult) -> str:
    lines = ["Zhishu Source Discovery", ""]
    for module in result.modules:
        lines.append(f"{module.module_name:<24}{len(module.sources)}")

    if result.errors:
        lines.extend(("", "ERROR"))
        lines.extend(f"{error.path.as_posix()}: {error.message}" for error in result.errors)

    lines.extend(
        (
            "",
            f"Modules: {len(result.modules)}",
            f"Conclusions: {result.conclusion_count}",
            f"Errors: {len(result.errors)}",
        )
    )
    return "\n".join(lines)


def format_initialization_result(result: InitializationResult) -> str:
    lines = ["Zhishu Source Directory Initialization", ""]
    for module in result.modules:
        lines.extend(
            (
                module.module_name,
                f"  Conclusions: {module.conclusion_count}",
                f"  Created images/: {module.created_images}",
                f"  Created pdfs/: {module.created_pdfs}",
                f"  Already initialized: {module.already_initialized}",
                "",
            )
        )

    if result.errors:
        lines.extend(("ERROR",))
        lines.extend(f"{error.path.as_posix()}: {error.message}" for error in result.errors)
        lines.append("")

    lines.extend(
        (
            "Summary",
            "",
            f"Modules: {len(result.modules)}",
            f"Conclusions: {result.conclusion_count}",
            f"Created images/: {result.created_images}",
            f"Created pdfs/: {result.created_pdfs}",
            f"Already initialized: {result.already_initialized}",
            f"Errors: {len(result.errors)}",
        )
    )
    return "\n".join(lines)


def format_runtime_mapping_result(result: RuntimeMappingResult) -> str:
    lines = [
        "Zhishu Runtime Mapping",
        "",
        f"Source Conclusions: {result.source_conclusion_count}",
        f"Structural KnowledgeNodes: {result.structural_node_count}",
        f"Conclusion KnowledgeNodes: {result.conclusion_node_count}",
        f"Total KnowledgeNodes: {len(result.knowledge_nodes)}",
        "",
        "Relations:",
        "  prerequisite: excluded from this phase",
        f"  related: {result.relation_count('related')}",
        f"  next: {result.relation_count('next')}",
        "Similar Relations: excluded from this phase",
        "Alternate Classifications: excluded from this phase",
        "",
        f"Image Assets: {result.asset_count('image')}",
        f"PDF Assets: {result.asset_count('pdf')}",
        f"SearchDocuments: {len(result.search_documents)}",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
    ]
    if result.errors:
        lines.extend(("", "ERROR"))
        lines.extend(
            f"{issue.path.as_posix()}: {issue.message}" for issue in result.errors[:20]
        )
        if len(result.errors) > 20:
            lines.append(f"... {len(result.errors) - 20} more errors")
    if result.warnings:
        lines.extend(("", "WARNING"))
        lines.extend(
            f"{issue.path.as_posix()}: {issue.message}" for issue in result.warnings[:20]
        )
        if len(result.warnings) > 20:
            lines.append(f"... {len(result.warnings) - 20} more warnings")
    return "\n".join(lines)


def format_package_build_result(result: PackageBuildResult) -> str:
    lines = [
        "Zhishu Content Package",
        "",
        f"Output: {result.output_dir}",
        f"contentVersion: {result.content_version}",
        f"packageHash: {result.package_hash}",
        f"Package Size: {result.package_size}",
    ]
    for key, value in result.counts.items():
        lines.append(f"{key}: {value}")
    lines.extend((f"Errors: {len(result.errors)}", f"Warnings: {len(result.warnings)}"))
    if result.errors:
        lines.extend(("", "ERROR"))
        lines.extend(f"{issue.path.as_posix()}: {issue.message}" for issue in result.errors)
    if result.warnings:
        lines.extend(("", "WARNING"))
        lines.extend(f"{issue.path.as_posix()}: {issue.message}" for issue in result.warnings)
    return "\n".join(lines)


def format_asset_preparation_result(manifest: dict[str, object], output: Path) -> str:
    assets = manifest.get("assets", [])
    total_bytes = sum(int(asset["bytes"]) for asset in assets)  # type: ignore[index]
    tool = manifest.get("tool", {})
    return "\n".join(
        (
            "Zhishu Runtime Image Preparation",
            "",
            f"Output: {output.resolve()}",
            f"Images: {len(assets)}",  # type: ignore[arg-type]
            f"Bytes: {total_bytes}",
            f"Tool: {tool.get('name')} {tool.get('version')}",  # type: ignore[union-attr]
        )
    )


def format_package_diff(result: PackageDiff) -> str:
    lines = ["Zhishu Content Package Diff"]
    for entity_type in ("KnowledgeNode", "KnowledgeRelation", "KnowledgeAsset", "SearchDocument", "AnimationShare"):
        lines.extend(("", entity_type))
        for operation in ("ADD", "UPDATE", "DELETE"):
            matching = [
                entry for entry in result.entries
                if entry.entity_type == entity_type and entry.operation == operation
            ]
            lines.append(f"  {operation}: {len(matching)}")
            lines.extend(f"    {entry.entity_id}" for entry in matching)
    lines.extend(("", f"Changes: {len(result.entries)}", f"Errors: {len(result.errors)}"))
    if result.errors:
        lines.extend(("", "ERROR"))
        lines.extend(f"{issue.path.as_posix()}: {issue.message}" for issue in result.errors)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        result = scan_repository(PROJECT_ROOT)
        print(format_scan_result(result))
        return 1 if result.errors else 0
    if args.command == "init-source":
        scan_result = scan_repository(PROJECT_ROOT)
        initialization_result = initialize_sources(scan_result)
        print(format_initialization_result(initialization_result))
        return 1 if initialization_result.errors else 0
    if args.command == "prepare-assets":
        scan_result = scan_repository(PROJECT_ROOT)
        try:
            manifest = prepare_runtime_images(scan_result, args.output)
        except (RuntimeAssetPreparationError, OSError) as exc:
            print(f"Runtime image preparation failed: {exc}")
            return 1
        print(format_asset_preparation_result(manifest, args.output))
        return 0
    if args.command == "map-runtime":
        scan_result = scan_repository(PROJECT_ROOT)
        try:
            verify_prepared_runtime_images(scan_result, args.prepared_assets)
        except (RuntimeAssetPreparationError, OSError) as exc:
            print(f"Runtime image preparation is stale: {exc}")
            return 1
        mapping_result = map_runtime(scan_result, args.prepared_assets)
        print(format_runtime_mapping_result(mapping_result))
        return 1 if mapping_result.errors else 0
    if args.command in ("build-package", "build-content"):
        if args.share_video_uid and args.output.resolve() == DEFAULT_PACKAGE_OUTPUT.resolve():
            print("Video package requires an explicit isolated --output directory")
            return 1
        if (args.command == "build-content" and args.share_video_uid
                and args.prepared_assets.resolve() == DEFAULT_RUNTIME_ASSET_OUTPUT.resolve()):
            print("Video package requires an explicit isolated --prepared-assets directory")
            return 1
        scan_result = scan_repository(PROJECT_ROOT)
        if args.command == "build-content":
            try:
                manifest = prepare_runtime_images(scan_result, args.prepared_assets)
            except (RuntimeAssetPreparationError, OSError) as exc:
                print(f"Runtime image preparation failed: {exc}")
                return 1
            print(format_asset_preparation_result(manifest, args.prepared_assets))
        try:
            verify_prepared_runtime_images(scan_result, args.prepared_assets)
        except (RuntimeAssetPreparationError, OSError) as exc:
            print(f"Runtime image preparation is stale: {exc}")
            return 1
        mapping_result = map_runtime(scan_result, args.prepared_assets)
        build_kwargs = {"share_video_uid": args.share_video_uid} if args.share_video_uid else {}
        package_result = build_package(
            scan_result, mapping_result, args.output, args.prepared_assets, **build_kwargs
        )
        print(format_package_build_result(package_result))
        return 1 if package_result.errors else 0
    if args.command == "diff":
        diff_result = diff_packages(args.previous.resolve(), args.current.resolve())
        print(format_package_diff(diff_result))
        return 1 if diff_result.errors else 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
