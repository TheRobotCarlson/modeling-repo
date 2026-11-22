"""AC remote battery cover: a copy of a working cover, for a second remote whose cover was lost.

The cover is a curved shell, open along the top and at the latch end. The floor is
flat in the middle and curves up into both long sides and the closed end. Two
cross ribs with scalloped tops press on the two AAA cells. At the open end, a
raised tongue with a ramp underneath latches into the remote, and a small block
sticks out of each corner. At the closed end, two hooks reach in under the remote's lip.

Sizes are the user's caliper measurements of the working cover unless marked
PHOTO (read off a photo against the caliper scale) or EST (guessed).

Millimetres. The cover lies open side up: outside of the floor at z = 0, the open
(latch) end towards +Y, the closed end towards -Y, centred on x = 0.
"""

import math

from build123d import (Align, Axis, Box, Cylinder, Plane, Polyline, Pos, Rot, extrude, fillet, make_face,
                       scale)

from modelkit import Assembly

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# --- shell -----------------------------------------------------------------------------
L = 62.3            # outside, closed end to open end, not counting the tongue
W = 48.6            # outside, across
H = 14.5            # outside of the floor to the rim
T_SIDE = 1.3        # long sides, at the rim; also the closed end's wall at the rim
T_FLOOR = 1.6
CURVE_SIDE = 15.2   # the floor is flat from this far in from each long side (outside)
CURVE_END = 17.2    # ... and from this far in from the closed end (outside)

# --- AAA cradle: two cross ribs with two scallops each ----------------------------------
RIB_T = 0.8
RIB_FRONT = 19.3            # open end (outside edge) to the front rib's inside face
RIB_SPAN = 27.2             # outside face to outside face of the two ribs
RIB_PEAK = 6.4              # rib height above the inside of the floor, at the middle peak
RIB_DIP = 4.8               # ... at the bottom of each scallop (may be a little lower)
CELL_D = 10.5               # AAA
RIB_W = 2 * CELL_D + 1.0    # EST: across, between the long ribs
SIDE_RIB_H = 1.9            # the long side ribs, and the front rib they meet
GUSSET_L = 6.0              # EST: triangle under the back holder's middle peak (full height), towards the cells

# --- latches ------------------------------------------------------------------------------
TONGUE_W = 6.1
TONGUE_OUT = 6.3            # past the open end
TONGUE_TOP = 5.0            # outside of the floor to the top face of the tongue
TONGUE_T = 1.7              # at its tip, and in the gap
TONGUE_PEAK = 3.0           # thickness at the catch: the ramp hangs below the tongue
TONGUE_RAIL = 1.0           # EST: the two supports under the tongue's edges, inside the cover, floor up to it
TONGUE_GAP = 1.1            # open end to the catch face: the remote's wall goes here
TONGUE_IN = 8.0             # how far inside the tongue runs, to the front rib
ANCHOR_W = 29.0             # PHOTO: the front rib, across; the side ribs meet it
CORNER = 2.2                # blocks in the open end's corners, 2.2 square, top flush with the rim
CORNER_OUT = 2.2            # ... sticking out past the open end
CORNER_L = 5.5              # ... and 5.5 long in all, the rest inside for strength
END_HOOK = (5.0, 3.9, 2.1)  # closed end: width, reach in from the wall, thickness
END_HOOK_SPAN = 37.5        # outer side of one hook to the outer side of the other
END_HOOK_EDGE = 10.5        # inner side of a hook to the cover's outside edge: a check, 10.55 from the others
END_HOOK_X = END_HOOK_SPAN / 2 - END_HOOK[0] / 2     # each hook's centre from the middle


def _rounded(w, l, h, sx, sy, sz):
    """Box w x l x h (bottom at z = 0) whose bottom long edges and -Y bottom edge curve up as
    quarter ellipses: sx across, sy along, both rising sz. Made by filleting a box in a stretched
    space and scaling back, so the corner where the curves meet stays smooth."""
    r = 10.0
    k = (sx / r, sy / r, sz / r)
    b = Pos(0, 0, 0) * Box(w / k[0], l / k[1], h / k[2] + 2.0, align=BASE)
    bottom = b.faces().sort_by(Axis.Z)[0]
    b = fillet([e for e in bottom.edges() if e.center().Y < l / k[1] / 2 - 0.1], r)
    b = scale(b, by=k)
    return b & Box(w, l, h, align=BASE)


def envelope():
    return _rounded(W, L, H, CURVE_SIDE, CURVE_END, H)


def shell():
    outer = envelope()
    # the inside: same curves, set in by the wall and floor, open at the top and the +Y end
    wi = W - 2 * T_SIDE
    inner = _rounded(wi, L, H, CURVE_SIDE - T_SIDE, CURVE_END - T_SIDE, H - T_FLOOR)
    inner = Pos(0, T_SIDE, T_FLOOR) * inner             # pokes out past the open end, so it is open
    inner += Pos(0, T_SIDE, H - 0.5) * Box(wi, L, 5, align=BASE)       # and clear above the rim
    return outer - inner


