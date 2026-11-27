"""Labelled drawing of the blind motor box: front, side and the sprocket, with every size coded.

The numbers come from box.py. Motor and chain sizes are from seller listings or guessed,
so they are orange until measured. Writes data/blind-motor/drawing/box.json for
<Drawing name="box" />.
"""

import math

import box as B
from modelkit.drawing import Drawing, View, ellipse, rect

D = Drawing("blind-motor", "box", scale=3)
size = D.size
W, H = B.W, B.H
LISTING = "photo / guess"          # seller listings count as unmeasured


def front():
    v = D.view("From the front (the chain side)")
    v.poly(rect(-W / 2, 0, W / 2, H), "part")
    for z0 in (-B.EAR[1], H):
        v.poly(rect(-B.EAR[0] / 2, z0, B.EAR[0] / 2, z0 + B.EAR[1]), "part")
    gz = B.Z_GB
    v.poly(rect(-B.GB_W / 2, gz, B.GB_W / 2, gz + B.GB_L), "offcut")
    v.poly(rect(-B.MOTOR_D / 2, gz + B.GB_L, B.MOTOR_D / 2, B.Z_CAN_TOP), "offcut")
    for s in (-1, 1):
        cx = s * (B.CELL_D / 2 + 0.3)
        v.poly(rect(cx - B.CELL_D / 2, B.Z_CELLS, cx + B.CELL_D / 2, B.Z_CELLS + B.CELL_L), "cell")
        v.poly(ellipse(s * B.MOUNT_DX, B.Z_SHAFT, 1.5, 1.5, 0, 360, 16), "inner")
    v.poly(ellipse(0, B.Z_SHAFT, B.R_FLANGE, B.R_FLANGE, 0, 360), "tongue")
    v.poly(ellipse(0, B.Z_SHAFT, B.R_PITCH, B.R_PITCH, 0, 360), "flat", close=False)
    for s in (-1, 1):                              # the chain runs up both sides
        v.line((s * B.R_PITCH, B.Z_SHAFT), (s * B.R_PITCH, B.Z_SHAFT + 75), "guide m")
    v.tag((B.R_PITCH + 2, B.Z_SHAFT + 70), "chain", "note")
    v.tag((0, B.Z_CELLS + B.CELL_L / 2), "2 × 18650", "note", anchor="middle")
    v.tag((0, gz + B.GB_L + 20), "motor", "note", anchor="middle")

    v.dim((-W / 2, -B.EAR[1] - 6), (W / 2, -B.EAR[1] - 6), f"B1 {W:.1f}",
          size("B1", "Box width, outside", W, "derived"), lab=(0, 16))
    v.dim((W / 2 + 8, 0), (W / 2 + 8, H), f"B2 {H:.1f}",
          size("B2", "Box height, outside, not counting the wall ears", H, "derived"))
    v.dim((-W / 2 - 6, 0), (-W / 2 - 6, B.Z_SHAFT), f"B5 {B.Z_SHAFT:.1f}",
          size("B5", "Shaft (sprocket centre) above the box's bottom", B.Z_SHAFT, "derived"), lab=(-6, 4))
    v.dim((-B.GB_W / 2, gz + B.GB_L + 4), (B.GB_W / 2, gz + B.GB_L + 4), "M1 32",
          size("M1", "Gearbox width (seller listing)", B.GB_W, LISTING), lab=(0, -6))
    v.dim((-W / 2 - 22, gz), (-W / 2 - 22, gz + B.GB_L), "M3 46",
          size("M3", "Gearbox length (seller listing)", B.GB_L, LISTING), lab=(-6, 4))
    v.dim((-B.MOUNT_DX, B.Z_SHAFT + 22), (B.MOUNT_DX, B.Z_SHAFT + 22), f"M9 {2 * B.MOUNT_DX:.0f}",
          size("M9", "Gearbox mounting holes (M3), centre to centre, either side of the shaft", 2 * B.MOUNT_DX,
               "photo / guess"), lab=(0, -6))
    size("M4", "Motor can diameter (seller listing)", B.MOTOR_D, LISTING)
    size("M5", "Motor can plus encoder, past the gearbox", B.MOTOR_L + B.ENC_L, "photo / guess")
    size("M8", "Shaft centre above the gearbox's lower end", B.SHAFT_UP, "photo / guess")


