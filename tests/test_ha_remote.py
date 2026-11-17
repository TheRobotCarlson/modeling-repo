"""ha-remote: nothing inside either remote collides, and every stem clears its switch."""

import importlib
import sys

import pytest

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "ha-remote" / "cad"))

# Intended contact: self-tapping screws cut into their bosses, and the TPU grip
# strips pinch the kit by a few hundredths of a millimetre.
ALLOWED = {("shell", "screws"), ("wio", "grip")}


@pytest.mark.parametrize("name", ["puck", "bar"])
def test_parts_do_not_collide(name):
    p = importlib.import_module(name).build()
    keys = list(p)
    hits = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            common = p[a] & p[b]
            vol = common.volume if common is not None else 0
            if vol > 0.05 and (a, b) not in ALLOWED:
                hits.append((a, b, round(vol, 2)))
    assert hits == []


@pytest.mark.parametrize("name, caps", [("puck", ["cap"]), ("bar", ["cap-main", "cap-1", "cap-2", "cap-3", "cap-4"])])
def test_stems_rest_just_above_switches(name, caps):
    m = importlib.import_module(name)
    p = m.build()
    switch = p["switch" if name == "puck" else "switches"]
    top = switch.bounding_box().max.Z
    for c in caps:
        gap = p[c].bounding_box().min.Z - top
        assert gap == pytest.approx(m.SW_GAP, abs=1e-6), c


# Each wire must touch what it connects: a gap here means a wire stops short.
ENDS = {
    "wire-red": ["battery", "xiao", "divider"],
    "wire-black": ["battery", "xiao", "divider"],
    "wire-sense": ["xiao", "divider"],
    "wire-signal": ["xiao"],
}


@pytest.mark.parametrize("name, switch", [("puck", "switch"), ("bar", "switches")])
def test_wires_reach_their_parts(name, switch):
    p = importlib.import_module(name).build()
    ends = {**ENDS, "wire-signal": ["xiao", switch]}
    ends["wire-black"] = ends["wire-black"] + [switch]
    for w, targets in ends.items():
        for t in targets:
            assert p[w].distance_to(p[t]) < 0.01, (w, t)
