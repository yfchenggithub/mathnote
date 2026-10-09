"""Check that a GIF is complete, animated, timed, and infinitely looping."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from PIL import Image, ImageSequence


def verify_gif(path: Path, *, width: int | None = None,
               height: int | None = None) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size < 32:
        raise ValueError(f"GIF missing or too small: {path}")
    with path.open("rb") as source:
        if source.read(6) not in (b"GIF87a", b"GIF89a"):
            raise ValueError("invalid GIF header")
    with Image.open(path) as gif:
        if gif.format != "GIF":
            raise ValueError(f"unexpected format: {gif.format}")
        if width is not None and gif.width != width:
            raise ValueError(f"unexpected width: {gif.width}; expected {width}")
        if height is not None and gif.height != height:
            raise ValueError(f"unexpected height: {gif.height}; expected {height}")
        if gif.info.get("loop") != 0:
            raise ValueError("GIF must explicitly loop forever")
        frame_count = getattr(gif, "n_frames", 1)
        if frame_count < 2:
            raise ValueError(f"too few animation frames: {frame_count}")
        durations: list[int] = []
        hashes: set[bytes] = set()
        blank_frames = 0
        for frame in ImageSequence.Iterator(gif):
            duration = frame.info.get("duration", 0)
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError("GIF contains a zero-duration frame")
            durations.append(int(duration))
            rgb = frame.convert("RGB")
            rgb.load()  # Force complete decode, including the last frame.
            hashes.add(sha256(rgb.tobytes()).digest())
            if rgb.getextrema() == ((0, 0), (0, 0), (0, 0)):
                blank_frames += 1
        if len(durations) != frame_count:
            raise ValueError("GIF frame count changed during decode")
        if len(hashes) < 2:
            raise ValueError("GIF contains no visible motion")
        if blank_frames > max(2, frame_count // 5):
            raise ValueError(f"too many black frames: {blank_frames}")
        return {
            "valid": True,
            "width": gif.width,
            "height": gif.height,
            "frame_count": frame_count,
            "distinct_frames": len(hashes),
            "duration_seconds": round(sum(durations) / 1000, 3),
            "min_frame_duration_ms": min(durations),
            "max_frame_duration_ms": max(durations),
            "loop": "infinite",
            "black_frames": blank_frames,
            "bytes": path.stat().st_size,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_gif(args.path, width=args.width, height=args.height),
                         sort_keys=True))
    except (OSError, ValueError) as exc:
        print(f"GIF FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