def side():
    v = D.view("From the right: wall at the left, chain at the right")
    v.line((0, -20), (0, H + 20), "guide m")
    v.tag((-2, H + 14), "wall", "note", anchor="end")
    v.poly(rect(0, 0, B.Y_LID, H), "part")
    v.poly(rect(B.WALL, B.WALL, B.Y_LID, H - B.WALL), "inner")
    v.poly(rect(B.Y_LID, 0, B.Y_FRONT, H), "rib")
    gz = B.Z_GB
    v.poly(rect(B.Y_LID - B.GB_T, gz, B.Y_LID, gz + B.GB_L), "offcut")
    sy = B.Y_SPROCKET
    v.poly(rect(sy, B.Z_SHAFT - B.HUB_D / 2, sy + B.HUB_L, B.Z_SHAFT + B.HUB_D / 2), "tongue")
    v.poly(rect(sy + B.HUB_L, B.Z_SHAFT - B.R_FLANGE, sy + B.HUB_L + B.WHEEL_W, B.Z_SHAFT + B.R_FLANGE), "tongue")
    v.line((B.CHAIN_Y, B.Z_SHAFT - B.R_PITCH - 6), (B.CHAIN_Y, B.Z_SHAFT + 75), "guide g")
    v.tag((B.CHAIN_Y + 2, B.Z_SHAFT + 70), "chain", "note")

    v.dim((0, H + 6), (B.Y_FRONT, H + 6), f"B3 {B.Y_FRONT:.1f}",
          size("B3", "Box depth off the wall, to the lid's face", B.Y_FRONT, "derived"))
    v.dim((0, -10), (B.CHAIN_Y, -10), f"B4 {B.CHAIN_Y:.1f}",
          size("B4", "Wall to the chain's line: the shade's chain must hang this far out", B.CHAIN_Y, "derived"),
          lab=(0, 16))
    v.dim((B.Y_LID - B.GB_T, gz + B.GB_L + 4), (B.Y_LID, gz + B.GB_L + 4), "M2 25",
          size("M2", "Gearbox thickness (seller listing)", B.GB_T, LISTING), lab=(0, -6))
    v.dim((B.Y_LID, B.Z_SHAFT + B.R_FLANGE + 6), (B.Y_LID + B.SHAFT_L, B.Z_SHAFT + B.R_FLANGE + 6), "M7 14",
          size("M7", "Shaft length out of the gearbox (seller listing)", B.SHAFT_L, LISTING), lab=(0, -6))


def sprocket():
    v = View("The sprocket, from the front", 8)
    D.views.append(v)
    z = 0
    v.poly(ellipse(0, z, B.R_FLANGE, B.R_FLANGE, 0, 360), "part")
    v.poly(ellipse(0, z, B.R_PITCH + 0.6, B.R_PITCH + 0.6, 0, 360), "inner")
    v.poly(ellipse(0, z, B.R_PITCH, B.R_PITCH, 0, 360), "flat", close=False)
    for i in range(B.TEETH):
        a = 2 * math.pi * i / B.TEETH
        v.poly(ellipse(B.R_PITCH * math.sin(a), B.R_PITCH * math.cos(a), B.BEAD_D / 2, B.BEAD_D / 2, 0, 360, 20),
               "tongue")
    v.poly(ellipse(0, z, B.SHAFT_D / 2, B.SHAFT_D / 2, 0, 360, 24), "inner")

    p0 = (0, B.R_PITCH)
    a1 = 2 * math.pi / B.TEETH
    p1 = (B.R_PITCH * math.sin(a1), B.R_PITCH * math.cos(a1))
    v.dim((p0[0], p0[1] + 4), (p1[0], p1[1] + 4), "C2 6.0",
          size("C2", "Bead pitch, centre to centre (#10 chain; some brands 6.1-6.2)", B.BEAD_PITCH, LISTING),
          lab=(4, -8))
    v.dim((-B.BEAD_D / 2, -B.R_PITCH - 4.5), (B.BEAD_D / 2, -B.R_PITCH - 4.5), "C1 4.5",
          size("C1", "Bead diameter (#10 chain)", B.BEAD_D, LISTING), lab=(0, 16))
    v.dim((0, 0), (-B.R_PITCH * math.sin(a1 * 2), -B.R_PITCH * math.cos(a1 * 2)), f"C3 {B.R_PITCH:.2f}",
          size("C3", f"Pitch radius: bead centres, {B.TEETH} pockets", B.R_PITCH, "derived"), lab=(-30, 4))
    v.dim((-B.R_FLANGE, B.R_FLANGE + 3), (B.R_FLANGE, B.R_FLANGE + 3), f"C4 {2 * B.R_FLANGE:.1f}",
          size("C4", "Flange diameter", 2 * B.R_FLANGE, "derived"))
    size("C5", "Chain moved per sprocket turn", B.CHAIN_PER_TURN, "derived")


front()
side()
sprocket()
D.export(order="BMC")
