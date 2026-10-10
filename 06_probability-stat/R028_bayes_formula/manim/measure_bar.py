"""Measure the visible positive-pool split in decoded GIF keyframes.

This deliberately reads raster pixels without importing the Manim Scene.
"""

import json
from pathlib import Path
import sys

from PIL import Image


def classify(rgb):
    r, g, b = rgb
    if r >= 145 and r > 1.25 * g and 60 <= g <= 160 and b <= 130:
        return "true_positive"
    if b >= 120 and b > 1.15 * g and 65 <= r <= 180 and g <= 150:
        return "false_positive"
    return None


def measure(path, y=520):
    with Image.open(path) as source:
        row = [classify(source.convert("RGB").getpixel((x, y)))
               for x in range(source.width)]
    orange = [x for x, role in enumerate(row) if role == "true_positive"]
    purple = [x for x, role in enumerate(row) if role == "false_positive"]
    if not orange or not purple:
        raise ValueError(f"missing bar segment in {path}")
    return {
        "file": str(path),
        "scanline_y": y,
        "orange_span": [min(orange), max(orange)],
        "purple_span": [min(purple), max(purple)],
        "orange_pixels": len(orange),
        "purple_pixels": len(purple),
        "visible_orange_share": len(orange) / (len(orange) + len(purple)),
    }


if __name__ == "__main__":
    print(json.dumps([measure(Path(name)) for name in sys.argv[1:]], indent=2))
