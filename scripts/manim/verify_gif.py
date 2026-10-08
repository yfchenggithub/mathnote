"""Fail a build when the exported GIF is not a real looping animation."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from PIL import Image, ImageSequence


def main(path: Path) -> None:
    if path.read_bytes()[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("invalid GIF header")
    with Image.open(path) as gif:
        if gif.format != "GIF" or gif.size != (576, 1024):
            raise ValueError(f"unexpected GIF format or size: {gif.format} {gif.size}")
        if gif.info.get("loop") != 0:
            raise ValueError("GIF must explicitly loop forever")
        frame_count = getattr(gif, "n_frames", 1)
        if frame_count < 100:
            raise ValueError(f"too few animation frames: {frame_count}")
        durations = []
        hashes = set()
        for frame in ImageSequence.Iterator(gif):
            durations.append(frame.info.get("duration", 0))
            hashes.add(sha256(frame.convert("RGB").tobytes()).digest())
        if min(durations) <= 0:
            raise ValueError("GIF contains a zero-duration frame")
        if len(hashes) < 50:
            raise ValueError(f"too few distinct moving frames: {len(hashes)}")
        total = sum(durations) / 1000
        if not 12 <= total <= 19:
            raise ValueError(f"unexpected duration: {total:.2f}s")
        print(f"GIF PASS: {gif.width}x{gif.height}, {frame_count} frames, "
              f"{len(hashes)} distinct, {total:.2f}s, loop=0, "
              f"{path.stat().st_size / 1048576:.2f} MiB")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
