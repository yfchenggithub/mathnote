"""Deterministic, renderer-measured label placement for static math diagrams.

Coordinates supplied to this module are mathematical coordinates.  Collision
tests use the figure's final display pixels (the Agg renderer at export DPI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot, isfinite

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
    max_anchor_distance: float = 64
    allow_leader: bool = False
    max_leader_distance: float = 90
    leader_artist: object | None = field(default=None, repr=False)
    artist: object | None = field(default=None, repr=False)
    attempted: list[dict] = field(default_factory=list, repr=False)


@dataclass
class PointLabel(MathLabel):
    kind: str = "point"
    max_anchor_distance: float = 42


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


class LayoutFailure(CollisionFailure):
    def __init__(self, report):
        self.report = report
        RuntimeError.__init__(self, f"LAYOUT_FAIL: {report['uid']} {report['card']} "
                              f"{report['label']} — {report.get('reason', 'association failure')}")


def _expand(box, amount):
    return Bbox.from_extents(box.x0 - amount, box.y0 - amount,
                             box.x1 + amount, box.y1 + amount)


def _point_rect_distance(x, y, box):
    return hypot(max(box.x0 - x, 0, x - box.x1),
                 max(box.y0 - y, 0, y - box.y1))


def _point_segment_distance(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    length2 = vx * vx + vy * vy
    if length2 == 0:
        return hypot(p[0] - a[0], p[1] - a[1])
    t = max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / length2))
    return hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)


def _segments_distance(a, b, c, d):
    def cross(u, v):
        return u[0] * v[1] - u[1] * v[0]
    ab, cd, ac = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1]), (c[0] - a[0], c[1] - a[1])
    den = cross(ab, cd)
    if abs(den) > 1e-12:
        t, u = cross(ac, cd) / den, cross(ac, ab) / den
        if 0 <= t <= 1 and 0 <= u <= 1:
            return 0.0
    return min(_point_segment_distance(a, c, d), _point_segment_distance(b, c, d),
               _point_segment_distance(c, a, b), _point_segment_distance(d, a, b))


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
        self.exemptions = {}

    def add(self, label: MathLabel):
        if not label.object_name or not all(isfinite(v) for v in label.anchor):
            raise ValueError("label requires a real mathematical object and finite anchor")
        if label.endpoint is None and label.kind == "segment":
            raise ValueError("segment label requires endpoint")
        self.labels.append(label)
        return label

    def exempt_text(self, artist, reason: str, *, exceptions=()):
        if not reason.strip():
            raise ValueError("text exemption requires a reason")
        self.exemptions[artist] = (reason, frozenset(exceptions))

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
            for gap in (16, 26, 38, 52):
                for direction in label.candidates or self.POINT_DIRECTIONS:
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

    def _association(self, label, box, lines, points):
        ax = self.canvas.ax
        anchor = ax.transData.transform(self.frame.xy(*label.anchor))
        if label.kind == "segment":
            end = ax.transData.transform(self.frame.xy(*label.endpoint))
            anchor = (anchor + end) / 2
        distance = _point_rect_distance(*anchor, box)
        issues = []
        if distance > label.max_anchor_distance:
            issues.append({"type": "anchor_distance", "distance_px": round(distance, 2),
                           "maximum_px": label.max_anchor_distance})
        if label.kind == "point":
            own_radius = next((radius for name, _, radius in points
                               if name == label.object_name), 0)
            own_gap = max(0, distance - own_radius)
            for name, stroke, vertices in lines:
                if name in label.exceptions:
                    continue
                anchor_to_path = min((_point_segment_distance(anchor, a, b)
                                      for a, b in zip(vertices[:-1], vertices[1:])),
                                     default=float("inf"))
                if anchor_to_path <= stroke + 8:
                    continue  # A curve/edge through the point is part of its context.
                gap = min((_segment_rect_distance(a, b, box)
                           for a, b in zip(vertices[:-1], vertices[1:])),
                          default=float("inf")) - stroke
                if gap + 4 < own_gap:
                    issues.append({"type": "wrong_object", "object": name,
                                   "object_gap_px": round(gap, 2),
                                   "anchor_gap_px": round(own_gap, 2)})
                    break
            for name, center, radius in points:
                if name == label.object_name or name in label.exceptions:
                    continue
                if hypot(center[0] - anchor[0], center[1] - anchor[1]) <= radius + 4:
                    continue
                gap = _point_rect_distance(*center, box) - radius
                if gap + 4 < own_gap:
                    issues.append({"type": "wrong_object", "object": name,
                                   "object_gap_px": round(gap, 2),
                                   "anchor_gap_px": round(own_gap, 2)})
                    break
        elif label.kind == "segment":
            targets = [(stroke, vertices) for name, stroke, vertices in lines
                       if name == label.object_name]
            if targets:
                own_gap = min(min((_segment_rect_distance(a, b, box)
                                   for a, b in zip(vertices[:-1], vertices[1:])),
                                  default=float("inf")) - stroke
                              for stroke, vertices in targets)
                for name, stroke, vertices in lines:
                    if name == label.object_name or name in label.exceptions:
                        continue
                    gap = min((_segment_rect_distance(a, b, box)
                               for a, b in zip(vertices[:-1], vertices[1:])),
                              default=float("inf")) - stroke
                    if gap + 4 < own_gap:
                        issues.append({"type": "wrong_object", "object": name,
                                       "object_gap_px": round(gap, 2),
                                       "target_gap_px": round(own_gap, 2)})
                        break
        return round(float(distance), 2), issues

    def _leader(self, label, box, lines, points, renderer):
        anchor = self.canvas.ax.transData.transform(self.frame.xy(*label.anchor))
        target = (max(box.x0, min(anchor[0], box.x1)),
                  max(box.y0, min(anchor[1], box.y1)))
        dx, dy = target[0] - anchor[0], target[1] - anchor[1]
        length = hypot(dx, dy)
        if length < 16 or length > label.max_leader_distance:
            return None, [{"object": "anchor", "type": "leader_length"}]
        ux, uy = dx / length, dy / length
        own_radius = next((radius for name, _, radius in points
                           if name == label.object_name), 6)
        start = (anchor[0] + ux * (own_radius + 3), anchor[1] + uy * (own_radius + 3))
        end = (target[0] - ux * 4, target[1] - uy * 4)
        if hypot(end[0] - start[0], end[1] - start[1]) < 6:
            return None, [{"object": "anchor", "type": "leader_length"}]
        hits = []
        for name, stroke, vertices in lines:
            if name in label.exceptions:
                continue
            gap = min((_segments_distance(start, end, a, b)
                       for a, b in zip(vertices[:-1], vertices[1:])), default=float("inf"))
            if gap < stroke + 5:
                hits.append({"object": name, "type": "leader_path", "clearance_px": round(gap - stroke, 2)})
        for name, center, radius in points:
            if name == label.object_name or name in label.exceptions:
                continue
            gap = _point_segment_distance(center, start, end) - radius
            if gap < 5:
                hits.append({"object": name, "type": "leader_point", "clearance_px": round(gap, 2)})
        for other in self.canvas.ax.texts:
            if other is label.artist or not other.get_visible():
                continue
            if _segment_rect_distance(start, end, other.get_window_extent(renderer)) < 5:
                hits.append({"object": other.get_text(), "type": "leader_label", "clearance_px": 0})
        return (start, end), hits

    def _draw_leader(self, label, segment):
        a, b = self.canvas.ax.transData.inverted().transform(segment)
        name = f"leader:{label.object_name}"
        label.leader_artist = self.canvas.line(*a, *b, label.color, 1.5, name=name)
        label.exceptions = label.exceptions | {name}

    def resolve(self):
        self.canvas.fig.canvas.draw()
        renderer = self.canvas.fig.canvas.get_renderer()
        lines, points = self._geometry()
        for label in sorted(self.labels, key=lambda item: -item.priority):
            label.artist = self.canvas.math(label.content, 0, 0, label.size, label.color, ha="center")
            last_hits = []
            leader_fallback = None
            association_rejections = []
            for candidate in self._candidate_positions(label):
                box = self._move(label, candidate, renderer)
                hits = self._collisions(label, box, lines, points, renderer)
                anchor_distance, association = self._association(label, box, lines, points)
                attempt = {"candidate": candidate[0], "distance_px": candidate[3],
                           "bbox_px": [round(float(v), 2) for v in box.extents],
                           "anchor_distance_px": anchor_distance,
                           "collisions": hits, "association": association}
                label.attempted.append(attempt)
                last_hits = hits
                if not hits and not association:
                    label.artist.set_visible(True)
                    nearest, actual = self._nearest_clearance(label, box, lines, points, renderer)
                    self.report.append({"uid": self.uid, "card": self.card, "label": label.content,
                                        "object": label.object_name, "kind": label.kind,
                                        "bbox_px": attempt["bbox_px"],
                                        "candidate": candidate[0], "distance_px": candidate[3],
                                        "anchor_distance_px": anchor_distance,
                                        "maximum_anchor_distance_px": label.max_anchor_distance,
                                        "leader": None,
                                        "minimum_required_px": label.clearance,
                                        "nearest_object": nearest,
                                        "actual_clearance_px": actual,
                                        "attempted": label.attempted, "status": "PASS"})
                    break
                if not hits and association:
                    association_rejections.append(association)
                    if (label.kind == "point" and label.allow_leader and
                            anchor_distance <= label.max_leader_distance and leader_fallback is None):
                        segment, leader_hits = self._leader(label, box, lines, points, renderer)
                        attempt["leader_collisions"] = leader_hits
                        if segment and not leader_hits:
                            leader_fallback = (candidate, segment, attempt)
            else:
                if leader_fallback:
                    candidate, segment, attempt = leader_fallback
                    box = self._move(label, candidate, renderer)
                    self._draw_leader(label, segment)
                    lines, points = self._geometry()
                    nearest, actual = self._nearest_clearance(label, box, lines, points, renderer)
                    self.report.append({"uid": self.uid, "card": self.card, "label": label.content,
                                        "object": label.object_name, "kind": label.kind,
                                        "bbox_px": attempt["bbox_px"], "candidate": candidate[0],
                                        "distance_px": candidate[3],
                                        "anchor_distance_px": attempt["anchor_distance_px"],
                                        "maximum_anchor_distance_px": label.max_anchor_distance,
                                        "leader": [[round(float(v), 2) for v in point]
                                                   for point in segment],
                                        "minimum_required_px": label.clearance,
                                        "nearest_object": nearest,
                                        "actual_clearance_px": actual,
                                        "attempted": label.attempted, "status": "PASS"})
                else:
                    label.artist.remove()
                    status = "LAYOUT_FAIL" if association_rejections else "COLLISION_FAIL"
                    failure = {"uid": self.uid, "card": self.card, "label": label.content,
                               "object": label.object_name, "kind": label.kind,
                               "collisions": last_hits, "association": association_rejections,
                               "attempted": label.attempted, "status": status,
                               "reason": "no candidate preserves object association" if association_rejections
                                         else "all candidate positions collide"}
                    self.report.append(failure)
                    raise LayoutFailure(failure) if association_rejections else CollisionFailure(failure)
        self.audit()
        self.canvas.layout_report = self.report
        self.canvas.label_layout = self
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
            anchor_distance, association = self._association(label, box, lines, points)
            if association and label.leader_artist is None:
                failure = {"uid": self.uid, "card": self.card, "label": label.content,
                           "object": label.object_name, "bbox_px": [round(float(v), 2) for v in box.extents],
                           "anchor_distance_px": anchor_distance, "association": association,
                           "attempted": label.attempted, "status": "LAYOUT_FAIL",
                           "reason": "final label does not clearly identify its object"}
                raise LayoutFailure(failure)
            if label.leader_artist is not None:
                segment, leader_hits = self._leader(label, box, lines, points, renderer)
                if segment is None or leader_hits:
                    failure = {"uid": self.uid, "card": self.card, "label": label.content,
                               "object": label.object_name, "collisions": leader_hits,
                               "attempted": label.attempted, "status": "LAYOUT_FAIL",
                               "reason": "leader line is no longer safe"}
                    raise LayoutFailure(failure)

    def coverage(self):
        """Enumerate every visible text artist; gate all text touching the plot."""
        self.canvas.fig.canvas.draw()
        renderer = self.canvas.fig.canvas.get_renderer()
        lines, points = self._geometry()
        p0, p1 = self.canvas.ax.transData.transform(
            ((self.bounds[0], self.bounds[1]), (self.bounds[2], self.bounds[3])))
        panel = Bbox.from_extents(min(p0[0], p1[0]), min(p0[1], p1[1]),
                                  max(p0[0], p1[0]), max(p0[1], p1[1]))
        registered = {label.artist: label for label in self.labels}
        entries = []
        for artist in self.canvas.ax.texts:
            if not artist.get_visible():
                continue
            box = artist.get_window_extent(renderer)
            in_plot = box.overlaps(panel)
            label = registered.get(artist)
            exemption = self.exemptions.get(artist)
            checks = label or MathLabel(artist.get_text(), "unregistered text", (0, 0),
                                        clearance=4,
                                        exceptions=exemption[1] if exemption else frozenset())
            checks.artist = artist
            hits = self._collisions(checks, box, lines, points, renderer) if in_plot else []
            entries.append({"text": artist.get_text(),
                            "bbox_px": [round(float(v), 2) for v in box.extents],
                            "zone": "plot" if in_plot else "outside_plot",
                            "registered": label is not None,
                            "object": label.object_name if label else None,
                            "exemption": exemption[0] if exemption else None,
                            "collisions": hits})
        self.canvas.text_coverage_report = entries
        collisions = [item for item in entries if item["zone"] == "plot" and item["collisions"]]
        if collisions:
            first = collisions[0]
            raise CollisionFailure({"uid": self.uid, "card": self.card,
                                    "label": first["text"], "collisions": first["collisions"],
                                    "bbox_px": first["bbox_px"], "text_coverage": entries,
                                    "attempted": [], "status": "COLLISION_FAIL"})
        uncovered = [item for item in entries if item["zone"] == "plot" and
                     not item["registered"] and not item["exemption"]]
        if uncovered:
            raise LayoutFailure({"uid": self.uid, "card": self.card,
                                 "label": uncovered[0]["text"], "reason": "unregistered plot text",
                                 "uncovered_text": uncovered, "text_coverage": entries,
                                 "attempted": [], "status": "LAYOUT_FAIL"})
        return entries

    def finalize(self):
        self.audit()
        return self.coverage()


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
