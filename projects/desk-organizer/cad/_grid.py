"""Gridfinity-compatible baseplate and bins.

Every module is a bin on a 42 mm grid that drops into a baseplate and lifts out,
so a module can be reprinted, moved or swapped without touching the rest, and any
community Gridfinity bin fits the same plate.

Profile values are the Gridfinity spec as commonly implemented (Zack Freedman's
reference files; 42 mm pitch, 7 mm height units, 41.5 mm bins, 4.75 mm foot). Print
a 1 x 1 bin and a 2 x 2 plate corner first to check the fit on your printer.

Millimetres, Z up, X across the desk, Y front (-) to back (+).
"""

import math

from build123d import (Align, Axis, Box, Cylinder, Pos, RectangleRounded, RegularPolygon, Rot, extrude,
                       fillet)

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

PITCH = 42.0                 # grid cell
UNIT = 7.0                   # height unit
GAP = 0.5                    # a bin is n * 42 - 0.5 across
BIN_R = 3.75                 # bin corner radius
FOOT = (0.8, 1.8, 2.15)      # bin foot: 45 deg chamfer, straight, 45 deg chamfer, from the bottom up
FOOT_H = sum(FOOT)           # 4.75: where the bin walls start
PLATE = (0.7, 1.8, 2.15)     # baseplate socket, from the bottom up
PLATE_H = sum(PLATE)         # 4.65
PLATE_R = 4.0
WALL = 1.2                   # thinnest bin wall
FIT = 0.6                    # clearance per side between an item and its pocket


def cell_centre(i, j, nx, ny):
    """Centre of cell (i, j) on a plate nx by ny, plate centred on the origin."""
    return (-nx * PITCH / 2 + PITCH * (i + 0.5), -ny * PITCH / 2 + PITCH * (j + 0.5))


def _stack(bottom_w, bottom_r, steps, z0=0.0):
    """Rounded square growing up through 45 deg and straight steps: (height, chamfered)."""
    w, r, z, out = bottom_w, bottom_r, z0, None
    for h, chamfer in steps:
        s = Pos(0, 0, z) * extrude(RectangleRounded(w, w, r), h, taper=-45 if chamfer else 0)
        out = s if out is None else out + s
        if chamfer:
            w, r = w + 2 * h, r + h
        z += h
    return out


def baseplate(nx, ny):
    """Open-frame baseplate, nx by ny cells, 4.65 mm tall, centred on the origin."""
    plate = extrude(RectangleRounded(nx * PITCH, ny * PITCH, PLATE_R), PLATE_H)
    a, b, c = PLATE
    bottom = PITCH - 2 * (a + c)
    for i in range(nx):
        for j in range(ny):
            x, y = cell_centre(i, j, nx, ny)
            cut = _stack(bottom, PLATE_R - a - c, [(a, True), (b, False), (c, True)])
            cut += Pos(0, 0, PLATE_H) * Box(PITCH, PITCH, 2, align=BASE)
            plate -= Pos(x, y, -0.01) * cut
    return plate


def bin_block(nx, ny, units):
    """Solid bin nx by ny cells, `units` x 7 mm tall, centred on the origin, bottom at z = 0.

    Pockets are cut from it afterwards. No stacking lip: nothing stacks here.
    """
    a, b, c = FOOT
    w = PITCH - GAP
    body = Pos(0, 0, FOOT_H) * extrude(RectangleRounded(nx * PITCH - GAP, ny * PITCH - GAP, BIN_R),
                                       units * UNIT - FOOT_H)
    for i in range(nx):
        for j in range(ny):
            x, y = cell_centre(i, j, nx, ny)
            body += Pos(x, y, 0) * _stack(w - 2 * (a + c), BIN_R - a - c, [(a, True), (b, False), (c, True)])
    return body


def inner(n):
    """Inside width of an n-cell bin with the thinnest wall."""
    return n * PITCH - GAP - 2 * WALL


def scoop(length, width, z_floor, z_top, r_side, r_bottom):
    """Cutter for a rounded basin: things slide to the middle and a finger sweeps them up the side."""
    h = z_top - z_floor + 5
    s = Pos(0, 0, z_floor) * Box(width, length, h, align=BASE)
    s = fillet(s.edges().filter_by(Axis.Z), r_side)
    s = fillet(s.faces().sort_by(Axis.Z)[0].edges(), r_bottom)
    return s


def round_pocket(d, z_floor, z_top, r_bottom=0.0):
    p = Pos(0, 0, z_floor) * Cylinder(d / 2, z_top - z_floor + 5, align=BASE)
    if r_bottom:
        p = fillet(p.faces().sort_by(Axis.Z)[0].edges(), r_bottom)
    return p


def triangle_pocket(side, z_floor, z_top, relief=1.5):
    """Equilateral triangle, one flat side to the front, bounding box centred.

    Small round reliefs in the corners, so the case's sharp edges seat.
    """
    r = side / math.sqrt(3)
    tri = RegularPolygon(r, 3, rotation=90)          # a point at the back, flat side at the front
    bb = tri.bounding_box()
    dy = -(bb.min.Y + bb.max.Y) / 2
    p = Pos(0, dy, z_floor) * extrude(tri, z_top - z_floor + 5)
    for k in range(3):
        ang = math.radians(90 + 120 * k)
        p += Pos(r * math.cos(ang), r * math.sin(ang) + dy, z_floor) * Cylinder(relief, z_top - z_floor + 5,
                                                                              align=BASE)
    return p, dy

