"""Manual dicer press: an arbor press over the stainless cartridge.

Turning the handle drives a rack on the platen's stem. The pinion's index wheel
clicks every 12 mm, one grid height. After each click, push the wire bow's rod back
(or pull it forward) once: the wire cuts off the layer that just came through.

Printed parts are PLA Pure and stay out of the fruit's path. The stem and head
are over the hopper, so the stem is a smooth printed bar with no grease.
"""

import math

from build123d import Align, Box, Cylinder, Pos, Rot

from _steel import (BASE, BOW_H, BOW_W, CELL, FLANGE, HOP_T, IN_X, IN_Y, PLATEN_LIP, T125, Y_SWEEP,
                    Z_GTOP, Z_GRID, Z_HTOP, Z_WIRE, grid, hopper, platen, stand_berries, wire_bow)
from modelkit import Assembly

BASE_T = 8.0
WALL_IN = 172.0                           # side walls' inner faces: a 340 mm dish fits between
WALL_OUT = BOW_W / 2 + 14.0
WALL_Y = 150.0                            # half length of the side walls
SLOT = (Z_WIRE - BOW_H - 1.5, Z_WIRE + 3.5)   # bow slot, bottom and top
STEM = 24.0
HEAD_Z = (300.0, 362.0)
PINION_R = 8 * CELL / (2 * math.pi)       # 8 clicks per turn, 12 mm each: 15.28 mm pitch radius
STEM_L = 225.0
UP = 280.0                                # platen face when raised for loading
COL_Y = (160.0, 200.0)


