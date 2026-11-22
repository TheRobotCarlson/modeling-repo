"""Labelled drawing of the cover: three views and a table of every size the model uses.

Each size has a short code (S1, R2, T5 ...) so a measurement can be read back by
code. The numbers come straight from cover.py, so the drawing never disagrees with
the model. Writes data/ac-remote-cover/drawing/cover.json for <Drawing name="cover" />.
"""

import math

import cover as C
from modelkit.drawing import Drawing, ellipse, rect

D = Drawing("ac-remote-cover", "cover")
size = D.size

L, W, H, T, F = C.L, C.W, C.H, C.T_SIDE, C.T_FLOOR
y_open, y_closed = L / 2, -L / 2
front_in = y_open - C.RIB_FRONT                  # front rib, face towards the cells
front_out = front_in + C.RIB_T                   # ... and towards the open end
back_out = front_out - C.RIB_SPAN                # back rib, face towards the closed end
back_in = back_out + C.RIB_T
xr = C.RIB_W / 2
xl = (C.RIB_W + C.RIB_T) / 2
t_low, t_top = C.TONGUE_TOP - C.TONGUE_PEAK, C.TONGUE_TOP  # catch's lowest point; the plate's top
t_under = t_top - C.TONGUE_T                                # the plate's underside
anchor_y = y_open - C.TONGUE_IN
fx_side = W / 2 - C.CURVE_SIDE
fy_end = y_closed + C.CURVE_END


