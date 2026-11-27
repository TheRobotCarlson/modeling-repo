"""blind-motor: everything fits in the box, and the sprocket matches the chain."""

import importlib
import math
import sys

import pytest

from modelkit import paths

sys.path.insert(0, str(paths.PROJECTS / "blind-motor" / "cad"))

B = importlib.import_module("box")


@pytest.fixture(scope="module")
def parts():
    return B.build()


def test_printed_parts_are_valid_solids(parts):
    for k in ("base", "lid", "sprocket"):
        assert parts[k].is_valid, k


def test_bought_parts_fit_without_touching_the_print(parts):
    bought = [parts["motor"], *parts["cells"], *parts["boards"].values()]
    for printed in ("base", "lid", "sprocket"):
        for b in bought:
            assert (b & parts[printed]).volume < 0.01, printed


def test_boards_and_cells_clear_the_motor(parts):
    for b in [*parts["cells"], *parts["boards"].values()]:
        assert (b & parts["motor"]).volume < 0.01


def test_sprocket_pockets_are_one_bead_pitch_apart():
    chord = 2 * B.R_PITCH * math.sin(math.pi / B.TEETH)
    assert chord == pytest.approx(B.BEAD_PITCH)
    assert B.CHAIN_PER_TURN == pytest.approx(72.0)


def test_chain_clears_the_lid_and_rides_in_the_pockets():
    assert B.CHAIN_Y - B.BEAD_D / 2 > B.Y_FRONT + 1.0          # strands pass in front of the lid
    y_core = B.Y_SPROCKET + B.HUB_L + B.FLANGE_T
    assert B.CHAIN_Y == pytest.approx(y_core + B.CORE_W / 2)   # centred between the flanges
    assert B.R_FLANGE - B.R_PITCH > B.BEAD_D / 2 + 1.5          # flanges stand well above the beads


def test_shaft_reaches_through_the_sprocket(parts):
    shaft_end = B.Y_LID + B.SHAFT_L
    engaged = shaft_end - B.Y_SPROCKET
    assert engaged > 0.9 * (B.HUB_L + B.WHEEL_W)
    assert parts["sprocket"].bounding_box().max.Y <= shaft_end + 0.5
