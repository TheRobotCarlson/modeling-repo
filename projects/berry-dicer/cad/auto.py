"""Automated dicer: load a row, press start, get cubes in the dish and tops in the bin.

The same stainless cartridge as the manual press, with the topper's tray mounted
behind the hopper. One cycle:

1. The berries lie in the tray, leafy end against the fence at the back.
2. A servo swings the topper wire down through the slot: the tops are off.
3. A servo flips the fence flap back: the tops fall into the compost bin.
4. A servo tilts the tray forward: the berries drop into the hopper. Which way up
   they land does not matter once the tops are off.
5. After up to three rows, the platen comes down on two lead screws in 12 mm steps.
   After each step a stepper sweeps the wire bow under the grid.

The platen parks high enough for the tray to tip under it.
"""

import math

from build123d import Box, Cylinder, Pos, Rot

from _steel import (BASE, BOW_H, BOW_W, HOP_T, IN_X, IN_Y, PLATEN_LIP, T125, TOP_W, TRAY_T, WIRE_D, Y_SWEEP, Z_GTOP,
                    Z_HTOP, Z_WIRE, berries, grid, hopper, platen, stand_berries, tray, wire_bow)
from modelkit import Assembly
from press import BASE_T, SLOT, WALL_IN, WALL_OUT, WALL_Y, dish

UP = 330.0                         # platen parked: clear of the tray as it tips
Z_BED = Z_HTOP + 16.0              # topper tray bed: high enough that its walls clear the hopper as it tips
TILT = (IN_Y / 2 + 4.0, Z_BED)     # tray pivot (y, z): its front edge, over the hopper's back wall
Y_FENCE = TILT[0] + 110.0
ARM_PIVOT = (TILT[0], Z_BED + 18.0)
ARM_X = TOP_W / 2 + 12.0
SCREW_X = WALL_OUT + 22.0          # lead screws, either side
NEMA = 42.3


def motor(x, y, z):
    return Pos(x, y, z) * Box(NEMA, NEMA, 48.0, align=BASE)


def servo(x, y, z):
    """DS3225-size servo body (40 x 20 x 40.5 mm, SOURCE: DSServo listing; EST mounting)."""
    return Pos(x, y, z) * Box(20, 40, 40.5)