# ============================== 1. from above ==============================
def plan():
    v = D.view("From above, open end at the top")
    v.poly(rect(-W / 2, y_closed, W / 2, y_open), "part")
    v.poly(rect(-W / 2 + T, y_closed + T, W / 2 - T, y_open), "inner")
    v.poly(rect(-fx_side, fy_end, fx_side, y_open), "flat")
    for y0, y1 in ((front_in, front_out), (back_out, back_in)):
        v.poly(rect(-xr, y0, xr, y1), "rib")
    for s in (-1, 1):
        v.poly(rect(s * xl - C.RIB_T / 2, y_closed + T, s * xl + C.RIB_T / 2, anchor_y - C.RIB_T), "rib")
    tw = C.TONGUE_W / 2
    v.poly(rect(-tw, anchor_y, tw, y_open + C.TONGUE_OUT), "tongue")
    for s_ in (-1, 1):                            # its two supports, under it
        rx = s_ * (C.TONGUE_W - C.TONGUE_RAIL) / 2
        v.poly(rect(rx - C.TONGUE_RAIL / 2, anchor_y, rx + C.TONGUE_RAIL / 2, y_open), "offcut")
    v.poly(rect(-C.ANCHOR_W / 2, anchor_y - C.RIB_T, C.ANCHOR_W / 2, anchor_y), "guessed")
    for s in (-1, 1):
        x0 = s * (W / 2 - T)
        v.poly(rect(x0, y_open + C.CORNER_OUT, x0 - s * C.CORNER, y_open + C.CORNER_OUT - C.CORNER_L), "tongue")
        hx, (hw, hr, _) = s * C.END_HOOK_X, C.END_HOOK
        v.poly(rect(hx - hw / 2, y_closed + T, hx + hw / 2, y_closed + T + hr), "tongue")

    v.dim((-W / 2 - 4, y_closed), (-W / 2 - 4, y_open), "S1 62.3",
          size("S1", "Length, outside, closed end to open end", L, "measured"), lab=(-6, 4))
    v.dim((-W / 2, y_closed - 4), (W / 2, y_closed - 4), "S2 48.6",
          size("S2", "Width, outside", W, "measured"), lab=(0, 16))
    v.dim((W / 2, fy_end), (fx_side, fy_end), "C1 15.2",
          size("C1", "Side curve: outside edge to where the floor goes flat", C.CURVE_SIDE, "measured"))
    v.dim((W / 2 - 3, y_closed), (W / 2 - 3, fy_end), "C2 17.2",
          size("C2", "Closed-end curve: outside of the end to where the floor goes flat", C.CURVE_END, "measured"))
    v.dim((W / 2 + 4, y_open), (W / 2 + 4, front_in), "R1 19.3",
          size("R1", "Open end (outside edge) to the front cross rib's inside face, the one towards the cells",
               C.RIB_FRONT, "measured"))
    for yy in (y_open, front_in):
        v.guide((xr, yy), (W / 2 + 5, yy), "m")
    v.dim((-xr - 4, back_out), (-xr - 4, front_out), "R2 27.2",
          size("R2", "The two cross ribs, outside face to outside face", C.RIB_SPAN, "measured"), lab=(-6, 4))
    v.dim((xr + 1, y_closed), (xr + 1, back_out), f"R7 {back_out - y_closed:.1f}",
          size("R7", "Closed end (outside) to the back rib's outside face. Follows from S1, R1, R2 and R3; "
                     "C2 says the curve ends 0.6 mm further in", round(back_out - y_closed, 1), "derived"))
    v.dim((-xr, front_in - 3), (xr, front_in - 3), f"R6 {C.RIB_W:.1f}",
          size("R6", "Cross ribs, length across", C.RIB_W, "photo / guess"))
    v.tag((xl, -3), "L1 L2", size("L1", "Long side ribs: height. They support both holders, run from the front "
                                        "rib back into the closed end's curve", C.SIDE_RIB_H, "measured"), dx=6)
    size("L2", f"Long side ribs: centre from the middle ({C.RIB_T} thick, just outside the holders)", round(xl, 1),
                                     "photo / guess")
    v.dim((-tw, y_open + C.TONGUE_OUT + 2), (tw, y_open + C.TONGUE_OUT + 2), "T1 6.1",
          size("T1", "Tongue width", C.TONGUE_W, "measured"))
    v.dim((tw + 2, y_open), (tw + 2, y_open + C.TONGUE_OUT), "T2 6.3",
          size("T2", "Tongue: how far it sticks out past the open end", C.TONGUE_OUT, "measured"))
    v.dim((-C.ANCHOR_W / 2, anchor_y - 4), (C.ANCHOR_W / 2, anchor_y - 4), f"T8 {C.ANCHOR_W:g}",
          size("T8", "Front rib: width across. The side ribs meet it; 1.9 tall like L1", C.ANCHOR_W,
               "photo / guess"))
    v.dim((-C.ANCHOR_W / 2 - 1, y_open), (-C.ANCHOR_W / 2 - 1, anchor_y), f"T7 {C.TONGUE_IN:g}",
          size("T7", "Open end to the front rib, where the tongue and its supports end", C.TONGUE_IN,
               "photo / guess"))
    kx = W / 2 - T - C.CORNER
    v.dim((kx - 1, y_open), (kx - 1, y_open + C.CORNER_OUT), "K1 2.2",
          size("K1", "Corner blocks: how far they stick out past the open end (2.2 square, top flush with the rim)",
               C.CORNER_OUT, "measured"), lab=(-6, 4))
    v.dim((kx - 7, y_open + C.CORNER_OUT - C.CORNER_L), (kx - 7, y_open + C.CORNER_OUT), "K2 5.5",
          size("K2", "Corner blocks: length in all, the part inside adds strength", C.CORNER_L, "measured"),
          lab=(-6, 4))
    v.dim((-C.END_HOOK_X - C.END_HOOK[0] / 2, y_closed + T + 5.9), (-C.END_HOOK_X + C.END_HOOK[0] / 2,
          y_closed + T + 5.9), "H1 5", size("H1", "Closed-end hooks: width", C.END_HOOK[0], "measured"))
    v.tag((C.END_HOOK_X, y_closed + T + C.END_HOOK[1]), "H2",
          size("H2", "Closed-end hooks: reach in from the end wall's inside", C.END_HOOK[1], "measured"), dx=-8, dy=-6)
    hin = C.END_HOOK_X - C.END_HOOK[0] / 2               # a hook's inner side, from the middle
    v.dim((-W / 2, y_closed + 14), (-hin, y_closed + 14), "H4 10.5",
          size("H4", "Inner side of a closed-end hook to the cover's outside edge (model: "
                     f"{W / 2 - hin:.2f}, from H5 and H1)", C.END_HOOK_EDGE, "measured"))
    v.dim((-C.END_HOOK_SPAN / 2, y_closed + 10.5), (C.END_HOOK_SPAN / 2, y_closed + 10.5), "H5 37.5",
          size("H5", "Outer side of one closed-end hook to the outer side of the other", C.END_HOOK_SPAN,
               "measured"))
    v.tag((-fx_side, fy_end), "floor flat inside the dashed line", "note", dx=-4, dy=16)
    return v