def cradle():
    """Two cross ribs, scalloped for the cells; the front rib; and the long side ribs, which run
    from the front rib back into the closed end's curve."""
    z0 = T_FLOOR
    y_front = L / 2 - RIB_FRONT + RIB_T / 2          # its inside face (towards the cells) at RIB_FRONT
    y_back = L / 2 - (RIB_FRONT - RIB_T) - RIB_SPAN + RIB_T / 2
    ribs = None
    for y in (y_front, y_back):
        r = Pos(0, y, z0) * Box(RIB_W, RIB_T, RIB_PEAK, align=BASE)
        ribs = r if ribs is None else ribs + r
    # each scallop is a cell-sized circle, sunk so its bottom is at RIB_DIP
    cz = z0 + RIB_DIP + CELL_D / 2
    for sx in (-1, 1):
        ribs -= Pos(sx * CELL_D / 2, (y_front + y_back) / 2, cz) * Rot(90, 0, 0) * Cylinder(
            CELL_D / 2, abs(y_front - y_back) + 4)
    y_anchor = L / 2 - TONGUE_IN                     # the front rib's face towards the cells
    ribs += Pos(0, y_anchor - RIB_T / 2, z0) * Box(ANCHOR_W, RIB_T, SIDE_RIB_H, align=BASE)
    side_len = y_anchor - (-L / 2)
    for sx in (-1, 1):
        side = Pos(sx * (RIB_W + RIB_T) / 2, y_anchor - side_len / 2, z0) * Box(RIB_T, side_len, SIDE_RIB_H,
                                                                               align=BASE)
        ribs += side & envelope()                    # stops where it runs into the curve
    # the back holder's triangle, under its middle peak, sloping down towards the open end
    yb = y_back + RIB_T / 2
    tri = Polyline((yb, z0), (yb + GUSSET_L, z0), (yb, z0 + RIB_PEAK), close=True)
    ribs += extrude(Plane.YZ.offset(-RIB_T / 2) * make_face(tri), RIB_T)
    return ribs


def tongue():
    """The latch: a plate from the front rib out past the open end, on two supports under its edges
    inside the cover. A ramp hangs below it, from the tip down to a catch face TONGUE_GAP from
    the end."""
    y0 = L / 2
    top = TONGUE_TOP                                 # the plate's top face
    low = TONGUE_TOP - TONGUE_PEAK                   # the bottom of the catch
    zp = top - TONGUE_T                              # its underside
    plate = Pos(0, y0 + (TONGUE_OUT - TONGUE_IN) / 2, zp) * Box(TONGUE_W, TONGUE_OUT + TONGUE_IN, TONGUE_T,
                                                                align=BASE)
    a, b = y0 + TONGUE_GAP, y0 + TONGUE_OUT
    ramp = Polyline((a, zp), (a, low), (b, zp), close=True)
    plate += extrude(Plane.YZ.offset(-TONGUE_W / 2) * make_face(ramp), TONGUE_W)
    for sx in (-1, 1):
        plate += Pos(sx * (TONGUE_W - TONGUE_RAIL) / 2, y0 - TONGUE_IN / 2, T_FLOOR) * Box(
            TONGUE_RAIL, TONGUE_IN, zp - T_FLOOR, align=BASE)
    return plate


def hooks():
    out = None
    for sx in (-1, 1):
        c = Pos(sx * (W / 2 - T_SIDE - CORNER / 2), L / 2 + CORNER_OUT - CORNER_L / 2, H - CORNER) * Box(
            CORNER, CORNER_L, CORNER, align=BASE)
        e = Pos(sx * END_HOOK_X, -L / 2 + T_SIDE + END_HOOK[1] / 2, H - END_HOOK[2]) * Box(*END_HOOK, align=BASE)
        out = c + e if out is None else out + c + e
    return out


def build():
    cover = shell() + cradle() + hooks()
    return {"cover": cover, "tongue": tongue() - cover}     # the anchor wall's ends meet the curved floor


def export():
    p = build()
    asm = Assembly("ac-remote-cover", "cover", title="AC remote cover",
                   description="Copy of the working cover: curved shell, AAA cradle ribs, a ramped latch tongue and four hooks.")
    asm.add("cover", p["cover"], "Cover shell", material="PLA", color="#e9ecef",
            description="Curved shell, 1.3 mm sides and 1.6 mm floor, with the cradle ribs and the four hooks.")
    asm.add("tongue", p["tongue"], "Latch tongue", material="PLA", color="#7fa7c9", explode=(0, 20, 0),
            description="Printed with the shell; shown apart so it is easy to see. Hangs from a cross wall 8 mm in.",
            notes=["where it is fixed: PHOTO"])
    asm.export()


if __name__ == "__main__":
    export()
