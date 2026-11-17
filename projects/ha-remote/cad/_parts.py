"""Shared pieces for both remotes: bought parts, and the printed keypad.

Bought-part sizes marked SOURCE come from a datasheet or the Seeed wiki; everything
marked EST is a stand-in until the real part is on a caliper (see the measure page).
Every function builds in a local frame: centred on X/Y, sitting on z = 0.
"""

import math

from build123d import (Align, Axis, Box, Circle, Cylinder, Polygon, Pos, Rot, Sphere, extrude,
                       offset)

BASE = (Align.CENTER, Align.CENTER, Align.MIN)

# --- Seeed XIAO ESP32S3 stacked on the Wio-SX1262 board ------------------------------
# Local frame: USB-C points to +X, z = 0 is the underside of the Wio board's parts.
KIT_L, KIT_W = 21.0, 17.8          # SOURCE: Seeed wiki, "21 x 17.8mm"
PCB = 1.0                          # EST
WIO_UNDER = 1.2                    # EST: parts on the Wio board's underside
B2B = 2.0                          # EST: board-to-board connector, mated height
CAN = 2.4                          # EST: RF shield on the XIAO
USB_W, USB_H, USB_L, USB_OUT = 9.0, 3.2, 7.4, 1.0   # EST: USB-C receptacle, overhang past PCB
KIT_H = WIO_UNDER + PCB + B2B + PCB + USB_H         # 8.4 mm tall
Z_XIAO_TOP = WIO_UNDER + 2 * PCB + B2B              # top face of the XIAO board
Z_USB = Z_XIAO_TOP + USB_H / 2                      # USB-C centre height


def kit():
    """(wio, xiao, usb) shapes of the radio kit."""
    z1 = WIO_UNDER
    wio = Pos(-1, 0, z1 / 2) * Box(14, 13, z1)
    wio += Pos(0, 0, z1 + PCB / 2) * Box(KIT_L, KIT_W, PCB)
    wio += Pos(-7.5, 5.8, z1 + PCB + 0.6) * Cylinder(1.3, 1.2)          # LoRa U.FL (EST position)
    z2 = z1 + PCB
    xiao = Pos(-2, 0, z2 + B2B / 2) * Box(9, 3.5, B2B)                   # B2B connector
    xiao += Pos(0, 0, z2 + B2B + PCB / 2) * Box(KIT_L, KIT_W, PCB)
    xiao += Pos(-3.5, 0, Z_XIAO_TOP + CAN / 2) * Box(12, 12.5, CAN)
    xiao += Pos(-8.3, -6.3, Z_XIAO_TOP + 0.6) * Cylinder(1.3, 1.2)       # Wi-Fi U.FL
    usb = Pos(KIT_L / 2 + USB_OUT - USB_L / 2, 0, Z_USB) * Box(USB_L, USB_W, USB_H)
    usb = usb.fillet(1.2, usb.edges().filter_by(Axis.X))
    return wio, xiao, usb


# --- LiPo cell: Adafruit 2750, 3.7 V 350 mAh, protection circuit built in -----------
BATT_L, CELL_W, CELL_T = 36.0, 19.6, 5.2     # SOURCE: Adafruit product page


def battery():
    """Cell along X; the lead leaves from the +X end."""
    cell = Pos(0, 0, CELL_T / 2) * Box(BATT_L, CELL_W, CELL_T)
    return cell.fillet(1.0, cell.edges().filter_by(Axis.X))


# --- Tactile switches ---------------------------------------------------------------
def tact(size):
    """Omron B3F tact switch, legs trimmed (SOURCE: Omron B3F datasheet).

    12: B3F-4055, 12 x 12 mm body 4.3 mm tall, 3.8 mm square plunger to 7.3 mm,
        two 1.8 mm positioning bosses underneath (their length is not given: EST 1 mm).
    6:  B3F-1020, 6 x 6 mm body 3.5 mm tall, 3.5 mm round plunger to 5.0 mm.
    """
    if size == 12:
        sw = Pos(0, 0, 4.3 / 2) * Box(12, 12, 4.3)
        sw += Pos(0, 0, 4.3 + 1.5) * Box(3.8, 3.8, 3.0)
        for y in (-4.5, 4.5):
            sw += Pos(0, y, -1.0) * Cylinder(0.9, 1.0, align=BASE)
        return sw, 7.3
    sw = Pos(0, 0, 3.5 / 2) * Box(6, 6, 3.5)
    sw += Pos(0, 0, 3.5) * Cylinder(1.75, 1.5, align=BASE)
    return sw, 5.0