# ============================== 2. lengthwise cut ==============================
def lengthwise():
    v = D.view("Cut lengthwise down the middle, closed end left, open end right")
    outer = [(y_open, 0), (fy_end, 0)] + ellipse(fy_end, H, C.CURVE_END, H, 270, 180)
    inner = ellipse(fy_end, H, C.CURVE_END - T, H - F, 180, 270) + [(fy_end, F), (y_open, F)]
    v.poly(outer + inner, "part")
    for y0, y1 in ((front_in, front_out), (back_out, back_in)):
        v.poly(rect(y0, F, y1, F + C.RIB_PEAK), "rib")
    a, b = y_open + C.TONGUE_GAP, y_open + C.TONGUE_OUT
    v.poly([(anchor_y, t_under), (a, t_under), (a, t_low), (b, t_under), (b, t_top), (anchor_y, t_top)], "tongue")
    v.poly(rect(y_open - C.TONGUE_IN, F, y_open, t_under), "offcut")
    v.poly(rect(anchor_y - C.RIB_T, F, anchor_y, F + C.SIDE_RIB_H), "guessed")
    v.poly([(back_in, F), (back_in + C.GUSSET_L, F), (back_in, F + C.RIB_PEAK)], "guessed")
    v.poly(rect(y_closed + T, H - C.END_HOOK[2], y_closed + T + C.END_HOOK[1], H), "offcut")

    v.dim((y_closed - 4, 0), (y_closed - 4, H), "S3 14.5",
          size("S3", "Depth: outside of the floor to the rim", H, "measured"), lab=(-6, 4))
    v.dim((4, 0), (4, F), "S5 1.6", size("S5", "Floor thickness", F, "measured"))
    v.dim((y_closed, H + 1.5), (y_closed + T, H + 1.5), "S6 1.3",
          size("S6", "Closed-end wall at the rim", T, "measured"), lab=(-8, 4))
    rows = [(-3, y_closed, fy_end, "C2 17.2", "m"), (-7, y_closed, back_out, f"R7 {back_out - y_closed:.1f}", "d"),
            (-11, back_out, front_out, "R2 27.2", "m"), (-15, front_in, y_open, "R1 19.3", "m")]
    for z, p, q, s, c in rows:
        v.dim((p, z), (q, z), s, c)
    for yy, z, c in ((fy_end, -3, "m"), (back_out, -7, "d"), (front_out, -11, "m"), (front_in, -15, "m")):
        v.guide((yy, F), (yy, z), c)
    v.dim((front_out + 1.5, F), (front_out + 1.5, F + C.RIB_PEAK), "R4 6.4",
          size("R4", "Cross rib height above the inside of the floor, at the middle peak", C.RIB_PEAK, "measured"),
          lab=(-26, 4))
    v.tag((front_in, F + C.RIB_PEAK), "R3 0.8", size("R3", "Cross rib thickness", C.RIB_T, "measured"),
          dx=-6, dy=-6, anchor="end")
    v.dim((b + 2, 0), (b + 2, t_low), f"T11 {t_low:.1f}",
          size("T11", "Outside of the floor to the tongue's lowest point, the bottom of the catch: T3 - T5",
               round(t_low, 1), "derived"), lab=(6, 16))
    v.guide((a, t_low), (b + 2.5, t_low), "m")
    v.dim((b + 0.4, t_under), (b + 0.4, t_top), "", "m")
    v.tag((b, t_top), "T4 1.7", size("T4", "Tongue thickness at the tip, and in the gap", C.TONGUE_T, "measured"),
          dx=8, dy=-2)
    v.dim((a - 0.5, t_low), (a - 0.5, t_top), "", "m")
    v.tag((b + 3, t_low + 0.6), "T5 3.0 at the catch",
          size("T5", "Tongue thickness at the catch: the ramp hangs below it", C.TONGUE_PEAK, "measured"),
          dx=4, dy=4)
    v.dim((y_open, t_top + 1.5), (a, t_top + 1.5), "T6 1.1",
          size("T6", "Open end to the catch face: the gap the remote's wall drops into", C.TONGUE_GAP, "measured"),
          lab=(0, -6))
    v.tag((y_open - C.TONGUE_IN / 2, 0), "T10",
          size("T10", f"Two supports under the tongue's edges, inside the cover (dashed: either side of this cut): "
                      f"{C.TONGUE_RAIL} thick each, floor up to the tongue", C.TONGUE_RAIL, "photo / guess"),
          dx=0, dy=16, anchor="middle")
    v.dim((anchor_y - 3, 0), (anchor_y - 3, t_top), f"T3 {t_top:.1f}",
          size("T3", "Outside of the floor to the top face of the tongue", C.TONGUE_TOP, "measured"), lab=(-6, 4))
    v.guide((anchor_y, t_top), (anchor_y - 3.5, t_top), "m")
    v.tag((back_in + C.GUSSET_L, F), "G1",
          size("G1", f"Triangle support behind the back holder's middle peak: {C.RIB_T} thick, {C.GUSSET_L:g} long, "
                     f"reaching the full peak height (measured); length", C.GUSSET_L, "photo / guess"), dx=2, dy=-4)
    v.tag((y_closed + T + C.END_HOOK[1], H - C.END_HOOK[2]), "H2 3.9, H3 2.1 (dashed: 16 mm off this cut)", "m",
          dx=6, dy=4)
    size("H3", "Closed-end hooks: thickness, top flush with the rim", C.END_HOOK[2], "measured")
    return v


