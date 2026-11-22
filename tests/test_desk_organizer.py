"""desk-organizer: every variant fits the desk, items fit their pockets and stand proud."""

import importlib
import sys

import pytest

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "desk-organizer" / "cad"))

O = importlib.import_module("organizer")
G = importlib.import_module("_grid")
BED = 320.0                     # Bambu H3C, 330 x 320 (listings); the short side
NAMES = list(O.VARIANTS)
GRIDDED = [n for n in NAMES if O.VARIANTS[n]["grid"]]


@pytest.fixture(scope="module")
def models():
    return {n: O.build(n) for n in NAMES}


@pytest.mark.parametrize("name", NAMES)
def test_nothing_collides(models, name):
    p, items = models[name]
    shapes = {**p, **{"item " + k: v for k, v in items.items()}}
    keys = list(shapes)
    hits = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            c = shapes[a] & shapes[b]
            if c is not None and c.volume > 0.05:
                hits.append((a, b, round(c.volume, 2)))
    assert hits == []


@pytest.mark.parametrize("name", NAMES)
def test_every_item_is_held(models, name):
    assert set(models[name][1]) == set(O.ITEM_NAMES)


@pytest.mark.parametrize("name", GRIDDED)
def test_modules_tile_the_plate_without_overlap(name):
    v = O.VARIANTS[name]
    gx, gy = v["grid"]
    used = set(v["free"])
    for mod, (size, (i, j), _) in v["modules"].items():
        cells = {(i + a, j + b) for a in range(size[0]) for b in range(size[1])}
        assert all(0 <= x < gx and 0 <= y < gy for x, y in cells), mod
        assert not cells & used, mod
        used |= cells
    assert len(used) == gx * gy


@pytest.mark.parametrize("name", GRIDDED)
def test_bins_are_gridfinity_size(models, name):
    p, _ = models[name]
    for mod, (size, _, _) in O.VARIANTS[name]["modules"].items():
        nx, ny, u = size
        s = p[mod].bounding_box().size
        assert s.X == pytest.approx(nx * G.PITCH - G.GAP, abs=0.01), mod
        assert s.Y == pytest.approx(ny * G.PITCH - G.GAP, abs=0.01), mod
        assert s.Z == pytest.approx(u * G.UNIT, abs=0.01), mod


# Items meant to stand proud of the part they sit in, by at least this much of their height.
PROUD = {"airpods_case": 0.5, "grip_trainer": 0.6, "pen": 0.6, "brush": 0.6, "glasses_case": 0.6,
         "metal_stick": 0.4}


def host(parts, item):
    """The part under the item's centre."""
    c = item.bounding_box().center()
    for k, s in parts.items():
        bb = s.bounding_box()
        if k != "baseplate" and bb.min.X < c.X < bb.max.X and bb.min.Y < c.Y < bb.max.Y:
            return s
    raise AssertionError("no part under the item")


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("item", list(PROUD))
def test_items_stand_proud(models, name, item):
    p, items = models[name]
    bb = items[item].bounding_box()
    out = bb.max.Z - host(p, items[item]).bounding_box().max.Z
    assert out / (bb.max.Z - bb.min.Z) >= PROUD[item]


@pytest.mark.parametrize("name", NAMES)
def test_fits_the_desk_space_and_the_bed(models, name):
    p, _ = models[name]
    for k, v in p.items():
        s = v.bounding_box().size
        assert s.X <= O.DESK[0] and s.Y <= O.DESK[1], k
        assert max(s.X, s.Y) <= BED, k
