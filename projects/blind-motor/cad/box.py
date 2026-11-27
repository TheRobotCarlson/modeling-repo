"""Blind motor: a worm-gear motor in a printed box that pulls a roller shade's bead chain.

A JGY-370 worm-gear motor with a Hall encoder turns a printed sprocket on the shade's
#10 bead chain. The worm gear can't be turned from the chain, so the shade holds still
with the power off and nobody can pull it out of step; the encoder counts every turn
the motor makes. Two 18650 cells keep the ESP32 counting through power cuts. A USB-C
charger fills them and the box runs from them, so mains is optional.

Sizes: chain and motor from seller listings (SPEC), or guessed (EST) where no listing
gives them. Everything marked EST is in the drawing for measuring.

Millimetres. The box hangs on the side wall of the window recess: the wall is the XZ
plane at y = 0, the box stands out along +Y, Z up, centred on x = 0. The sprocket is on
the front, at the bottom; the chain loop hangs down to it.
"""

import math

from build123d import Align, Box, Cylinder, Pos, Rot, Sphere

from modelkit import Assembly

# --- chain: #10 bead chain, the usual roller-shade size ----------------------------
BEAD_D = 4.5            # SPEC: bead diameter (3/16")
BEAD_PITCH = 6.0        # SPEC: bead centre to bead centre (6.0-6.2 by brand)
TEETH = 12
R_PITCH = BEAD_PITCH / (2 * math.sin(math.pi / TEETH))    # bead centres sit on this circle
CHAIN_PER_TURN = TEETH * BEAD_PITCH                         # 72 mm of chain per sprocket turn
LINK_W = 1.6            # EST: groove for the wire between beads

# --- motor: JGY-370 worm gearmotor with Hall encoder ------------------------------
GB_W, GB_T, GB_L = 32.0, 25.0, 46.0   # SPEC: gearbox width (x), thickness (y), length (z)
MOTOR_D, MOTOR_L = 24.4, 30.8          # SPEC: motor can
ENC_L = 12.0            # EST: encoder cap on the motor's end
SHAFT_D, SHAFT_L = 6.0, 14.0           # SPEC: D-shaft out of the gearbox face
SHAFT_FLAT = 5.5        # EST: across the D, flat to round
SHAFT_UP = 12.0         # EST: shaft centre above the gearbox's lower end
BUSH_D = 10.0           # EST: the boss round the shaft on the gearbox face
MOUNT_DX = 11.0         # EST: two M3 holes in the gearbox face, this far either side of the shaft

# --- cells, boards ------------------------------------------------------------------
CELL_D, CELL_L = 18.6, 65.2            # SPEC: 18650
CELL_BAY = CELL_L + 6.0                # with a spring contact at each end
BOARD_T = 5.0                          # boards stand on edge beside the motor can
XIAO = (BOARD_T, 17.8, 21.0)           # SPEC: XIAO ESP32-C6, 21 x 17.8
DRIVER = (BOARD_T, 18.0, 20.0)         # EST: DRV8833 breakout
BUCK = (BOARD_T, 17.0, 22.0)           # EST: buck module, battery to 5 V
CHARGER = (25.0, 20.0, 5.0)            # EST: 2-cell USB-C charger, lying flat on top
USB_C = (9.4, 3.8)                     # SPEC: receptacle opening

# --- box ----------------------------------------------------------------------------
WALL, CLR = 2.4, 0.4
LID_T = 2.4
IW = max(GB_W, 2 * CELL_D + 1.0) + 2 * CLR      # inside width
ID = GB_T + 2 * CLR                              # inside depth, back wall to lid
W = IW + 2 * WALL
Z_GB = WALL + CLR                                # gearbox's lower end
Z_SHAFT = Z_GB + SHAFT_UP
Z_CAN_TOP = Z_GB + GB_L + MOTOR_L + ENC_L
Z_BOARDS = Z_GB + GB_L + 0.5                     # boards beside the can, two high each side
Z_SHELF = max(Z_CAN_TOP, Z_BOARDS + XIAO[2] + 1.0 + BUCK[2]) + 0.6     # floor of the battery bay
Z_CELLS = Z_SHELF + 1.6 + 3.0                    # cells stand on their contacts
Z_CHARGER = Z_SHELF + 1.6 + CELL_BAY + 1.0
BUTTON_ROOM = 7.0                                # under the top, for two 6 x 6 mm push buttons
H = Z_CHARGER + CHARGER[2] + BUTTON_ROOM + WALL
BUTTON_DX = 8.0                                  # the buttons poke through the top, either side of centre
Y_LID = WALL + ID                                # lid's inside face = gearbox face
Y_FRONT = Y_LID + LID_T
EAR = (14.0, 12.0)                               # wall ears, top and bottom, for one screw each

# --- sprocket -------------------------------------------------------------------------
HUB_D, HUB_L = 14.0, 3.0
CORE_W = BEAD_D + 0.6
FLANGE_T = 1.5
WHEEL_W = CORE_W + 2 * FLANGE_T
R_FLANGE = R_PITCH + BEAD_D / 2 + 2.5
Y_SPROCKET = Y_FRONT + 0.6                       # hub starts here
CHAIN_Y = Y_SPROCKET + HUB_L + WHEEL_W / 2       # the chain runs in this plane

