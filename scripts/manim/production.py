"""UID-neutral Manim rendering and guarded GIF export."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from verify_gif import verify_gif


ROOT = Path(__file__).resolve().parents[2]
MODULES = frozenset({
    "00_set", "01_function", "02_sequence", "03_conic", "04_vector",
    "05_geometry-solid", "06_probability-stat", "07_inequality",
    "08_trigonometry", "09_geometry-plane", "10_junior_basics",
})
UID = re.compile(r"[A-Z][0-9]{3}\Z")
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
SCENE_CLASS = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def conclusion(uid: str) -> Path:
    uid = uid.upper()
    if not UID.fullmatch(uid):
        raise ValueError(f"invalid UID: {uid}")
    matches = [child for module in ROOT.iterdir() if module.is_dir()
               and module.name in MODULES
               for child in module.iterdir() if child.is_dir()
               and child.name.startswith(uid + "_")]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one conclusion for {uid}; found {len(matches)}")
    target = matches[0].resolve()
    if not inside(target, ROOT.resolve()):
        raise ValueError("conclusion path escapes repository")
    return target


def scenes_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = [base.id if isinstance(base, ast.Name) else base.attr
                 if isinstance(base, ast.Attribute) else "" for base in node.bases]
        if any(base in {"Scene", "MovingCameraScene", "ThreeDScene", "ZoomedScene"}
               for base in bases):
            result.append(node.name)
    return result


def select_scene(folder: Path, scene_file: str | None, scene: str | None) -> tuple[Path, str]:
    source_dir = folder / "manim"
    if not source_dir.is_dir() or not inside(source_dir.resolve(), folder):
        raise ValueError(f"invalid Manim source directory: {source_dir}")
    if scene_file:
        if Path(scene_file).name != scene_file or not re.fullmatch(r"scene[A-Za-z0-9_-]*\.py", scene_file):
            raise ValueError("scene-file must be a direct scene*.py file in this UID")
        files = [source_dir / scene_file]
    else:
        files = sorted(source_dir.glob("scene*.py"))
    found = []
    for path in files:
        if path.is_file():
            if not inside(path.resolve(), source_dir.resolve()):
                raise ValueError(f"scene file escapes this UID: {path}")
            found.extend((path, name) for name in scenes_in(path))
    if scene:
        if not SCENE_CLASS.fullmatch(scene):
            raise ValueError(f"invalid Scene: {scene}")
        found = [(path, name) for path, name in found if name == scene]
    if len(found) != 1:
        choices = ", ".join(f"{path.name}:{name}" for path, name in found) or "none"
        raise ValueError(f"Scene selection ambiguous or missing ({choices}); specify -Scene and -SceneFile")
    return found[0]


def location(args: argparse.Namespace) -> tuple[str, Path, Path, str, Path]:
    uid = args.uid.upper()
    folder = conclusion(uid)
    source, scene = select_scene(folder, args.scene_file, args.scene)
    name = args.name or scene
    if not SAFE_NAME.fullmatch(name):
        raise ValueError(f"invalid output name: {name}")
    allowed = (ROOT / "build" / "manim").resolve()
    if not inside(allowed, ROOT.resolve()):
        raise ValueError("build/manim escapes repository")
    build_root = Path(args.build_root)
    if not build_root.is_absolute():
        build_root = ROOT / build_root
    build_root = build_root.resolve()
    if not inside(build_root, allowed):
        raise ValueError(f"build root must stay inside {allowed}")
    work = build_root / uid / name
    if not inside(work.resolve(), allowed):
        raise ValueError("build path escapes repository build/manim")
    return uid, folder, source, scene, work


def identity(work: Path, uid: str, source: Path, scene: str) -> None:
    expected = {"uid": uid, "source": source.name, "scene": scene}
    marker = work / "source.json"
    if marker.is_symlink():
        raise ValueError(f"source marker must not be a symlink: {marker}")
    if marker.exists() and json.loads(marker.read_text(encoding="utf-8")) != expected:
        raise ValueError(f"output name already belongs to a different scene: {work}")
    work.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(expected, sort_keys=True), encoding="utf-8")


def render(args: argparse.Namespace) -> Path:
    uid, _folder, source, scene, work = location(args)
    identity(work, uid, source, scene)
    media = work / "media"
    if not inside(media.resolve(), (ROOT / "build" / "manim").resolve()):
        raise ValueError("media path escapes build/manim")
    output = work / f"{work.name}.mp4"
    command = [sys.executable, "-m", "manim", "--disable_caching", "-r", "576,1024",
               "--fps", "24", "--media_dir", str(media), "--output_file",
               output.name, str(source), scene]
    subprocess.run(command, cwd=ROOT, check=True)
    videos = media / "videos"
    found = [path for path in videos.rglob(output.name)
             if path.is_file() and "partial_movie_files" not in path.parts]
    if len(found) != 1:
        raise ValueError(f"expected one rendered MP4 for {scene}; found {len(found)}")
    staged = work / f".{output.name}.{uuid.uuid4().hex}.tmp"
    try:
        shutil.copyfile(found[0], staged)
        os.replace(staged, output)
    finally:
        staged.unlink(missing_ok=True)
    print(f"MP4: {output}")
    return output


def export(args: argparse.Namespace) -> Path:
    if args.overwrite and not args.publish:
        raise ValueError("-Overwrite requires -Publish")
    uid, folder, source, scene, work = location(args)
    asset_name = args.asset_name or f"{work.name}.gif"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*\.gif", asset_name, re.IGNORECASE):
        raise ValueError(f"invalid GIF asset name: {asset_name}")
    if args.publish:
        images = folder / "images"
        if not images.is_dir() or not inside(images.resolve(), folder):
            raise ValueError(f"invalid images directory: {images}")
        target = images / asset_name
        if target.exists() and not args.overwrite:
            raise ValueError(f"formal GIF exists; explicit -Overwrite required: {target}")
    identity(work, uid, source, scene)
    mp4 = render(args) if args.rebuild else work / f"{work.name}.mp4"
    if not mp4.is_file() or not inside(mp4.resolve(), work.resolve()):
        raise ValueError(f"input MP4 missing: {mp4}; render first or use -Rebuild")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ValueError("FFmpeg unavailable on PATH")
    palette = work / f".palette.{uuid.uuid4().hex}.png"
    staged = work / f".{asset_name}.{uuid.uuid4().hex}.tmp.gif"
    output = work / asset_name
    try:
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i",
                        str(mp4), "-vf", "fps=12,scale=576:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff",
                        str(palette)], check=True)
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i",
                        str(mp4), "-i", str(palette), "-filter_complex",
                        "[0:v]fps=12,scale=576:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
                        "-loop", "0", str(staged)], check=True)
        info = verify_gif(staged)
        if args.publish:
            output = target
            temporary = images / f".{asset_name}.{uuid.uuid4().hex}.tmp"
            try:
                shutil.copyfile(staged, temporary)
                if args.overwrite:
                    os.replace(temporary, output)
                else:
                    os.link(temporary, output)  # Atomic create, never overwrites.
            finally:
                temporary.unlink(missing_ok=True)
        else:
            os.replace(staged, output)
        print(json.dumps(info, ensure_ascii=False, sort_keys=True))
        print(f"GIF: {output}")
        return output
    finally:
        palette.unlink(missing_ok=True)
        staged.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("render", "export"):
        p = sub.add_parser(command)
        p.add_argument("--uid", required=True)
        p.add_argument("--scene")
        p.add_argument("--scene-file")
        p.add_argument("--name")
        p.add_argument("--build-root", default="build/manim")
        if command == "export":
            p.add_argument("--asset-name")
            p.add_argument("--rebuild", action="store_true")
            p.add_argument("--publish", action="store_true")
            p.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        render(args) if args.command == "render" else export(args)
    except (ValueError, OSError, subprocess.CalledProcessError, SyntaxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