def build(platen_z=UP, bow_y=Y_SWEEP[0]):
    p = {}
    p["hopper"], p["grid"] = hopper(), grid()
    p["platen"] = platen(platen_z)
    p["bow"], p["wire"] = wire_bow(bow_y)
    p["rod"] = Pos(0, bow_y - T125 / 2 - 80.0, Z_WIRE - BOW_H + 5) * Rot(90, 0, 0) * Cylinder(3.0, 160.0)
    p["rod"] += Pos(0, bow_y - T125 / 2 - 160.0, Z_WIRE - BOW_H + 5) * Rot(90, 0, 0) * Cylinder(9.0, 22.0)   # knob
    p["berries"] = stand_berries(Z_GTOP)

    # --- printed frame ------------------------------------------------------------------
    base = Pos(0, 25, 0) * Box(2 * WALL_OUT + 20, 2 * WALL_Y + 100, BASE_T, align=BASE)
    walls = None
    for sx in (-1, 1):
        w = Pos(sx * (WALL_IN + WALL_OUT) / 2, 0, BASE_T) * Box(WALL_OUT - WALL_IN, 2 * WALL_Y,
                                                                 Z_HTOP - HOP_T - BASE_T, align=BASE)
        # the bow's arms and crossbar ends run in this slot, open at the front
        w -= Pos(sx * (WALL_IN + BOW_W / 2 + 4) / 2, -10, SLOT[0]) * Box(BOW_W / 2 + 4 - WALL_IN, 2 * WALL_Y,
                                                                        SLOT[1] - SLOT[0], align=BASE)
        w -= Pos(sx * (WALL_IN + WALL_OUT) / 2, 10, BASE_T + 6) * Box(WALL_OUT - WALL_IN - 8, 2 * WALL_Y - 40,
                                                                       SLOT[0] - BASE_T - 12, align=BASE)   # hollow
        walls = w if walls is None else walls + w
    col = Pos(0, sum(COL_Y) / 2, BASE_T) * Box(90, COL_Y[1] - COL_Y[0], HEAD_Z[1] - BASE_T, align=BASE)
    col -= Pos(0, sum(COL_Y) / 2, BASE_T + 6) * Box(78, COL_Y[1] - COL_Y[0] - 12, HEAD_Z[0] - BASE_T - 12, align=BASE)
    head = Pos(0, (STEM / 2 + 4 + COL_Y[1]) / 2 - 18, HEAD_Z[0]) * Box(90, COL_Y[1] + 18 - STEM / 2 - 4 + 18,
                                                                       HEAD_Z[1] - HEAD_Z[0], align=BASE)
    head = Pos(0, (-STEM / 2 - 10 + COL_Y[0]) / 2, HEAD_Z[0]) * Box(90, COL_Y[0] + STEM / 2 + 10,
                                                                    HEAD_Z[1] - HEAD_Z[0], align=BASE)
    head -= Pos(0, 0, HEAD_Z[0] - 1) * Box(STEM + 0.6, STEM + 0.6, 100, align=BASE)       # stem bore
    pz = sum(HEAD_Z) / 2
    py = STEM / 2 + PINION_R
    head -= Pos(0, py, pz) * Rot(0, 90, 0) * Cylinder(PINION_R + 3, 50)                   # pinion pocket
    head -= Pos(0, py, pz) * Rot(0, 90, 0) * Cylinder(4.2, 120)                           # shaft
    p["frame"] = base + walls + col + head

    # --- moving parts -------------------------------------------------------------------
    stem_z = platen_z + PLATEN_LIP
    p["stem"] = Pos(0, 0, stem_z) * Box(STEM, STEM, STEM_L, align=BASE)
    p["stem"] += Pos(0, 0, platen_z + T125) * Box(80, 40, PLATEN_LIP - T125, align=BASE)  # foot, bolted to the platen
    shaft = Pos(0, py, pz) * Rot(0, 90, 0) * Cylinder(4.0, 130)
    p["pinion"] = Pos(0, py, pz) * Rot(0, 90, 0) * Cylinder(PINION_R - 0.3, 40) - shaft
    hub = Pos(62, py, pz) * Rot(0, 90, 0) * Cylinder(14, 12)
    arm = Pos(62, py - 110, pz) * Box(10, 220, 14)
    knob = Pos(62 + 5, py - 215, pz) * Rot(0, 90, 0) * Cylinder(12, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p["handle"] = shaft + hub + arm + knob
    index = Pos(-58, py, pz) * Rot(0, 90, 0) * Cylinder(26, 8)
    for k in range(8):
        a = 2 * math.pi * k / 8
        index -= Pos(-58, py + 26 * math.cos(a), pz + 26 * math.sin(a)) * Rot(0, 90, 0) * Cylinder(3.5, 10)
    p["index"] = index - shaft
    p["plunger"] = Pos(-58, py, pz + 26 + 3.6) * Box(8, 8, 22, align=BASE)
    p["dish"] = dish()
    return p


def dish():
    """A 9 x 13 in baking dish under the grid, to catch the cubes (reference)."""
    d = Pos(0, 0, BASE_T) * Box(340, 240, 55, align=BASE)
    d -= Pos(0, 0, BASE_T + 4) * Box(332, 232, 60, align=BASE)
    return d


def export(p):
    asm = Assembly("berry-dicer", "press", title="Dicer press, manual",
                   description="Arbor press over the stainless cartridge: one click, one wire sweep, one layer of 12 mm cubes.")
    food = dict(material="Stainless 304", source="machined")
    asm.add("hopper", p["hopper"], "Hopper", color="#c9ced4", explode=(0, 0, 60), **food,
            description="312 x 156 mm inside, 0.048 in sheet bent into a box with an outward flange that rests on the frame.",
            notes=["Laser cut and bent (SendCutSend)", "Dishwasher"])
    asm.add("grid", p["grid"], "Cutting grid", color="#e3e6ea", explode=(0, 0, 30), **food,
            description="37 slotted strips of 0.030 in 304, 12 mm tall, crossed into 12 mm cells. Top edges sharpened.",
            notes=["Laser cut (SendCutSend)", "Sharpen before assembly", "Dishwasher"])
    asm.add("platen", p["platen"], "Platen", color="#b5bcc4", explode=(0, 0, 40), **food,
            description="1/8 in 304 tray, face down, edges bent up for stiffness.", notes=["Dishwasher"])
    asm.add("bow", p["bow"], "Wire bow", color="#aab1b9", explode=(0, -60, -30), **food,
            description="Flat U of 1/8 in 304. Its arms run in the side walls' slots.", notes=["Dishwasher"])
    asm.add("wire", p["wire"], "Cutting wire", color="#5b636c", explode=(0, -60, -30), material="Stainless 304",
            source="bought", description="0.5 mm stainless wire across the bow's tips, tensioned by a screw.",
            notes=["EST: gauge"])
    asm.add("rod", p["rod"], "Bow push rod", color="#aab1b9", explode=(0, -60, -30), **food,
            description="6 mm stainless rod with a knob: push to sweep the wire back, pull to sweep it forward.")
    asm.add("frame", p["frame"], "Frame", material="PLA", color="#f1d9c6",
            description="Base, side walls with the bow slots, column and head. PLA Pure. Wipe clean, not dishwasher.",
            notes=["Printed in parts and bolted"])
    asm.add("stem", p["stem"], "Stem and rack", material="PLA", color="#e8b796", explode=(0, 0, 40),
            description="24 mm square bar with a rack on its back face (teeth not drawn). Its foot bolts to the platen.")
    asm.add("pinion", p["pinion"], "Pinion", material="PLA", color="#e8b796", explode=(0, 40, 0),
            description="16 teeth, 15.3 mm pitch radius: one turn is 96 mm, eight clicks of 12.")
    asm.add("handle", p["handle"], "Handle", material="PLA", color="#d27f5a", explode=(40, 0, 0),
            description="220 mm arm on a steel shaft: about 13 to 1 over the pinion.")
    asm.add("index", p["index"], "Index wheel", material="PLA", color="#d27f5a", explode=(-40, 0, 0),
            description="Eight notches: a click every 12 mm of platen travel.")
    asm.add("plunger", p["plunger"], "Spring plunger", color="#7d838c", material="Steel", source="bought",
            explode=(-40, 0, 20), description="M8 ball spring plunger into the index notches.")
    asm.add("dish", p["dish"], "Baking dish (yours)", color="#d8e6ef", source="bought", explode=(0, -80, 0),
            description="Any dish at least 320 x 170 mm and under 75 mm tall catches the cubes.",
            notes=["reference only"])
    asm.add("berries", p["berries"], "Berries, tops off", color="#d63b3b", source="bought", layer="Berries",
            description="Standing on their cut faces, ready to press.", notes=["reference only"])
    asm.export()


if __name__ == "__main__":
    export(build())