BASE = (Align.CENTER, Align.MIN, Align.MIN)


def _y_cyl(r, length, x, y0, z):
    """Cylinder along +Y from y0."""
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, length, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _x_cyl(r, length, x0, y, z):
    return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(r, length, align=(Align.CENTER, Align.CENTER, Align.MIN))


def motor():
    """Reference model of the gearmotor, placed as it sits in the box."""
    yc = Y_LID - GB_T / 2
    gb = Pos(0, Y_LID - GB_T, Z_GB) * Box(GB_W, GB_T, GB_L, align=BASE)
    can = Pos(0, yc, Z_GB + GB_L) * Cylinder(MOTOR_D / 2, MOTOR_L + ENC_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shaft = _y_cyl(SHAFT_D / 2, SHAFT_L, 0, Y_LID, Z_SHAFT)
    flat = Pos(0, Y_LID + 1, Z_SHAFT + SHAFT_FLAT - SHAFT_D / 2) * Box(SHAFT_D, SHAFT_L, SHAFT_D,
                                                                       align=(Align.CENTER, Align.MIN, Align.MIN))
    return gb + can + (shaft - flat)


def cells():
    return [Pos(s * (CELL_D / 2 + 0.3), WALL + ID / 2, Z_CELLS) *
            Cylinder(CELL_D / 2, CELL_L, align=(Align.CENTER, Align.CENTER, Align.MIN)) for s in (-1, 1)]


def boards():
    """Bought modules, placed. Boards stand on edge in the gaps beside the motor can."""
    side = IW / 2 - CLR - BOARD_T / 2
    y = WALL + ID / 2
    z0 = Z_BOARDS
    def board(size, x, z):
        return Pos(x, y, z) * Box(*size, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return {
        "xiao": board(XIAO, -side, z0),
        "buck": board(BUCK, -side, z0 + XIAO[2] + 1.0),
        "driver": board(DRIVER, side, z0),
        "charger": Pos(0, y, Z_CHARGER) * Box(*CHARGER, align=(Align.CENTER, Align.CENTER, Align.MIN)),
    }


def base():
    """Back, sides, top and bottom in one print; open at the front for the lid."""
    outer = Box(W, Y_LID, H, align=BASE)
    inner = Pos(0, WALL, WALL) * Box(IW, ID + 1, H - 2 * WALL, align=BASE)
    b = outer - inner
    # battery bay floor, with a hole for the wires
    shelf = Pos(0, WALL, Z_SHELF) * Box(IW, ID, 1.6, align=BASE)
    b += shelf - Pos(0, WALL + ID / 2, Z_SHELF) * Box(8, 6, 2, align=BASE)
    # wall ears
    for z0, zc in ((-EAR[1], -EAR[1] / 2), (H, H + EAR[1] / 2)):
        ear = Pos(0, 0, z0) * Box(EAR[0], WALL, EAR[1], align=BASE)
        b += ear - _y_cyl(2.2, WALL, 0, 0, zc)
    # lid screws into the two top corners
    for s in (-1, 1):
        x = s * (IW / 2 - 3.0)
        z = H - WALL - 3.0
        b += _y_cyl(3.0, ID, x, WALL, z) - _y_cyl(1.25, ID, x, WALL + 4, z)
    # USB-C on the right, beside the charger; up and down buttons through the top
    zc = Z_CHARGER + CHARGER[2] / 2
    b -= Pos(IW / 2 - 1, WALL + ID / 2, zc) * Box(WALL + 2, USB_C[0], USB_C[1], align=(Align.MIN, Align.CENTER, Align.CENTER))
    for s in (-1, 1):
        b -= Pos(s * BUTTON_DX, WALL + ID / 2, H - WALL - 1) * Cylinder(1.75, WALL + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b


def lid():
    """Front plate. The gearbox screws to it, so the shaft is always square to it."""
    p = Pos(0, Y_LID, 0) * Box(W, LID_T, H, align=BASE)
    p -= _y_cyl(BUSH_D / 2 + 0.4, LID_T, 0, Y_LID, Z_SHAFT)
    for s in (-1, 1):
        p -= _y_cyl(1.7, LID_T, s * MOUNT_DX, Y_LID, Z_SHAFT)                    # into the gearbox
        p -= _y_cyl(1.7, LID_T, s * (IW / 2 - 3.0), Y_LID, H - WALL - 3.0)        # into the base
    # a lip that keys into the opening
    lip = Pos(0, Y_LID - 1.5, WALL + CLR) * Box(IW - 2 * CLR, 1.5, H - 2 * WALL - 2 * CLR, align=BASE)
    lip -= Pos(0, Y_LID - 1.5, WALL + CLR + 1.2) * Box(IW - 2 * CLR - 2.4, 1.5, H - 2 * WALL - 2 * CLR - 2.4, align=BASE)
    lip -= Pos(0, Y_LID - 1.5, 0) * Box(GB_W + 2 * CLR, 1.5, Z_GB + GB_L + CLR, align=BASE)   # clear of the gearbox
    return p + lip


def sprocket():
    """12 pockets for #10 beads, a groove for the wire between them, flanges each side."""
    def ring(r, w, y0):
        return _y_cyl(r, w, 0, y0, Z_SHAFT)
    y_core = Y_SPROCKET + HUB_L + FLANGE_T
    s = ring(HUB_D / 2, HUB_L, Y_SPROCKET)
    s += ring(R_FLANGE, FLANGE_T, Y_SPROCKET + HUB_L)
    s += ring(R_PITCH + 0.6, CORE_W, y_core)
    s += ring(R_FLANGE, FLANGE_T, y_core + CORE_W)
    yc = y_core + CORE_W / 2
    s -= ring(R_PITCH + 1, LINK_W, yc - LINK_W / 2) - ring(R_PITCH - 1.0, LINK_W, yc - LINK_W / 2)
    for i in range(TEETH):
        a = 2 * math.pi * i / TEETH
        s -= Pos(R_PITCH * math.sin(a), yc, Z_SHAFT + R_PITCH * math.cos(a)) * Rot(90, 0, 0) * Sphere(BEAD_D / 2 + 0.2)  # poles off the faces
    # D bore, and an M3 set screw down onto the flat
    bore = ring(SHAFT_D / 2 + 0.1, HUB_L + WHEEL_W, Y_SPROCKET)
    bore -= Pos(0, Y_SPROCKET, Z_SHAFT + SHAFT_FLAT - SHAFT_D / 2 + 0.1) * Box(SHAFT_D, HUB_L + WHEEL_W, SHAFT_D,
                                                                              align=(Align.CENTER, Align.MIN, Align.MIN))
    s -= bore
    s -= Pos(0, Y_SPROCKET + HUB_L / 2, Z_SHAFT) * Cylinder(1.25, HUB_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s


def chain():
    """The chain where it wraps the sprocket's lower half and runs up both sides."""
    beads = []
    for i in range(TEETH // 2 + 1):                     # 180 degrees of wrap, under the shaft
        a = math.pi * i / (TEETH // 2)
        beads.append(Pos(R_PITCH * math.cos(a), CHAIN_Y, Z_SHAFT - R_PITCH * math.sin(a)) * Sphere(BEAD_D / 2))
    for s in (-1, 1):
        for k in range(1, 9):
            beads.append(Pos(s * R_PITCH, CHAIN_Y, Z_SHAFT + k * BEAD_PITCH) * Sphere(BEAD_D / 2))
    out = beads[0]
    for b in beads[1:]:
        out += b
    return out


def build():
    return {"base": base(), "lid": lid(), "sprocket": sprocket(), "motor": motor(),
            "cells": cells(), "boards": boards(), "chain": chain()}


def export():
    p = build()
    asm = Assembly("blind-motor", "box", title="Blind motor",
                   description="Worm-gear motor, encoder, two 18650 cells and an ESP32 in a printed box; a sprocket pulls the shade's bead chain.")
    asm.add("base", p["base"], "Box", material="PETG", color="#e9ecef",
            description="Back, sides, battery-bay floor and wall ears, in one print. Open at the front.")
    asm.add("lid", p["lid"], "Lid", material="PETG", color="#cfd6dd", explode=(0, 25, 0),
            description="Front plate. Two M3 screws hold the gearbox to it, two more hold it to the box.")
    asm.add("sprocket", p["sprocket"], "Sprocket", material="PETG", color="#7fa7c9", explode=(0, 45, 0),
            description=f"{TEETH} pockets for #10 beads: {CHAIN_PER_TURN:.0f} mm of chain per turn. D bore and an M3 set screw.",
            notes=["print the pocket size to fit your chain"])
    asm.add("motor", p["motor"], "JGY-370 worm gearmotor with encoder", source="bought", color="#8a8f98",
            explode=(0, 0, 0), mass_g=162, description="12 V worm gearmotor with a Hall encoder. Self-locking: the chain can't turn it.",
            notes=["shaft height and mounting holes: EST"])
    for i, c in enumerate(p["cells"]):
        asm.add(f"cell{i + 1}", c, "18650 cell", source="bought", color="#4a7c59", explode=(0, 0, 40), mass_g=47,
                description="Two in series: 7.4 V nominal. They run the box; USB-C keeps them charged.")
    names = {"xiao": "XIAO ESP32-C6", "buck": "Buck converter, battery to 5 V", "driver": "DRV8833 motor driver",
             "charger": "2-cell USB-C charger"}
    for k, s in p["boards"].items():
        asm.add(k, s, names[k], source="bought", color="#2f6f9f", explode=(0, 0, 0), mass_g=3,
                description="Placed to show the space it needs.", notes=["size: EST"])
    asm.add("chain", p["chain"], "Bead chain (the shade's own)", source="bought", color="#b9b9b9",
            explode=(0, 45, 0), mass_g=0, layer="Chain", description="#10 bead chain: 4.5 mm beads, 6 mm apart.")
    asm.export()


if __name__ == "__main__":
    export()
