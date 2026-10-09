"""Deterministic, renderer-measured label placement for static math diagrams.

Coordinates supplied to this module are mathematical coordinates.  Collision
tests use the figure's final display pixels (the Agg renderer at export DPI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot

from matplotlib.patches import Circle, Rectangle
from matplotlib.transforms import Bbox


@dataclass
class MathLabel:
    content: str
    object_name: str
    anchor: tuple[float, float]
    candidates: tuple[str, ...] = ()
    size: float = 25
    color: str = "#12345b"
    priority: int = 0
    clearance: float = 6
    exceptions: frozenset[str] = frozenset()
    kind: str = "point"
    endpoint: tuple[float, float] | None = None
    artist: object | None = field(default=None, repr=False)
    attempted: list[dict] = field(default_factory=list, repr=False)


@dataclass
class PointLabel(MathLabel):
    kind: str = "point"


@dataclass
class SegmentLabel(MathLabel):
    kind: str = "segment"


@dataclass
class CurveLabel(MathLabel):
    kind: str = "curve"


@dataclass
class LineLabel(MathLabel):
    kind: str = "line"


class CollisionFailure(RuntimeError):
    def __init__(self, report):
        self.report = report
        super().__init__(f"COLLISION_FAIL: {report['uid']} {report['card']} "
                         f"{report['label']} vs {report['collisions']}")


def _expand(box, amount):
    return Bbox.from_extents(box.x0 - amount, box.y0 - amount,
                             box.x1 + amount, box.y1 + amount)


def _point_rect_distance(x, y, box):
    return hypot(max(box.x0 - x, 0, x - box.x1),
                 max(box.y0 - y, 0, y - box.y1))


def _segment_rect_distance(a, b, box):
    # Segment clipping against an axis-aligned rectangle, then distances to
    # its four edges. This avoids treating a curved path's large bbox as ink.
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, a[0] - box.x0), (dx, box.x1 - a[0]),
                 (-dy, a[1] - box.y0), (dy, box.y1 - a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                break
        else:
            t = q / p
            if p < 0:
                lo = max(lo, t)
            else:
                hi = min(hi, t)
    else:
        if lo <= hi:
            return 0.0
    corners = ((box.x0, box.y0), (box.x0, box.y1),
               (box.x1, box.y0), (box.x1, box.y1))

    def point_segment(p, u, v):
        vx, vy = v[0] - u[0], v[1] - u[1]
        t = max(0, min(1, ((p[0] - u[0]) * vx + (p[1] - u[1]) * vy) /
                            (vx * vx + vy * vy)))
        return hypot(p[0] - u[0] - t * vx, p[1] - u[1] - t * vy)

    edges = ((corners[0], corners[1]), (corners[1], corners[3]),
             (corners[3], corners[2]), (corners[2], corners[0]))
    return min(_point_rect_distance(*a, box), _point_rect_distance(*b, box),
               *(point_segment(c, a, b) for c in corners),
               *(point_segment(a, u, v) for u, v in edges),
               *(point_segment(b, u, v) for u, v in edges))


class LabelLayout:
    """Register semantic labels, place by priority, then audit every label."""

    POINT_DIRECTIONS = ("NE", "SE", "NW", "SW", "E", "W", "N", "S")

    def __init__(self, canvas, frame, bounds, *, uid=None, card=None):
        self.canvas, self.frame = canvas, frame
        self.bounds = bounds  # x0, y0, x1, y1 in card pixels
        self.uid = uid or canvas.uid
        self.card = card or canvas.number
        self.labels = []
        self.report = []

    def add(self, label: MathLabel):
        if label.endpoint is None and label.kind == "segment":
            raise ValueError("segment label requires endpoint")
        self.labels.append(label)
        return label

    def _geometry(self):
        ax = self.canvas.ax
        lines = []
        points = []
        for index, line in enumerate(ax.lines):
            if not line.get_visible():
                continue
            vertices = line.get_path().transformed(line.get_transform()).vertices
            if line.get_marker() not in (None, "None", "") and len(vertices) == 1:
                points.append((getattr(line, "_mathnote_name", None) or f"marker[{index}]", vertices[0],
                               line.get_markersize() * self.canvas.fig.dpi / 144 +
                               line.get_markeredgewidth() * self.canvas.fig.dpi / 144))
            if len(vertices) >= 2:
                lines.append((getattr(line, "_mathnote_name", None) or f"line[{index}]", line.get_linewidth() *
                              self.canvas.fig.dpi / 72 / 2, vertices))
        for index, patch in enumerate(ax.patches):
            if isinstance(patch, Circle) and patch.get_visible():
                center = ax.transData.transform(patch.center)
                radius = patch.radius * ax.transData.get_matrix()[0, 0]
                points.append((getattr(patch, "_mathnote_name", None) or f"point[{index}]", center, abs(radius) +
                               patch.get_linewidth() * self.canvas.fig.dpi / 144))
        return lines, points

    def _candidate_positions(self, label):
        x, y = self.canvas.ax.transData.transform(self.frame.xy(*label.anchor))
        if label.kind == "point":
            for direction in label.candidates or self.POINT_DIRECTIONS:
                for gap in (16, 26, 38, 52):
                    yield direction, x, y, gap
        elif label.kind == "segment":
            ex, ey = self.canvas.ax.transData.transform(self.frame.xy(*label.endpoint))
            vx, vy = ex - x, ey - y
            length = hypot(vx, vy)
            if length == 0:
                raise ValueError("zero length segment")
            nx, ny = -vy / length, vx / length
            for distance in (20, 30, 42, 56, 72):
                for side in (1, -1):
                    yield f"normal{'+' if side == 1 else '-'}", (x + ex) / 2 + side * distance * nx, (y + ey) / 2 + side * distance * ny, distance
        else:
            for direction in label.candidates or self.POINT_DIRECTIONS:
                for gap in (12, 24, 36, 48, 64):
                    yield direction, x, y, gap

    def _move(self, label, candidate, renderer):
        direction, x, y, gap = candidate
        artist = label.artist
        # Build around the true renderer-measured text size, including MathText.
        artist.set_position((x, y))
        box = artist.get_window_extent(renderer)
        w, h = box.width, box.height
        if direction.startswith("normal"):
            cx, cy = x, y
        else:
            sx = (1 if "E" in direction else -1 if "W" in direction else 0)
            sy = (1 if "N" in direction else -1 if "S" in direction else 0)
            cx = x + sx * (gap + w / 2)
            cy = y + sy * (gap + h / 2)
        # ax text coordinates are data coordinates; convert display centre back.
        artist.set_position(self.canvas.ax.transData.inverted().transform((cx, cy)))
        return artist.get_window_extent(renderer)

    def _collisions(self, label, box, lines, points, renderer):
        clearance = label.clearance
        margin = _expand(box, clearance)
        x0, y0, x1, y1 = self.bounds
        panel = self.canvas.ax.transData.transform(((x0, y0), (x1, y1)))
        left, right = sorted((panel[0, 0], panel[1, 0]))
        bottom, top = sorted((panel[0, 1], panel[1, 1]))
        hits = []
        if margin.x0 < left or margin.x1 > right or margin.y0 < bottom or margin.y1 > top:
            hits.append({"object": "plot boundary", "type": "boundary", "clearance_px": 0})
        for name, stroke, vertices in lines:
            if name in label.exceptions:
                continue
            distance = min((_segment_rect_distance(a, b, box)
                            for a, b in zip(vertices[:-1], vertices[1:])), default=float("inf"))
            safe = distance - stroke
            if safe < clearance:
                hits.append({"object": name, "type": "path", "clearance_px": round(safe, 2)})
        for name, center, radius in points:
            if name in label.exceptions:
                continue
            safe = _point_rect_distance(*center, box) - radius
            if safe < clearance:
                hits.append({"object": name, "type": "point", "clearance_px": round(safe, 2)})
        for other in self.canvas.ax.texts:
            if other is label.artist or not other.get_visible():
                continue
            if margin.overlaps(other.get_window_extent(renderer)):
                hits.append({"object": other.get_text(), "type": "label", "clearance_px": 0})
        return hits

    def _nearest_clearance(self, label, box, lines, points, renderer):
        x0, y0, x1, y1 = self.bounds
        panel = self.canvas.ax.transData.transform(((x0, y0), (x1, y1)))
        left, right = sorted((panel[0, 0], panel[1, 0]))
        bottom, top = sorted((panel[0, 1], panel[1, 1]))
        distances = [("plot boundary", min(box.x0 - left, right - box.x1,
                                           box.y0 - bottom, top - box.y1))]
        for name, stroke, vertices in lines:
            if name not in label.exceptions:
                distances.append((name, min((_segment_rect_distance(a, b, box)
                                             for a, b in zip(vertices[:-1], vertices[1:])),
                                            default=float("inf")) - stroke))
        for name, center, radius in points:
            if name not in label.exceptions:
                distances.append((name, _point_rect_distance(*center, box) - radius))
        for other in self.canvas.ax.texts:
            if other is label.artist or not other.get_visible():
                continue
            other_box = other.get_window_extent(renderer)
            dx = max(other_box.x0 - box.x1, box.x0 - other_box.x1, 0)
            dy = max(other_box.y0 - box.y1, box.y0 - other_box.y1, 0)
            distances.append((other.get_text(), hypot(dx, dy)))
        name, distance = min(distances, key=lambda pair: pair[1])
        return name, round(float(distance), 2)

    def resolve(self):
        self.canvas.fig.canvas.draw()
        renderer = self.canvas.fig.canvas.get_renderer()
        lines, points = self._geometry()
        for label in sorted(self.labels, key=lambda item: -item.priority):
            label.artist = self.canvas.math(label.content, 0, 0, label.size, label.color, ha="center")
            last_hits = []
            for candidate in self._candidate_positions(label):
                box = self._move(label, candidate, renderer)
                hits = self._collisions(label, box, lines, points, renderer)
                label.attempted.append({"candidate": candidate[0], "distance_px": candidate[3],
                                        "bbox_px": [round(v, 2) for v in box.extents],
                                        "collisions": hits})
                last_hits = hits
                if not hits:
                    label.artist.set_visible(True)
                    nearest, actual = self._nearest_clearance(label, box, lines, points, renderer)
                    self.report.append({"uid": self.uid, "card": self.card, "label": label.content,
                                        "object": label.object_name, "kind": label.kind,
                                        "bbox_px": label.attempted[-1]["bbox_px"],
                                        "candidate": candidate[0], "distance_px": candidate[3],
                                        "minimum_required_px": label.clearance,
                                        "nearest_object": nearest,
                                        "actual_clearance_px": actual,
                                        "attempted": label.attempted, "status": "PASS"})
                    break
            else:
                label.artist.remove()
                failure = {"uid": self.uid, "card": self.card, "label": label.content,
                           "object": label.object_name, "kind": label.kind,
                           "collisions": last_hits, "attempted": label.attempted,
                           "status": "COLLISION_FAIL"}
                self.report.append(failure)
                raise CollisionFailure(failure)
        self.audit()
        self.canvas.layout_report = self.report
        return self.report

    def audit(self):
        """Recheck final positions after all labels have been placed."""
        self.canvas.fig.canvas.draw()
        renderer = self.canvas.fig.canvas.get_renderer()
        lines, points = self._geometry()
        for label in self.labels:
            if label.artist is None:
                continue
            box = label.artist.get_window_extent(renderer)
            hits = self._collisions(label, box, lines, points, renderer)
            if hits:
                failure = {"uid": self.uid, "card": self.card, "label": label.content,
                           "object": label.object_name, "bbox_px": [round(v, 2) for v in box.extents],
                           "collisions": hits, "attempted": label.attempted,
                           "status": "COLLISION_FAIL"}
                raise CollisionFailure(failure)


def save_debug_preview(canvas, path):
    """Write a preview-only image with measured final label bounding boxes."""
    overlays = []
    for item in canvas.layout_report:
        if item["status"] != "PASS":
            continue
        x0, y0, x1, y1 = item["bbox_px"]
        corners = canvas.ax.transData.inverted().transform(((x0, y0), (x1, y1)))
        rect = Rectangle(corners[0], corners[1, 0] - corners[0, 0],
                         corners[1, 1] - corners[0, 1], fill=False,
                         edgecolor="#e63838", linewidth=1.5, zorder=30)
        canvas.ax.add_patch(rect)
        overlays.append(rect)
    canvas.fig.savefig(path, dpi=100, facecolor=canvas.fig.get_facecolor())
    for rect in overlays:
        rect.remove()
