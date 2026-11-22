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
    # front rib's inside face, and the outside-to-outside span of the two ribs
    r = C.cradle().bounding_box()
    assert C.L / 2 - r.max.Y == pytest.approx(C.RIB_FRONT - C.RIB_T, abs=0.01)
    assert r.max.Y - r.min.Y == pytest.approx(C.RIB_SPAN, abs=0.01)
    assert r.max.Z - C.T_FLOOR == pytest.approx(C.RIB_PEAK, abs=0.01)
