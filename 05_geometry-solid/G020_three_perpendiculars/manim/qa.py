"""Inspect the actual staged G020 GIF and make world-identical camera views."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from manim import DEGREES, ThreeDCamera, config

from math_model import RAISED, norm, subtract


ROOT = Path(__file__).resolve().parents[3]
BUILD = ROOT / "build/manim/G020/14F_1"
GIF = BUILD / "G020/three_perpendiculars/three_perpendiculars.gif"
OUT = BUILD / "qa"
OUT.mkdir(parents=True, exist_ok=True)


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_gif() -> dict:
    frames: list[Image.Image] = []
    delays: list[int] = []
    with Image.open(GIF) as im:
        loop = im.info.get("loop")
        size = im.size
        for index in range(im.n_frames):
            im.seek(index)
            delays.append(int(im.info.get("duration", 0)))
            frames.append(im.convert("RGB"))
    times = np.cumsum([0] + delays)
    targets = [0, .8, 1.5, 2.35, 3.2, 4.15, 5.1, 6.2, 7.2, 8.3, 9.6, 10.7, 12.0, 13.2, times[-1] / 1000 - .12]
    picks = sorted(set(min(len(frames)-1, int(np.searchsorted(times[:-1], t*1000))) for t in targets))
    thumbnails = []
    for index in picks:
        p = OUT / f"keyframe_{index:03d}.png"
        frames[index].save(p)
        thumb = frames[index].resize((216, 384))
        thumbnails.append((index, thumb))
    sheet = Image.new("RGB", (216 * 4, 410 * ((len(thumbnails)+3)//4)), "#FFFFFF")
    draw = ImageDraw.Draw(sheet)
    for i, (index, thumb) in enumerate(thumbnails):
        x, y = (i % 4)*216, (i // 4)*410
        sheet.paste(thumb, (x, y+22))
        draw.text((x+8, y+3), f"f{index}  {times[index]/1000:.2f}s", fill="black")
    sheet.save(OUT / "contact_sheet.png")
    for index in (0, picks[len(picks)//2], picks[-3]):
        frames[index].resize((360, 640)).save(OUT / f"phone_360_frame_{index:03d}.png")

    blank = 0
    dark_border = 0
    frame_hashes = []
    for frame in frames:
        small = np.asarray(frame.resize((144, 256)), dtype=np.uint8)
        if int(np.sum(np.any(small < 235, axis=2))) < 200:
            blank += 1
        arr = np.asarray(frame, dtype=np.uint8)
        edge = np.concatenate([arr[:3].reshape(-1,3), arr[-3:].reshape(-1,3),
                               arr[:, :3].reshape(-1,3), arr[:, -3:].reshape(-1,3)])
        if np.any(np.all(edge < 70, axis=1)):
            dark_border += 1
        frame_hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
    first = np.asarray(frames[0], dtype=np.int16)
    last = np.asarray(frames[-1], dtype=np.int16)
    first_last_mean = float(np.mean(np.abs(first-last)))
    return {
        "path": str(GIF.relative_to(ROOT)), "sha256": hash_file(GIF),
        "width": size[0], "height": size[1], "frames": len(frames),
        "distinct_frames": len(set(frame_hashes)), "duration_ms": int(times[-1]),
        "delay_min_ms": min(delays), "delay_max_ms": max(delays), "loop": loop,
        "bytes": GIF.stat().st_size, "blank_frames": blank,
        "frames_with_dark_3px_border": dark_border,
        "first_last_mean_abs_channel_delta": first_last_mean,
        "keyframe_indices": picks,
    }


def camera_diagnostics() -> dict:
    config.frame_width = 9
    config.frame_height = 16
    s = RAISED
    points = {"O": s.O, "A": s.A, "P": s.P,
              "l-": s.point_on_l(-1.9), "l+": s.point_on_l(1.9)}
    views = {"oblique": (45, -35), "near_top": (15, -35), "side": (78, -20)}
    result = {"world_plane_dot": s.plane_dot, "world_space_dot": s.space_dot,
              "views": {}}
    for name, (phi, theta) in views.items():
        camera = ThreeDCamera(
            phi=phi*DEGREES, theta=theta*DEGREES, zoom=1.4,
            frame_center=np.array((1.6, 0, .2)),
        )
        def xy(point):
            q = camera.project_point(np.asarray(point, dtype=float))
            return (float(q[0]), float(q[1]))
        def pixels(point):
            x, y = xy(point)
            return (round(288 + x*64), round(512 - y*64))
        canvas = Image.new("RGB", (576, 1024), "#F7F8FA")
        draw = ImageDraw.Draw(canvas)
        corners = [(-.25,-1.85,0), (4.1,-1.85,0), (4.1,1.85,0), (-.25,1.85,0)]
        draw.polygon([pixels(p) for p in corners], fill="#E5EEF4", outline="#A7B4C2", width=2)
        for key, start, end, color, width in (
            ("OA", s.O, s.A, "#158068", 7),
            ("l", points["l-"], points["l+"], "#8055B2", 7),
            ("PO", s.P, s.O, "#2778BD", 4),
            ("PA", s.P, s.A, "#CD6031", 8),
        ):
            draw.line([pixels(start), pixels(end)], fill=color, width=width)
        for key in ("O", "A", "P"):
            x, y = pixels(points[key])
            draw.ellipse((x-7,y-7,x+7,y+7), fill="#B77D12")
            draw.text((x+10,y-15), key, fill="#213044")
        draw.text((18,25), f"{name}: phi={phi}, theta={theta}; SAME WORLD GEOMETRY", fill="#213044")
        canvas.save(OUT / f"diagnostic_{name}.png")
        coords = {key: xy(value) for key, value in points.items()}
        result["views"][name] = {
            "phi_deg": phi, "theta_deg": theta, "projected_scene_coordinates": coords,
            "P_O_screen_distance": float(norm((coords["P"][0]-coords["O"][0], coords["P"][1]-coords["O"][1], 0))),
            "A_O_screen_distance": float(norm((coords["A"][0]-coords["O"][0], coords["A"][1]-coords["O"][1], 0))),
        }
    return result


if __name__ == "__main__":
    report = {"actual_gif": inspect_gif(), "camera": camera_diagnostics()}
    (OUT / "qa_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"gif": report["actual_gif"], "camera_world_dots":
                      (report["camera"]["world_plane_dot"], report["camera"]["world_space_dot"])},
                     ensure_ascii=False, indent=2))
