"""ac-remote-cover: the model matches the working cover's measurements."""

import importlib
import sys

import pytest

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "ac-remote-cover" / "cad"))

C = importlib.import_module("cover")


@pytest.fixture(scope="module")
def parts():
    return C.build()


def test_outline_matches_the_calipers(parts):
    s = parts["cover"].bounding_box().size
    assert (s.X, s.Y, s.Z) == pytest.approx((C.W, C.L + C.CORNER_OUT, C.H), abs=0.01)


def test_it_is_a_thin_shell(parts):
    assert parts["cover"].volume < 0.2 * C.L * C.W * C.H
    assert parts["cover"].is_valid and parts["tongue"].is_valid


def test_tongue_reaches_out_and_up_as_measured(parts):
    bb = parts["tongue"].bounding_box()
    assert bb.max.Y == pytest.approx(C.L / 2 + C.TONGUE_OUT, abs=0.01)
    assert bb.max.Z == pytest.approx(C.TONGUE_Z + C.TONGUE_PEAK, abs=0.01)


def test_tongue_meets_the_shell_without_overlap(parts):
    c = parts["cover"] & parts["tongue"]
    assert c is None or c.volume < 0.01


def test_cradle_ribs_are_where_measured():
    # a strip down the middle, above the side ribs, holds only the two battery holders (and G1)
    from build123d import Box, Pos
    strip = Pos(0, 0, C.T_FLOOR + C.SIDE_RIB_H + 0.1) * Box(0.2, C.L, C.H, align=C.BASE)
    r = (C.cradle() & strip).bounding_box()
    assert C.L / 2 - r.max.Y == pytest.approx(C.RIB_FRONT - C.RIB_T, abs=0.01)   # R1, to the inside face
    assert r.max.Y - r.min.Y == pytest.approx(C.RIB_SPAN, abs=0.01)              # R2
    assert r.max.Z - C.T_FLOOR == pytest.approx(C.RIB_PEAK, abs=0.01)            # R4


def test_side_ribs_stay_inside_the_shell(parts):
    from build123d import Box, Pos
    past_open_end = Pos(0, C.L / 2 + 10, 0) * Box(C.W, 20, C.H, align=C.BASE)   # where the corner blocks go
    outside = parts["cover"] - C.envelope() - past_open_end
    assert outside is None or outside.volume < 0.01
