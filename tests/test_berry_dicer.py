"""berry-dicer press: parts clear each other at rest and through their travel."""

import importlib
import math
import sys

import pytest

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "berry-dicer" / "cad"))

P = importlib.import_module("_steel")
# Intended contact: berries rest on the grid; parts that sit on each other.
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


def test_nothing_collides_at_rest():
    p = importlib.import_module("press").build()
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


@pytest.mark.parametrize("bow_y", [P.Y_SWEEP[0], 0.0, P.Y_SWEEP[1]])
def test_platen_bottoms_on_the_grid_and_the_bow_sweeps_clear(bow_y):
    m = importlib.import_module("press")
    p = m.build(platen_z=P.Z_GTOP, bow_y=bow_y)
    assert hits(p, only={"platen", "bow", "wire", "stem", "rod"}, skip=REST) == []
    assert p["platen"].bounding_box().min.Z == pytest.approx(P.Z_GTOP)