def build(platen_z=UP, bow_y=Y_SWEEP[0], arm_deg=25.0):
    p = {}
    p["hopper"], p["grid"] = hopper(), grid()
    p["platen"] = platen(platen_z)
    p["bow"], p["wire"] = wire_bow(bow_y)
    p["tray"], p["flap"], slot_y = tray(Y_FENCE, Z_BED, +1)
    p["berries"] = berries(Y_FENCE - TRAY_T, Z_BED, +1, n=9) + stand_berries(Z_GTOP, n=8, seed=8)

    # --- topper wire arm ---------------------------------------------------------------
    r = math.hypot(slot_y - ARM_PIVOT[0], ARM_PIVOT[1] - Z_BED)
    wy = ARM_PIVOT[0] + r * math.cos(math.radians(arm_deg))
    wz = ARM_PIVOT[1] + r * math.sin(math.radians(arm_deg))
    p["twire"] = Pos(0, wy, wz) * Rot(0, 90, 0) * Cylinder(WIRE_D / 2, 2 * ARM_X - 3)
    pins = Pos(0, *ARM_PIVOT) * Rot(0, 90, 0) * Cylinder(3, 2 * ARM_X + 24)
    arms = None
    for sx in (-1, 1):
        a = Pos(sx * ARM_X, (wy + ARM_PIVOT[0]) / 2, (wz + ARM_PIVOT[1]) / 2) * Rot(arm_deg, 0, 0) * Box(T125, r + 16, 14)
        a += Pos(sx * ARM_X, *ARM_PIVOT) * Rot(0, 90, 0) * Cylinder(9, T125)
        arms = a if arms is None else arms + a
    p["tarm"], p["pins"] = arms - pins, pins

    # --- frame -------------------------------------------------------------------------
    base = Pos(0, 95, 0) * Box(2 * SCREW_X + 70, 2 * WALL_Y + 230, BASE_T, align=BASE)
    walls = None
    for sx in (-1, 1):
        w = Pos(sx * (WALL_IN + WALL_OUT) / 2, 0, BASE_T) * Box(WALL_OUT - WALL_IN, 2 * WALL_Y,
                                                                 Z_HTOP - HOP_T - BASE_T, align=BASE)
        w -= Pos(sx * (WALL_IN + BOW_W / 2 + 4) / 2, -10, SLOT[0]) * Box(BOW_W / 2 + 4 - WALL_IN, 2 * WALL_Y,
                                                                        SLOT[1] - SLOT[0], align=BASE)
        w -= Pos(sx * (WALL_IN + WALL_OUT) / 2, 10, BASE_T + 6) * Box(WALL_OUT - WALL_IN - 8, 2 * WALL_Y - 40,
                                                                       SLOT[0] - BASE_T - 12, align=BASE)
        # pivot brackets for the tray and the topper arm, on the wall's back end
        br = Pos(sx * (ARM_X + T125 / 2 + 8), TILT[0], Z_HTOP) * Box(12, 40, ARM_PIVOT[1] - Z_HTOP + 12, align=BASE)
        # a slit through the wall's outer skin for the belt clamp (left side only matters)
        w -= Pos(sx * (BOW_W / 2 + 8), -10, SLOT[0] - 9) * Box(12, 2 * WALL_Y, 8, align=BASE)
        walls = w + br if walls is None else walls + w + br
    walls -= pins
    for sx in (-1, 1):                 # posts the tray's back end rests on
        walls += Pos(sx * (TOP_W / 2 - 20), Y_FENCE - 30, BASE_T) * Box(16, 16, Z_BED - TRAY_T - BASE_T, align=BASE)
    p["frame"] = base + walls

    top_z = UP + 140.0
    ext = None                         # 2020 aluminium extrusion uprights and the top beam
    for sx in (-1, 1):
        e = Pos(sx * SCREW_X, -32, BASE_T) * Box(20, 20, top_z - BASE_T, align=BASE)
        ext = e if ext is None else ext + e
    ext += Pos(0, -32, top_z) * Box(2 * SCREW_X + 20, 20, 20, align=BASE)
    p["extrusion"] = ext
    screws = None
    for sx in (-1, 1):
        s = Pos(sx * SCREW_X, 0, Z_HTOP - 20) * Cylinder(4, top_z - Z_HTOP + 20, align=BASE)
        screws = s if screws is None else screws + s
    p["screws"] = screws
    p["motors"] = (motor(-SCREW_X, 0, top_z + 20) + motor(SCREW_X, 0, top_z + 20)
                   + Pos(-(WALL_OUT + 24), -WALL_Y - 26, Z_WIRE - BOW_H / 2) * Box(NEMA, NEMA, 48))
    p["topplate"] = Pos(0, 0, top_z + 20 - 6) * Box(2 * SCREW_X + 60, 60, 6, align=BASE)
    p["topplate"] -= Pos(0, -32, top_z) * Box(2 * SCREW_X + 22, 21, 20.5, align=BASE)
    for sx in (-1, 1):
        p["topplate"] -= Pos(sx * SCREW_X, 0, top_z) * Cylinder(5, 40)

    # crosshead: nuts on the screws, the platen hung under it on two stainless posts
    ch_z = platen_z + PLATEN_LIP + 70.0
    ch = Pos(0, 0, ch_z) * Box(2 * SCREW_X + 40, 30, 20, align=BASE)
    for sx in (-1, 1):
        ch -= Pos(sx * SCREW_X, 0, ch_z - 1) * Cylinder(4.2, 22, align=BASE)
    p["crosshead"] = ch
    posts = None
    for sx in (-1, 1):
        s = Pos(sx * 90, 0, platen_z + T125) * Cylinder(6, ch_z - platen_z - T125, align=BASE)
        posts = s if posts is None else posts + s
    p["posts"] = posts
    y0, y1 = -WALL_Y - 26 + NEMA / 2 + 1, WALL_Y + 20
    p["belt"] = Pos(-(WALL_OUT + 6), (y0 + y1) / 2, SLOT[0] - 8) * Box(6, y1 - y0, 6, align=BASE)
    p["servos"] = (servo(-(ARM_X + 30), ARM_PIVOT[0], ARM_PIVOT[1])
                   + servo(ARM_X + 30, TILT[0] + 22, TILT[1] + 24)
                   + servo(ARM_X + 30, slot_y + 2, Z_BED - 26))
    p["dish"] = dish()
    p["bin"] = Pos(0, Y_FENCE + 55, BASE_T) * Box(300, 90, 120, align=BASE) - Pos(0, Y_FENCE + 55, BASE_T + 3) * Box(294, 84, 130, align=BASE)
    p["electronics"] = Pos(SCREW_X - 10, WALL_Y + 150, BASE_T) * Box(90, 60, 45, align=BASE)
    return p


