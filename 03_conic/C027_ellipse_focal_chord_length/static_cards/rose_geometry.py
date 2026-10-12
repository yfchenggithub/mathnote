"""Exact, transparent diagrams for the C027 rose cards."""

from math import pi
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .model import Ellipse


def draw(kind: str, directory: Path) -> dict:
    if kind not in {"general", "example", "vertical"}:
        raise ValueError(kind)
    e = Ellipse(3, 3**0.5) if kind == "example" else Ellipse(3, 2)
    k = None if kind == "vertical" else (1 if kind == "example" else .65)
    p, q = e.intersections(k)
    check = e.validate_case(k, 1)
    directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"svg.fonttype": "path", "svg.hashsalt": "C027-rose-v1",
                         "mathtext.fontset": "cm"})
    fig = plt.figure(figsize=(5.0, 3.25), dpi=120, facecolor="none")
    ax = fig.add_axes([.045, .09, .91, .82], facecolor="none")
    ax.set_xlim(-3.55, 3.55)
    ax.set_ylim(-2.45, 2.45)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    t = np.linspace(0, 2*pi, 1001)
    ax.plot(e.a*np.cos(t), e.b*np.sin(t), color="#087cc5", lw=2.7, zorder=3)
    ax.plot([-3.4, 3.4], [0, 0], color="#168bd1", lw=1.2, zorder=1)
    ax.plot([0, 0], [-2.35, 2.35], color="#168bd1", lw=1.2, zorder=1)
    if k is None:
        ax.plot([e.c, e.c], [-2.23, 2.23], color="#f47b15", lw=2.7, zorder=4)
    else:
        vx, vy = q[0]-p[0], q[1]-p[1]
        ax.plot([p[0]-.16*vx, q[0]+.16*vx],
                [p[1]-.16*vy, q[1]+.16*vy], color="#f47b15", lw=2.7, zorder=4)
    ax.scatter([-e.c, e.c], [0, 0], s=58, color="#21a46c", zorder=6)
    ax.scatter([p[0], q[0]], [p[1], q[1]], s=62, color="#087cc5", zorder=7)
    ax.annotate(r"$F_1$", (-e.c, 0), xytext=(-14, -18),
                textcoords="offset points", fontsize=14, color="#5b1230")
    ax.annotate(r"$F_2$", (e.c, 0), xytext=(-26, 8),
                textcoords="offset points", fontsize=14, color="#5b1230")
    ax.annotate(r"$P$", p, xytext=(8, -24),
                textcoords="offset points", fontsize=15, color="#5b1230")
    ax.annotate(r"$Q$", q, xytext=(23, 22),
                textcoords="offset points", fontsize=15, color="#5b1230")
    fig.canvas.draw()
    transform = ax.transData
    ux = transform.transform((1, 0))[0]-transform.transform((0, 0))[0]
    uy = transform.transform((0, 1))[1]-transform.transform((0, 0))[1]
    if abs(ux-uy) > 1e-7:
        raise ArithmeticError("non-isometric diagram")
    bounds = []
    renderer = fig.canvas.get_renderer()
    paths = [np.column_stack((e.a*np.cos(t), e.b*np.sin(t))),
             np.column_stack((np.linspace(-3.4, 3.4, 401), np.zeros(401))),
             np.column_stack((np.zeros(401), np.linspace(-2.35, 2.35, 401)))]
    if k is None:
        paths.append(np.column_stack((np.full(401, e.c),
                                      np.linspace(-2.23, 2.23, 401))))
    else:
        paths.append(np.column_stack((np.linspace(p[0]-.16*vx, q[0]+.16*vx, 401),
                                      np.linspace(p[1]-.16*vy, q[1]+.16*vy, 401))))
    pixel_paths = [transform.transform(path) for path in paths]
    for artist in ax.texts:
        box = artist.get_window_extent(renderer)
        if box.x0 < 0 or box.y0 < 0 or box.x1 > 600 or box.y1 > 390:
            raise ValueError(f"clipped label: {artist.get_text()}")
        for path_index, path in enumerate(pixel_paths):
            crossing = ((path[:, 0] > box.x0 + 2) & (path[:, 0] < box.x1 - 2) &
                        (path[:, 1] > box.y0 + 2) & (path[:, 1] < box.y1 - 2))
            if crossing.any():
                raise ValueError(f"line crosses label: {kind}: {artist.get_text()} path={path_index}")
        for prior in bounds:
            if box.overlaps(prior):
                raise ValueError(f"overlapping labels: {artist.get_text()}")
        bounds.append(box)
    svg = directory / f"{kind}.svg"
    png = directory / f"{kind}.png"
    fig.savefig(svg, transparent=True, metadata={"Date": None})
    fig.savefig(png, transparent=True, dpi=120)
    plt.close(fig)
    with Image.open(png) as im:
        clean = im.convert("RGBA")
    clean.save(png, optimize=True)
    return {"kind": kind, "a": e.a, "b": e.b, "c": e.c, "k": k,
            "P": p, "Q": q, "F": e.focus(), "distance": check["distance"],
            "formula": check["formula"], "unit_scale_px": ux,
            "label_count": len(bounds), "png": str(png), "svg": str(svg)}
