"""Matplotlib vector diagrams from C027's mathematical model."""

from pathlib import Path
from math import pi
import shutil
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .model import Ellipse


BLUE = "#0877e6"
NAVY = "#102b62"
TEAL = "#11ad73"
ORANGE = "#ff9d18"


def make_diagram(kind: str, destination: Path):
    """Save matched transparent SVG and PNG without altering model coordinates."""
    e = Ellipse(3, 2)
    vertical = kind == "latus_rectum"
    k = None if vertical else 1
    p, q = e.intersections(k, 1)
    w, h = (320, 280) if vertical else (500, 365)
    plt.rcParams.update({"svg.fonttype": "path", "svg.hashsalt": "c027-exact",
                         "mathtext.fontset": "cm"})
    fig = plt.figure(figsize=(w/100, h/100), dpi=100, facecolor="none")
    ax = fig.add_axes([.03, .06, .94, .88], facecolor="none")
    ax.set_xlim(-3.75, 3.85)
    ax.set_ylim(-2.6, 2.6)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    t = np.linspace(0, 2*pi, 721)
    ax.fill(e.a*np.cos(t), e.b*np.sin(t), color="#cfefff", alpha=.40, zorder=1)
    ax.plot(e.a*np.cos(t), e.b*np.sin(t), color=NAVY, linewidth=2.4, zorder=3)
    ax.annotate("", (3.65,0), (-3.65,0), arrowprops=dict(arrowstyle="->",
                lw=1.55,color="#243146"), zorder=2)
    ax.annotate("", (0,2.42), (0,-2.45), arrowprops=dict(arrowstyle="->",
                lw=1.55,color="#243146"), zorder=2)
    if vertical:
        ax.plot([e.c,e.c],[-2.42,2.42],color=BLUE,lw=3.2,zorder=4)
    else:
        vx, vy = q[0]-p[0], q[1]-p[1]
        ax.plot([p[0]-.20*vx,q[0]+.20*vx],
                [p[1]-.20*vy,q[1]+.20*vy],color=BLUE,lw=3.2,zorder=4)
    for x, color in ((-e.c,ORANGE),(e.c,ORANGE)):
        ax.scatter([x],[0],s=72,color=color,edgecolors="white",linewidths=.8,zorder=7)
    ax.scatter([0],[0],s=50,color=BLUE,edgecolors="white",linewidths=.7,zorder=7)
    ax.scatter([p[0],q[0]],[p[1],q[1]],s=85,color=TEAL,
               edgecolors="white",linewidths=.8,zorder=8)
    labelkw={"fontsize":18,"color":NAVY,"zorder":10}
    ax.annotate(r"$F(-c,0)$",(-e.c,0),xytext=(-39,-28),
                textcoords="offset points",**labelkw)
    ax.annotate(r"$F(c,0)$",(e.c,0),
                xytext=(10,-31) if vertical else (-3,-28),
                textcoords="offset points",
                fontsize=15 if vertical else 18,color=NAVY,zorder=10)
    ax.annotate(r"$O$",(0,0),xytext=(-18,-22),textcoords="offset points",**labelkw)
    ax.annotate(r"$P$",p,xytext=(-16,-23),textcoords="offset points",**labelkw)
    ax.annotate(r"$Q$",q,xytext=(11,4),textcoords="offset points",**labelkw)
    if vertical:
        ax.text(1.70,2.12,r"$x=\sqrt{5}$",fontsize=14,color=BLUE)
    elif kind == "main":
        ax.text(1.41,2.15,r"$y=k(x-c)$",fontsize=15,color=BLUE)
    else:
        ax.text(1.41,2.15,r"$y=x-\sqrt{5}$",fontsize=15,color=BLUE)
    ax.text(3.33,-.34,r"$x$",fontsize=20,color=NAVY)
    ax.text(.12,2.38,r"$y$",fontsize=20,color=NAVY)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    labels=[(artist.get_text(),artist.get_window_extent(renderer))
            for artist in ax.texts if artist.get_text()]
    for i,(name,box) in enumerate(labels):
        if box.x0<1 or box.y0<1 or box.x1>w-1 or box.y1>h-1:
            raise ValueError(f"geometry label outside canvas: {kind}: {name}")
        for other,otherbox in labels[i+1:]:
            if box.overlaps(otherbox):
                raise ValueError(f"geometry labels overlap: {kind}: {name}/{other}")
    trans=ax.transData
    dx=trans.transform((1,0))[0]-trans.transform((0,0))[0]
    dy=trans.transform((0,1))[1]-trans.transform((0,0))[1]
    if abs(dx-dy)>1e-7:
        raise ArithmeticError("diagram does not have equal x/y scale")
    destination.mkdir(parents=True,exist_ok=True)
    svg=destination/(kind+".svg")
    png=destination/(kind+".png")
    fig.savefig(svg,format="svg",transparent=True,metadata={"Date":None})
    plt.close(fig)
    magick=shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick is required to rasterize the exact SVG")
    subprocess.run([magick,"-background","none","-density","100",str(svg),
                    "PNG32:"+str(png)],check=True,capture_output=True,text=True)
    # ImageMagick adds wall-clock PNG metadata. Re-encode unchanged RGBA pixels
    # without ancillary chunks so identical builds have identical bytes.
    with Image.open(png) as raster:
        clean=raster.convert("RGBA")
    clean.save(png,optimize=True)
    return {"svg":str(svg),"png":str(png),"size":[w,h],
            "unit_scale_px":dx,"focus":e.focus(1),"P":p,"Q":q,
            "line":"x=c" if vertical else "y=x-c",
            "label_overlap_count":0,"label_count":len(labels)}
