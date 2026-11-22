"""Labelled 2D drawings: views with coded dimensions, and a table of every size.

A drawing sits beside the 3D viewer on a page. Each size gets a short code (S1,
R2, T5 ...) so a measurement can be read back by code, and a source (measured,
photo / guess, derived) shown by colour. Build the numbers from the CAD module's
own constants, so the drawing and the model cannot disagree.

    d = Drawing("my-project", "cover")
    v = d.view("From above")
    v.poly(rect(-20, -30, 20, 30), "part")
    v.dim((-20, -34), (20, -34), "S2 40", d.size("S2", "Width, outside", 40, "measured"))
    d.export()            # -> data/my-project/drawing/cover.json, for <Drawing name="cover" />

Model coordinates are mm, y up on the page. Shape classes: part, inner, flat, rib,
tongue (a highlighted feature), guessed, offcut (dashed, not in this cut), cell
(dashed reference object). Colour classes for dimensions: m, g, d, note.
"""

import json
import math

from .paths import data_dir

SOURCES = {"measured": "m", "photo / guess": "g", "derived": "d"}


def ellipse(cx, cy, a, b, a0, a1, n=40):
    """Points on an elliptical arc centred (cx, cy), radii a and b, from angle a0 to a1 (degrees)."""
    return [(cx + a * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + b * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


class View:
    """One SVG view. Grows its own viewBox to fit everything drawn in it."""

    def __init__(self, title, k):
        self.title, self.k, self.out = title, k, []
        self.lo, self.hi = [1e9, 1e9], [-1e9, -1e9]

    def px(self, x, y):
        return x * self.k, -y * self.k

    def _grow(self, x, y):
        self.lo = [min(self.lo[0], x), min(self.lo[1], y)]
        self.hi = [max(self.hi[0], x), max(self.hi[1], y)]

    def poly(self, pts, cls="part", close=True):
        q = [self.px(*p) for p in pts]
        for x, y in q:
            self._grow(x, y)
        tag = "polygon" if close else "polyline"
        self.out.append(f'<{tag} class="{cls}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in q)}"/>')

    def line(self, a, b, cls):
        (x1, y1), (x2, y2) = self.px(*a), self.px(*b)
        self.out.append(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    def guide(self, a, b, c):
        """Thin dashed extension line from a feature to its dimension."""
        self.line(a, b, f"guide {c}")

    def _text(self, x, y, s, cls, anchor):
        w = 6.6 * len(s)
        ax = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
        self._grow(ax, y - 12)
        self._grow(ax + w, y + 4)
        self.out.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{s}</text>')

    def dim(self, a, b, label, c, lab=None):
        """Dimension between two model points, arrows both ends. lab: label offset in px."""
        (x1, y1), (x2, y2) = self.px(*a), self.px(*b)
        self._grow(x1, y1)
        self._grow(x2, y2)
        self.out.append(f'<line class="dim {c}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                        f'marker-start="url(#ar-{c})" marker-end="url(#ar-{c})"/>')
        if not label:
            return
        horiz = abs(y2 - y1) < 1
        if lab is None:
            lab = (0, -6) if horiz else (6, 4)
        anchor = "middle" if horiz and lab[0] == 0 else ("end" if lab[0] < 0 else "start")
        self._text((x1 + x2) / 2 + lab[0], (y1 + y2) / 2 + lab[1], label, f"lbl {c}", anchor)

    def tag(self, p, s, c, dx=0, dy=0, anchor="start"):
        """A label at a model point, offset in px."""
        x, y = self.px(*p)
        self._text(x + dx, y + dy, s, f"lbl {c}", anchor)

    def svg(self, margin=10):
        x0, y0 = self.lo[0] - margin, self.lo[1] - margin
        w, h = self.hi[0] - self.lo[0] + 2 * margin, self.hi[1] - self.lo[1] + 2 * margin
        return dict(title=self.title, viewBox=f"{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}", width=round(w),
                    body="\n".join(self.out))


class Drawing:
    def __init__(self, project, name, scale=8.0):
        self.project, self.name, self.k = project, name, scale
        self.views, self.sizes = [], {}

    def view(self, title):
        v = View(title, self.k)
        self.views.append(v)
        return v

    def size(self, code, what, mm, source):
        """Record a size for the table; returns its colour class for the dimension."""
        if code in self.sizes:
            raise ValueError(f"size code {code} used twice")
        self.sizes[code] = dict(code=code, what=what, mm=round(mm, 2) if isinstance(mm, float) else mm,
                                source=source)
        return SOURCES[source]

    def export(self, order=""):
        """order: code prefixes in table order, e.g. "SCRT"; others follow alphabetically."""
        def key(s):
            head = s["code"].rstrip("0123456789")
            return (order.index(head) if head in order else len(order), head, int(s["code"][len(head):] or 0))
        rows = sorted(self.sizes.values(), key=key)
        out = data_dir(self.project, "drawing")
        (out / f"{self.name}.json").write_text(json.dumps(
            dict(views=[v.svg() for v in self.views], sizes=rows), indent=1))
