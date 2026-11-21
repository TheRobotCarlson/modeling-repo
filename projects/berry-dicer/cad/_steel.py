"""Shared stainless parts: everything the fruit touches.

Every food-contact part is laser-cut 304 stainless (SendCutSend sheet sizes), bent
where noted, or stainless wire. Printed PLA never touches the food. All of it lifts
out and goes in the dishwasher.

Millimetres, Z up, X across the machine, Y front (-) to back (+).

The dicer: berries, leaves pinched off by hand, sit any way up in a hopper over a grid of
sharpened strips. A platen pushes them down in 12 mm steps. After each step a wire
sweeps under the grid and cuts off what came through, so every piece is a 12 mm
cube except the tips and edges. Step, grid height and cell all equal CELL.
"""

from build123d import Align, Box, Cylinder, Pos, Rot

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# Sheet thicknesses SendCutSend cuts in 304 (SOURCE: sendcutsend.com/stainless-steel)
T030, T048, T060, T125 = 0.762, 1.219, 1.524, 3.175

# --- dicer cartridge: hopper with the grid in its bottom ----------------------------
CELL = 12.0                        # cube size: grid pitch, strip height and step
NX, NY = 26, 13                    # cells across and front to back
IN_X, IN_Y = NX * CELL, NY * CELL  # 312 x 156 inside the hopper
STRIP_T = T030                     # grid strips, top edge sharpened
HOP_H = 60.0                       # hopper wall above the grid
HOP_T = T048
FLANGE = 30.0                      # the hopper's top edge is bent out and rests on the frame
Z_GRID = 120.0                     # bottom of the grid (and of the hopper)
Z_GTOP = Z_GRID + CELL             # top of the grid: where the berries stand
Z_HTOP = Z_GTOP + HOP_H            # top of the hopper, where its flange sits

WIRE_D = 0.5                       # cutting wire, 304 stainless (EST: cheese-wire gauge)
Z_WIRE = Z_GRID - 0.6              # the wire's centre, just under the strips
BOW_W = IN_X + 2 * 30.0            # wire bow: a flat U of 3 mm 304, wire across its tips
BOW_H = 34.0
BOW_RAIL_X = BOW_W / 2 - 6.0       # where the bow's arms run in the frame's slots
Y_SWEEP = (-(IN_Y / 2 + 14.0), IN_Y / 2 + 14.0)     # wire parked clear of the grid at either end

PLATEN_CLR = 1.5                   # gap all round between platen and hopper
HULL = 2.0                         # what pinching the leaves off takes from the length (EST)
PLATEN_LIP = 15.0                  # the platen's edges are bent up 15 mm to stiffen it


def hopper():
    """Four walls, bent from one blank, with the top edge flanged outward."""
    ox, oy = IN_X / 2 + HOP_T, IN_Y / 2 + HOP_T
    walls = Pos(0, 0, Z_GRID) * Box(2 * ox, 2 * oy, CELL + HOP_H, align=BASE)
    walls -= Pos(0, 0, Z_GRID - 1) * Box(IN_X, IN_Y, CELL + HOP_H + 2, align=BASE)
    flange = Pos(0, 0, Z_HTOP - HOP_T) * Box(2 * (ox + FLANGE), 2 * (oy + FLANGE), HOP_T, align=BASE)
    flange -= Pos(0, 0, Z_HTOP - HOP_T - 1) * Box(2 * ox, 2 * oy, HOP_T + 2, align=BASE)
    return walls + flange


def grid():
    """Egg-crate of slotted strips: 12 running across, 25 front to back.

    The slots are not modelled; the strips are shown crossing. Their ends sit in
    slots in the hopper walls (also not modelled).
    """
    g = None
    for k in range(1, NY):
        s = Pos(0, -IN_Y / 2 + k * CELL, Z_GRID) * Box(IN_X, STRIP_T, CELL, align=BASE)
        g = s if g is None else g + s
    for k in range(1, NX):
        g += Pos(-IN_X / 2 + k * CELL, 0, Z_GRID) * Box(STRIP_T, IN_Y, CELL, align=BASE)
    return g


def platen(z_bottom):
    """Bent tray of 1/8 in 304: flat face down, edges up. Bottom face at z_bottom."""
    px, py = IN_X - 2 * PLATEN_CLR, IN_Y - 2 * PLATEN_CLR
    p = Pos(0, 0, z_bottom) * Box(px, py, PLATEN_LIP, align=BASE)
    p -= Pos(0, 0, z_bottom + T125) * Box(px - 2 * T125, py - 2 * T125, PLATEN_LIP, align=BASE)
    return p


def wire_bow(y):
    """Flat U of 3 mm 304 in the XZ plane, with the wire across the tops of its arms.

    The wire sweeps just under the grid; the crossbar passes under it at bowl level.
    """
    t = T125
    arm = 12.0
    b = Pos(0, y, Z_WIRE - BOW_H) * Box(BOW_W, t, 10, align=BASE)
    for sx in (-1, 1):
        b += Pos(sx * (BOW_W / 2 - arm / 2), y, Z_WIRE - BOW_H) * Box(arm, t, BOW_H + 2.5, align=BASE)
    w = Pos(0, y, Z_WIRE) * Rot(0, 90, 0) * Cylinder(WIRE_D / 2, BOW_W - 2 * arm + 0.2)
    return b, w


def stand_berries(z, n=11, seed=5):
    """Hulled berries standing in the hopper, ready to dice."""
    import random

    from build123d import Cone
    rnd = random.Random(seed)
    out = None
    spots = [(-130 + 26 * (i % 11), -40 + 40 * (i // 11)) for i in range(n * 3)]
    rnd.shuffle(spots)
    for x, y in spots[:n]:
        w = rnd.uniform(24, 36)
        h = w * rnd.uniform(1.1, 1.3) - HULL
        c = Pos(x, y, z) * Cone(w / 2, 2.0, h, align=BASE)
        out = c if out is None else out + c
    return out
