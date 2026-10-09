"""Generate C043 mobile previews and equal-scale V1/V2 audit sheets."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.static_cards.v2.build import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    v1 = ROOT / "03_conic" / "C043_hyperbola_abc_relation" / "images"
    output = ROOT / ".build" / "static_cards_v2" / "C043"
    if not all((output / f"{n}.png").is_file() for n in ("001", "002", "003")):
        raise ValueError("build all three V2 cards before generating review previews")
    files = {}
    for n in ("001", "002", "003"):
        with Image.open(output / f"{n}.png") as im:
            image = im.convert("RGB")
            if image.size != (1080, 1440):
                raise ValueError(f"invalid V2 size: {n}")
            for width in (390, 360):
                height = width * 4 // 3
                target = output / f"{n}_mobile_{width}.png"
                image.resize((width, height), Image.Resampling.LANCZOS).save(target)
                files[target.name] = digest(target)
        with Image.open(v1 / f"{n}.png") as old:
            old_image = old.convert("RGB")
            if old_image.size != (1080, 1440):
                raise ValueError(f"invalid V1 size: {n}")
            sheet = Image.new("RGB", (780, 550), "#E9EDF3")
            draw = ImageDraw.Draw(sheet)
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 19)
            draw.text((167, 7), "V1", fill="#18283D", font=font)
            draw.text((552, 7), "V2", fill="#18283D", font=font)
            sheet.paste(old_image.resize((390, 520), Image.Resampling.LANCZOS), (0, 30))
            sheet.paste(image.resize((390, 520), Image.Resampling.LANCZOS), (390, 30))
            target = output / f"{n}_v1_v2.png"
            sheet.save(target)
            files[target.name] = digest(target)
    report = {"status": "VISUAL REVIEW PENDING", "comparison_scale": "390×520 both versions",
              "mobile_resampling": "Pillow LANCZOS", "files_sha256": files,
              "v1_sha256": {f"{n}.png": digest(v1 / f"{n}.png")
                            for n in ("001", "002", "003")}}
    (output / "review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "review_files": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
