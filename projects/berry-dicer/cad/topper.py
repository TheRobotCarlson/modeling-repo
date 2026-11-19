"""Manual topper: a row of berries against a fence, one swing of a wire.

Lay the berries on their sides in the stainless tray, leafy end against the fence.
Swing the wire arm down: the wire goes through every berry 7 mm from the fence and
into the slot, so each loses the same 5 mm whatever its size. Flip the fence flap
forward to drop the tops into the compost, then tip the tray into the press's hopper.
The tray is as wide as the hopper.
"""

import math

from build123d import Box, Cylinder, Pos, Rot

from _steel import BASE, CAP, SLOT_W, T125, TOP_D, TOP_W, TRAY_T, WIRE_D, berries, tray
from modelkit import Assembly

Z_BED = 30.0
Y_FENCE = -60.0
PIVOT = (70.0, Z_BED + 18.0)        # wire arm pivot (y, z): about half a berry's height up
ARM_X = TOP_W / 2 + 12.0
UP_DEG = 22.0


def wire_radius(slot_y):
    """The arm length that puts the wire through the slot centre at bed level."""
    return math.hypot(PIVOT[0] - slot_y, PIVOT[1] - Z_BED)


def arm_at(deg, r):
    """Wire arm rotated deg above the pivot's horizontal, pointing to -Y."""
    y = PIVOT[0] - r * math.cos(math.radians(deg))
    z = PIVOT[1] + r * math.sin(math.radians(deg))
    return y, z


def build(arm_deg=UP_DEG):
    p = {}
    p["tray"], p["flap"], slot_y = tray(Y_FENCE, Z_BED, -1)
    r = wire_radius(slot_y)
    a0 = math.degrees(math.atan2(PIVOT[1] - Z_BED, PIVOT[0] - slot_y))   # angle below horizontal at the slot
    wy, wz = arm_at(arm_deg, r)
    p["wire"] = Pos(0, wy, wz) * Rot(0, 90, 0) * Cylinder(WIRE_D / 2, 2 * ARM_X - 3)
    arms = None
    ang = math.atan2(wz - PIVOT[1], wy - PIVOT[0])
    mid = ((wy + PIVOT[0]) / 2, (wz + PIVOT[1]) / 2)
    for sx in (-1, 1):
        a = Pos(sx * ARM_X, *mid) * Rot(math.degrees(ang), 0, 0) * Box(T125, r + 16, 14)
        a += Pos(sx * ARM_X, *PIVOT) * Rot(0, 90, 0) * Cylinder(9, T125)
        arms = a if arms is None else arms + a
    hy, hz = arm_at(arm_deg + 12.0, r + 18)          # handle tube, ahead of and above the wire
    arms += Pos(0, hy, hz) * Rot(0, 90, 0) * Cylinder(6, 2 * ARM_X + T125)
    for sx in (-1, 1):
        a = math.atan2(hz - wz, hy - wy)
        arms += Pos(sx * ARM_X, (hy + wy) / 2, (hz + wz) / 2) * Rot(math.degrees(a), 0, 0) * Box(T125, math.hypot(hy - wy, hz - wz) + 12, 12)
    p["pins"] = Pos(0, *PIVOT) * Rot(0, 90, 0) * Cylinder(3, 2 * ARM_X + 20)
    p["arm"] = arms - p["pins"]

    base = Pos(0, 0, 0) * Box(TOP_W + 70, 160, Z_BED - TRAY_T, align=BASE)
    base -= Pos(0, slot_y, Z_BED - TRAY_T - 8) * Box(2 * ARM_X + 4, SLOT_W + 2, 10, align=BASE)     # wire runs out here
    base -= Pos(0, 5, Z_BED - TRAY_T - 3) * Box(TOP_W + 2 * TRAY_T + 1, TOP_D + 12, 4, align=BASE)  # tray pocket
    for sx in (-1, 1):
        post = Pos(sx * (ARM_X + T125 / 2 + 6), PIVOT[0], Z_BED - TRAY_T - 1) * Box(10, 26, PIVOT[1] - Z_BED + 14, align=BASE)
        base += post
    base -= Pos(0, 0, 0) * Box(TOP_W + 40, 130, Z_BED - TRAY_T - 6, align=BASE)        # hollow underneath
    base -= p["pins"]
    for sx in (-1, 1):                 # the arms swing down into these slots; their floor is the stop
        base -= Pos(sx * ARM_X, (PIVOT[0] - 12 - 95) / 2, 8.0) * Box(T125 + 3, PIVOT[0] - 12 + 95, 40, align=BASE)
    p["base"] = base
    p["berries"] = berries(Y_FENCE + TRAY_T, Z_BED, -1, n=9)
    return p


def export(p):
    asm = Assembly("berry-dicer", "topper", title="Topper, manual",
                   description="A row of nine berries against a fence; one swing of a wire takes 5 mm off every leafy end.")
    food = dict(material="Stainless 304", source="machined")
    asm.add("tray", p["tray"], "Tray", color="#c9ced4", explode=(0, 0, 25), **food,
            description="0.060 in 304, bent: a 312 mm bed with side walls, as wide as the hopper.",
            notes=["Laser cut and bent (SendCutSend)", "Dishwasher"])
    asm.add("flap", p["flap"], "Fence flap", color="#b5bcc4", explode=(0, -30, 25), **food,
            description=f"The fence and the {CAP:.0f} mm strip in front of the slot. Hinges forward to drop the tops off.",
            notes=["Dishwasher"])
    asm.add("wire", p["wire"], "Cutting wire", color="#5b636c", material="Stainless 304", source="bought",
            explode=(0, 0, 50), description="0.5 mm stainless wire between the arm tips, tensioned by a screw.",
            notes=["EST: gauge"])
    asm.add("arm", p["arm"], "Wire arm", color="#aab1b9", explode=(0, 0, 50), **food,
            description="Two 1/8 in 304 arms and a handle tube. Swings down through the slot.", notes=["Dishwasher"])
    asm.add("pins", p["pins"], "Pivot rod", color="#7d838c", material="Stainless 304", source="bought",
            explode=(0, 0, 50), description="6 mm stainless rod through both arms and the posts.")
    asm.add("base", p["base"], "Base", material="PLA", color="#f1d9c6",
            description="Holds the tray, the pivot posts and the arm stops. PLA Pure, wipe clean.")
    asm.add("berries", p["berries"], "Berries", color="#d63b3b", source="bought", layer="Berries",
            description="Nine berries, 24 to 36 mm across, leafy end on the fence.", notes=["reference only"])
    asm.export()


if __name__ == "__main__":
    export(build())