# ============================== 3. cut across ==============================
def across():
    v = D.view("Cut across, looking at a cross rib")
    outer = [(-fx_side, 0), (fx_side, 0)] + ellipse(fx_side, H, C.CURVE_SIDE, H, 270, 360) + [(W / 2 - T, H)] + \
        ellipse(fx_side, H, C.CURVE_SIDE - T, H - F, 360, 270) + [(-fx_side, F)] + \
        ellipse(-fx_side, H, C.CURVE_SIDE - T, H - F, 270, 180) + [(-W / 2, H)] + \
        ellipse(-fx_side, H, C.CURVE_SIDE, H, 180, 270)
    v.poly(outer, "part")
    r = C.CELL_D / 2
    cz = F + C.RIB_DIP + r
    half = math.degrees(math.acos((cz - F - C.RIB_PEAK) / r))
    rib = [(-xr, F), (xr, F), (xr, F + C.RIB_PEAK)]
    for s in (1, -1):
        rib += ellipse(s * r, cz, r, r, 270 + half, 270 - half, 30)
    rib += [(-xr, F + C.RIB_PEAK)]
    v.poly(rib, "rib")
    for s in (-1, 1):
        v.poly(ellipse(s * r, cz, r, r, 0, 360, 60), "cell")
        v.poly(rect(s * xl - C.RIB_T / 2, F, s * xl + C.RIB_T / 2, F + C.SIDE_RIB_H), "rib")
    v.dim((W / 2 - T, H + 1.5), (W / 2, H + 1.5), "S4 1.3",
          size("S4", "Long side wall at the rim", T, "measured"), lab=(10, 4))
    v.dim((W / 2, -2), (fx_side, -2), "C1 15.2", "m", lab=(0, 16))
    v.dim((-r, F), (-r, F + C.RIB_DIP), "R5 4.8",
          size("R5", "Cross rib height at the bottom of each scallop (may be a little lower)", C.RIB_DIP, "measured"),
          lab=(-4, 4))
    v.dim((0.4, F), (0.4, F + C.RIB_PEAK), "R4 6.4", "m")
    v.tag((r, cz + r), "AAA cells, dashed", "note", dx=40, dy=-4)
    size("R8", "Scallop shape: round, AAA size, so the cells sit in them", C.CELL_D, "photo / guess")
    v.tag((xl, F + C.SIDE_RIB_H), "L1", "m", dx=4, dy=-4)
    return v


def main():
    plan()
    lengthwise()
    across()
    D.export(order="SCRLGTKH")


if __name__ == "__main__":
    main()