def export(p):
    asm = Assembly("berry-dicer", "auto", title="Dicer, automated",
                   description="Topper tray behind the hopper, platen on two lead screws, wire bow on a belt.")
    food = dict(material="Stainless 304", source="machined")
    ref = dict(source="bought", notes=["reference only"])
    asm.add("hopper", p["hopper"], "Hopper", color="#c9ced4", explode=(0, -40, 60), **food,
            description="The same cartridge as the manual press.", notes=["Dishwasher"])
    asm.add("grid", p["grid"], "Cutting grid", color="#e3e6ea", explode=(0, -40, 30), **food,
            description="12 mm cells, sharpened strips.", notes=["Dishwasher"])
    asm.add("platen", p["platen"], "Platen", color="#b5bcc4", explode=(0, 0, 40), **food,
            description="Hung from the crosshead on two posts.", notes=["Dishwasher"])
    asm.add("bow", p["bow"], "Wire bow", color="#aab1b9", explode=(0, -60, -30), **food,
            description="Clamped to the belt on the left.", notes=["Dishwasher"])
    asm.add("wire", p["wire"], "Dicing wire", color="#5b636c", material="Stainless 304", source="bought",
            explode=(0, -60, -30), description="0.5 mm, under the grid.", notes=["EST: gauge"])
    asm.add("tray", p["tray"], "Topper tray", color="#c9ced4", explode=(0, 60, 40), **food,
            description="Tilts forward about its front edge to drop the row into the hopper.", notes=["Dishwasher"])
    asm.add("flap", p["flap"], "Fence flap", color="#b5bcc4", explode=(0, 90, 40), **food,
            description="Flips back to drop the tops into the bin.", notes=["Dishwasher"])
    asm.add("twire", p["twire"], "Topper wire", color="#5b636c", material="Stainless 304", source="bought",
            explode=(0, 60, 80), description="Swings down through the tray's slot.", notes=["EST: gauge"])
    asm.add("tarm", p["tarm"], "Topper arm", color="#aab1b9", explode=(0, 60, 80), **food,
            description="Two 1/8 in 304 arms on a servo.", notes=["Dishwasher"])
    asm.add("pins", p["pins"], "Arm pivot rod", color="#7d838c", material="Stainless 304", source="bought",
            explode=(0, 60, 80), description="6 mm stainless rod.")
    asm.add("frame", p["frame"], "Frame", material="PLA", color="#f1d9c6",
            description="Base, side walls with bow slots, tray brackets and rests. PLA Pure.",
            notes=["Printed in parts and bolted", "Mass shown is solid"])
    asm.add("extrusion", p["extrusion"], "2020 extrusion", material="Aluminum 6061", color="#9aa3ad",
            source="bought", description="Two uprights and a top beam carry the lead screws.")
    asm.add("topplate", p["topplate"], "Motor plate", material="PLA", color="#e8b796",
            description="Holds both lead-screw motors on the top beam.")
    asm.add("screws", p["screws"], "T8 lead screws (2)", material="Stainless 304", color="#7d838c", source="bought",
            description="2 mm lead, 300 mm, for force: 8 mm lead screws would stall before the peak. Driven together.")
    asm.add("motors", p["motors"], "NEMA 17 steppers (3)", color="#30343a", source="bought", mass_g=3 * 390,
            description="Two on the lead screws, one on the wire bow's belt.")
    asm.add("crosshead", p["crosshead"], "Crosshead", material="Aluminum 6061", color="#9aa3ad", source="bought",
            explode=(0, 0, 40), description="2040 extrusion with a lead-screw nut at each end.",
            notes=["EST: section"])
    asm.add("posts", p["posts"], "Platen posts", material="Stainless 304", color="#aab1b9", source="bought",
            explode=(0, 0, 40), description="12 mm stainless rod, bolted through the platen's face.")
    asm.add("belt", p["belt"], "GT2 belt", color="#30343a", source="bought", mass_g=10,
            description="Runs the length of the left wall; the bow is clamped to it.")
    asm.add("servos", p["servos"], "Servos (3)", color="#30343a", source="bought", mass_g=3 * 65,
            description="Topper arm, tray tilt and fence flap. 25 kg cm class.")
    asm.add("electronics", p["electronics"], "Controller box", material="PLA", color="#e8b796",
            description="XIAO ESP32S3, three TMC2209 drivers, 24 V supply in, 6 V for the servos.")
    asm.add("dish", p["dish"], "Baking dish (yours)", color="#d8e6ef", explode=(0, -80, 0), **ref)
    asm.add("bin", p["bin"], "Compost bin (yours)", color="#9fb38a", explode=(0, 80, 0), **ref)
    asm.add("berries", p["berries"], "Berries", color="#d63b3b", source="bought", layer="Berries",
            description="A row in the tray, and topped berries already in the hopper.", notes=["reference only"])
    asm.export()


if __name__ == "__main__":
    export(build())