# --- FPC antennas (the kit ships one Wi-Fi and one LoRa) ------------------------------
FPC_T = 0.3
WIFI_FPC = (35.0, 9.0)    # EST length x width
LORA_FPC = (45.0, 10.0)   # EST


def fpc_arc(r, length, width, angle_deg, z0):
    """Antenna stuck to the inside of a round wall of radius r, centred at angle_deg."""
    span = length / r * 57.29578
    ring = Pos(0, 0, z0) * (Cylinder(r, width, align=BASE) - Cylinder(r - FPC_T, width, align=BASE))
    a0, a1 = angle_deg - span / 2, angle_deg + span / 2
    pts = [(0, 0)] + [(2 * r * math.cos(math.radians(a0 + (a1 - a0) * i / 12)),
                       2 * r * math.sin(math.radians(a0 + (a1 - a0) * i / 12))) for i in range(13)]
    wedge = Pos(0, 0, z0 - 1) * extrude(Polygon(*pts, align=None), width + 2)
    return ring & wedge


def fpc_flat(x_wall, y0, length, width, z0, side):
    """Antenna stuck flat to a straight side wall at x = x_wall, running +Y from y0."""
    return Pos(x_wall - side * FPC_T / 2, y0 + length / 2, z0 + width / 2) * Box(FPC_T, length, width)


# --- The keypad: rigid caps floating in a TPU panel, printed in one go with the shell ---
def slab(face, z0, z1):
    return Pos(0, 0, z0) * extrude(face, z1 - z0)


def keypad(top, panel, caps, groove=2.6, wall=0.8, depth=2.4, cap_t=2.0,
           panel_t=1.0, flange=1.5, dish=0.5):
    """Build the TPU panel and the caps.

    panel: 2D region of the shell's top that becomes TPU. caps: list of
    (2D outline, (x, y) stem centre, stem radius, stem bottom z).
    Around each cap the panel dips into a U-shaped channel `groove` wide and
    `depth` deep with `wall`-thick walls; that U is the spring and the seal.
    The panel's edge runs `flange` under the shell's top as a lap joint.

    Returns (tpu, [cap solids], plate_cut) where plate_cut is what to remove
    from the shell's top plate to make room for the panel.
    """
    lap = offset(panel, flange)
    tpu = slab(lap, top - 2 * panel_t, top - panel_t) + slab(panel, top - panel_t, top)
    cap_solids = []
    for outline, (cx, cy), stem_r, stem_z in caps:
        out = offset(outline, groove)
        tpu -= slab(out, top - depth - 1, top + 1)
        tpu += slab(out - offset(outline, groove - wall), top - depth, top)   # outer wall
        tpu += slab(offset(outline, wall) - outline, top - depth, top)        # inner wall
        tpu += slab(out - outline, top - depth, top - depth + wall)           # bottom
        cap = slab(outline, top - cap_t, top)
        cap += Pos(cx, cy, stem_z) * Cylinder(stem_r, top - cap_t - stem_z + 0.01, align=BASE)
        if dish:
            r = 60.0
            cap -= Pos(cx, cy, top - dish + r) * Sphere(r)
        cap_solids.append(cap)
    plate_cut = slab(panel, top - panel_t, top + 1) + slab(lap, top - 2 * panel_t - 0.01, top - panel_t)
    return tpu, cap_solids, plate_cut


def screw_m2(x, y, z_head, length=8.0):
    """M2 x 8 pan-head thread-forming screw for plastic (McMaster 99461A916: head 3.5 x 1.4)."""
    s = Pos(x, y, z_head) * Cylinder(1.75, 1.4, align=BASE)
    s += Pos(x, y, z_head + 1.4) * Cylinder(0.95, length, align=BASE)
    return s


__all__ = ["kit", "battery", "tact", "fpc_arc", "fpc_flat", "keypad", "slab", "screw_m2",
           "Circle", "Rot"]
