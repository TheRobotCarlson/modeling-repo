"""berry-dicer: parts clear each other at rest and through their travel."""

import importlib
import math
import sys

import pytest
from build123d import Pos, Rot

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "berry-dicer" / "cad"))

P = importlib.import_module("_steel")
# Intended contact: berries rest on the grid and tray; parts that sit on each other.
REST = {"berries"}


def hits(p, only=None, skip=()):
    keys = [k for k in p if k not in skip]
    out = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if only and a not in only and b not in only:
                continue
            c = p[a] & p[b]
            v = c.volume if c is not None else 0
            if v > 0.05:
                out.append((a, b, round(v, 2)))
    return out


@pytest.mark.parametrize("name", ["press", "topper", "auto"])
def test_nothing_collides_at_rest(name):
    p = importlib.import_module(name).build()
    assert hits(p) == []


def test_cube_size_is_step_grid_height_and_cell():
    """Each push of one step moves exactly one grid height through: cubes, not slabs."""
    g = P.grid().bounding_box()
    assert g.max.Z - g.min.Z == pytest.approx(P.CELL)
    press = importlib.import_module("press")
    assert 2 * math.pi * press.PINION_R / 8 == pytest.approx(P.CELL)


def test_wire_runs_just_under_the_grid():
    _, w = P.wire_bow(0)
    gap = P.grid().bounding_box().min.Z - w.bounding_box().max.Z
    assert 0.1 < gap < 1.0


@pytest.mark.parametrize("name", ["press", "auto"])
@pytest.mark.parametrize("bow_y", [P.Y_SWEEP[0], 0.0, P.Y_SWEEP[1]])
def test_platen_bottoms_on_the_grid_and_the_bow_sweeps_clear(name, bow_y):
    m = importlib.import_module(name)
    p = m.build(platen_z=P.Z_GTOP, bow_y=bow_y)
    assert hits(p, only={"platen", "bow", "wire", "stem", "posts", "crosshead", "rod"}, skip=REST) == []
    assert p["platen"].bounding_box().min.Z == pytest.approx(P.Z_GTOP)


def test_topper_wire_goes_through_the_slot():
    t = importlib.import_module("topper")
    _, _, slot_y = P.tray(t.Y_FENCE, t.Z_BED, -1)
    a0 = math.degrees(math.atan2(t.PIVOT[1] - t.Z_BED, t.PIVOT[0] - slot_y))
    for deg in (t.UP_DEG, 0.0, -a0, -(a0 + 2)):
        p = t.build(deg)
        assert hits(p, only={"wire", "arm"}, skip=REST) == [], deg
    p = t.build(t.UP_DEG)
    top = p["berries"].bounding_box().max.Z
    assert p["wire"].bounding_box().min.Z > top                 # starts above every berry


def test_tray_tips_under_the_parked_platen():
    a = importlib.import_module("auto")
    p = a.build()
    y, z = a.TILT
    for deg in (45, 90, 135):
        tip = Pos(0, y, z) * Rot(deg, 0, 0) * Pos(0, -y, -z)
        moved = {"tray": tip * p["tray"], "flap": tip * p["flap"]}
        for k in ("platen", "hopper", "frame", "tarm", "twire", "crosshead", "posts"):
            for m_ in moved:
                c = moved[m_] & p[k]
                assert c is None or c.volume < 0.05, (deg, m_, k)
