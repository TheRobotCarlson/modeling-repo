"""The bar: five buttons, 44 x 120 mm and 15 mm thick.

Same construction as the puck. The shell, a TPU keypad panel and five caps print
as one piece, top face down. The base screws on from below and hooks under the
top end with a tongue, so the end under the buttons cannot spring away.

Layout, top to bottom: one round main button, a 2 x 2 block of square keys, then
the battery, then the radio kit with USB-C in the bottom end. The antennas lie
along the side walls beside the battery.
"""

from build123d import Axis, Box, Circle, Pos, RectangleRounded, Rot, extrude, offset

from _parts import (BASE, BATT_L, CAP_BODY, CELL_W, GAP_Z, KIT_L, KIT_W, LORA_FPC, RES_D, RES_L,
                    USB_OUT, WIFI_FPC, Z_USB, battery, capacitor, fpc_flat, keypad, kit, pad,
                    resistor_y, screw_m2, slab, tact, wire)
from modelkit import Assembly
from puck import wiring_parts

W, L, CORNER = 44.0, 120.0, 14.0
WALL, TOP_T, BASE_T = 2.0, 2.0, 2.0
H = 15.0
IN_W, IN_L = W - 2 * WALL, L - 2 * WALL
FIT = 0.2
STEM_Z, SW_GAP = 11.5, 0.2

MAIN = (0.0, 44.0)
KEYS = [(-8.0, 25.0), (8.0, 25.0), (-8.0, 8.0), (8.0, 8.0)]
MAIN_R, KEY = 8.5, 11.0
BOSSES = [(-16.8, 16.0), (16.8, 16.0), (-14.5, -48.0), (14.5, -48.0)]
BOSS_R = 2.5

KIT_Y = -(IN_L / 2) + 0.7 + KIT_L / 2 + USB_OUT     # USB face 0.7 mm inside the end wall
BATT_Y = -15.4
TONGUE_W = 14.0


def plan(w, l, r):
    return RectangleRounded(w, l, r)


def build():
    p = {}
    # --- bought parts --------------------------------------------------------------
    kloc = Pos(0, KIT_Y, BASE_T) * Rot(0, 0, -90)
    wio, xiao, usb = (kloc * s for s in kit())
    p["wio"], p["xiao"], p["usb"] = wio, xiao, usb
    p["battery"] = Pos(0, BATT_Y, BASE_T) * Rot(0, 0, -90) * battery()     # leads toward the kit
    sw, sw_h = tact(6)
    sw_z = STEM_Z - SW_GAP - sw_h
    switches = [Pos(x, y, sw_z) * sw for x, y in [MAIN, *KEYS]]
    p["switches"] = switches[0] + switches[1] + switches[2] + switches[3] + switches[4]
    p["fpc-wifi"] = fpc_flat(IN_W / 2, -36.0, *WIFI_FPC, 3.0, +1)
    p["fpc-lora"] = fpc_flat(-IN_W / 2, -46.0, *LORA_FPC, 2.5, -1)

    # --- shell ---------------------------------------------------------------------
    shell = extrude(plan(W, L, CORNER), H)
    shell = shell.fillet(3.5, shell.edges().group_by(Axis.Z)[-1])
    shell = shell.fillet(1.0, shell.edges().group_by(Axis.Z)[0])
    shell -= extrude(plan(IN_W, IN_L, CORNER - WALL), H - TOP_T)
    for x, y in BOSSES:
        top = H - TOP_T if y < 0 else H - 3.0          # the upper pair stops short of the keypad
        sx = 1 if x > 0 else -1
        shell += Pos(x, y, BASE_T) * Cylinder_(BOSS_R, top - BASE_T + 0.01)
        shell += Pos((x + sx * IN_W / 2) / 2 + sx * 0.5, y, BASE_T) * Box(abs(IN_W / 2 - abs(x)) + 1.0, 1.6, top - BASE_T + 0.01, align=BASE)
        shell -= Pos(x, y, BASE_T - 0.01) * Cylinder_(0.8, 9.0)
    port = Pos(0, -(IN_L / 2) - 1, BASE_T + Z_USB) * Box(9.8, 6, 4.0)
    shell -= port.fillet(1.6, port.edges().filter_by(Axis.Y))
    shell -= Pos(0, IN_L / 2 - 0.2, 0.6) * Box(TONGUE_W + 0.6, 1.8, 1.6, align=(BASE[0], BASE[2], BASE[2]))   # slot for the base's tongue
    shell -= Pos(6.0, KIT_Y - 7.0, H - TOP_T - 0.01) * Cylinder_(1.6, TOP_T - 0.6)          # light window (EST)

    caps = [(Circle(8.5).moved(Pos(*MAIN)), MAIN, 1.6, STEM_Z)]
    caps += [(RectangleRounded(KEY, KEY, 3.0).moved(Pos(x, y)), (x, y), 1.6, STEM_Z) for x, y in KEYS]
    panel = RectangleRounded(33.0, 57.5, 9.0).moved(Pos(0, 27.25))
    tpu, cap_solids, cut = keypad(H, panel, caps, groove=2.2, wall=0.7, depth=2.2)
    shell -= cut
    p["shell"], p["panel"] = shell, tpu
    p["cap-main"] = cap_solids[0]
    for i, c in enumerate(cap_solids[1:], 1):
        p[f"cap-{i}"] = c

    # --- base ----------------------------------------------------------------------
    base = extrude(plan(IN_W - 2 * FIT, IN_L - 2 * FIT, CORNER - WALL - FIT), BASE_T)
    base += Pos(0, IN_L / 2 - FIT, 0.8) * Box(TONGUE_W, 1.4 + FIT, 1.2, align=(BASE[0], BASE[2], BASE[2]))
    for x, y in [MAIN, *KEYS]:
        ped = Pos(x, y, BASE_T) * Box(8, 8, sw_z + 0.6 - BASE_T, align=BASE)
        ped -= Pos(x, y, sw_z) * Box(6.2, 6.2, 1, align=BASE)
        ped -= Pos(x, y, sw_z - 1.0) * Box(2.0, 9, 2, align=BASE)     # leg and wire channel
        base += ped
    for sx in (-1, 1):
        base += Pos(sx * (CELL_W / 2 + 1.0), BATT_Y, BASE_T) * Box(1.2, 20, 3, align=BASE)
        base += Pos(sx * (KIT_W / 2 + 1.0), KIT_Y + 1.5, BASE_T) * Box(1.2, 13, 3, align=BASE)
    stop_y = (BATT_Y - BATT_L / 2 + KIT_Y + KIT_L / 2) / 2
    for sx in (-1, 1):                     # between battery and kit, apart so the battery wires pass
        base += Pos(sx * 7.0, stop_y, BASE_T) * Box(4, 0.8, 4, align=BASE)
    grip = None
    for sx in (-1, 1):
        g = Pos(sx * (KIT_W / 2 + 0.18), KIT_Y + 1.5, BASE_T + 0.5) * Box(0.4, 9, 2.5, align=BASE)
        grip = g if grip is None else grip + g
    for x, y in [(-13, 40), (13, 40), (-13, -30), (13, -30)]:
        foot = Pos(x, y, -0.6) * Cylinder_(4.0, 1.2)
        base -= foot
        grip += foot
    screws = None
    for x, y in BOSSES:
        base -= Pos(x, y, -0.01) * Cylinder_(1.2, BASE_T + 0.1)
        base -= Pos(x, y, -0.01) * Cylinder_(2.1, 1.7)
        s = screw_m2(x, y, 0.1)
        screws = s if screws is None else screws + s
    p["base"], p["grip"], p["screws"] = base, grip, screws
    p.update(wiring(kloc, sw_z))
    return p


def wiring(kloc, sw_z):
    """Wires, as they could be run. Paths are a plan, not a measurement.

    The battery leads go straight from the cell's end into the gap between the
    boards. Six wires (ground and D1 - D5) leave the XIAO's edge pads, climb over
    the USB-C port and run up the middle in a flat ribbon, over the battery, to the
    keys, dropping to each switch. The divider lies on the floor right of the
    battery and grounds to key 4.
    """
    under = GAP_Z + BASE_T + 0.4
    gap = GAP_Z + BASE_T
    zl, zs = 10.9, sw_z + 1.3                   # ribbon height; where wires meet a switch's side
    zr = BASE_T + RES_D / 2 + 0.05
    bp, bn, g = pad(kloc, "BAT+"), pad(kloc, "BAT-"), pad(kloc, "GND")
    ds = [pad(kloc, f"D{i}") for i in range(6)]
    cell = BATT_Y - BATT_L / 2
    face = 3.0                                  # switch half width
    rx, r1, r2 = 14.0, -44.0, -36.0             # divider column; R1 and R2 lower ends
    j = r1 + RES_L + 1.0
    cx, cy = 17.5, r2 + RES_L / 2
    leg = CAP_BODY[1] / 2 - 0.21
    cz = zr + 0.4
    lane = dict(zip(["G", "D1", "D2", "D3", "D4", "D5"], [-3.15, -2.25, -1.35, -0.45, 0.45, 1.35]))

    def rise(pt, x):
        return [pt, (pt[0], pt[1], zl), (x, pt[1], zl)]

    red = wire(
        [(bp[0], cell, gap), (bp[0], bp[1], gap), (bp[0], bp[1], under)],
        [(bp[0], bp[1], gap), (11.0, bp[1], gap), (11.0, r1 - 0.6, gap), (rx, r1 - 0.6, gap),
         (rx, r1 - 0.6, zr), (rx, r1, zr)])
    sense = wire(
        [(rx, r1 + RES_L, zr), (rx, r2, zr)],
        [(cx, cy - leg, cz), (cx, cy - leg, zr), (cx, j, zr), (rx, j, zr)],
        [ds[0], (ds[0][0], ds[0][1], 7.55), (11.0, ds[0][1], 7.55), (11.0, j, 7.55), (rx, j, 7.55), (rx, j, zr)])
    k3, k4, k1, k2 = 8.0, 8.0, 25.0, 25.0       # key rows
    black = wire(
        [(bn[0], cell, gap), (bn[0], bn[1], gap), (bn[0], bn[1], under)],
        [(rx, r2 + RES_L, zr), (rx, r2 + RES_L + 1, zr), (rx, r2 + RES_L + 1, zs), (rx, k4, zs),
         (8.0 + face, k4, zs)],
        [(cx, cy + leg, cz), (cx, cy + leg, zr), (cx, r2 + RES_L + 1, zr), (rx, r2 + RES_L + 1, zr)],
        rise(g, lane["G"]) + [(lane["G"], 36.0, zl), (lane["G"], 36.0, zs), (-1.5, 36.0, zs),
                              (-1.5, 44.0 - face, zs)],
        *[[(lane["G"], y - 1.5, zl), (lane["G"], y - 1.5, zs), (-8.0 + face, y - 1.5, zs)] for y in (k3, k1)],
        *[[(lane["G"], y - 1.5, zs), (8.0 - face, y - 1.5, zs)] for y in (k4, k2)])
    signal = wire(
        rise(ds[1], lane["D1"]) + [(lane["D1"], 38.5, zl), (1.0, 38.5, zl), (1.0, 38.5, zs), (1.0, 44.0 - face, zs)],
        rise(ds[2], lane["D2"]) + [(lane["D2"], k1 + 1.5, zl), (lane["D2"], k1 + 1.5, zs), (-8.0 + face, k1 + 1.5, zs)],
        rise(ds[3], lane["D3"]) + [(lane["D3"], k2 + 1.5, zl), (lane["D3"], k2 + 1.5, zs), (8.0 - face, k2 + 1.5, zs)],
        rise(ds[4], lane["D4"]) + [(lane["D4"], k3 + 1.5, zl), (lane["D4"], k3 + 1.5, zs), (-8.0 + face, k3 + 1.5, zs)],
        rise(ds[5], lane["D5"]) + [(lane["D5"], k4 + 1.5, zl), (lane["D5"], k4 + 1.5, zs), (8.0 - face, k4 + 1.5, zs)])
    divider = (resistor_y(rx, r1, r1 + RES_L, zr) + resistor_y(rx, r2, r2 + RES_L, zr)
               + capacitor(cx, cy, cz))
    return {"wire-red": red, "wire-black": black, "wire-sense": sense, "wire-signal": signal,
            "divider": divider}


def Cylinder_(r, h):
    from build123d import Cylinder
    return Cylinder(r, h, align=BASE)


PRINT_TOP = "Shell, panel and caps: one print, top face down"
PRINT_BASE = "Base and its TPU: one print, floor down"
CAP_COLORS = ["#e0803a", "#2f6fb7", "#2f6fb7", "#8b93a5", "#8b93a5"]


def export(p):
    asm = Assembly("ha-remote", "bar", title="Bar",
                   description="Five-button remote, 44 x 120 x 15 mm, shown with its parts inside.")
    ref = dict(source="bought", notes=["reference only"])
    up = 34
    asm.add("xiao", p["xiao"], "XIAO ESP32S3", material="FR4", color="#2c6e49", explode=(0, 0, 12),
            description="The microcontroller and battery charger. Sits on top of the radio board.", **ref)
    asm.add("usb", p["usb"], "USB-C port", material="Steel", color="#b9bec5", explode=(0, 0, 12),
            description="Charging, in the bottom end.", **ref)
    asm.add("wio", p["wio"], "Wio-SX1262 board", material="FR4", color="#1f4e8c", explode=(0, 0, 12),
            description="The LoRa radio, under the XIAO.", **ref)
    asm.add("battery", p["battery"], "LiPo cell, 350 mAh", color="#c9ccd1", mass_g=8.2, explode=(0, 0, 9),
            description="Adafruit 2750: 36 x 19.6 x 5.2 mm, protection circuit built in.", source="bought",
            mpn="2750")
    asm.add("switches", p["switches"], "6 mm tact switches (5)", color="#30343a", mass_g=1.25, mpn="B3F-1020", explode=(0, 0, 16),
            description="6 x 6 x 5 mm, one under each cap.", source="bought")
    asm.add("fpc-wifi", p["fpc-wifi"], "Wi-Fi antenna (FPC)", color="#c79a3b", mass_g=0.3, explode=(10, 0, 6),
            description="On the right wall beside the battery.", source="bought", notes=["EST: size"])
    asm.add("fpc-lora", p["fpc-lora"], "LoRa antenna (FPC)", color="#c79a3b", mass_g=0.4, explode=(-10, 0, 6),
            description="On the left wall beside the battery.", source="bought", notes=["EST: size"])
    asm.add("shell", p["shell"], "Shell", material="PLA", color="#eceae4", explode=(0, 0, up),
            description="Top and wall, with a tongue slot at the top end.", notes=[PRINT_TOP])
    asm.add("panel", p["panel"], "Keypad panel", material="TPU", color="#3a3f47", explode=(0, 0, up),
            description="75A TPU. A U-channel round every cap is that cap's spring.", notes=[PRINT_TOP])
    names = ["Main button", "Key 1", "Key 2", "Key 3", "Key 4"]
    for i, (key, name) in enumerate(zip(["cap-main", "cap-1", "cap-2", "cap-3", "cap-4"], names)):
        asm.add(key, p[key], name, material="PLA", color=CAP_COLORS[i], explode=(0, 0, up),
                description="17 mm round cap." if i == 0 else "11 mm square cap.", notes=[PRINT_TOP])
    asm.add("base", p["base"], "Base", material="PLA", color="#d8d5cc",
            description="Floor with five switch pedestals and cradles; tongue at the top end.", notes=[PRINT_BASE])
    asm.add("grip", p["grip"], "Feet and grips", material="TPU", color="#3a3f47",
            description="Four TPU feet, and two strips that pinch the kit.", notes=[PRINT_BASE])
    asm.add("screws", p["screws"], "M2 x 8 thread-forming screws (4)", material="Steel", color="#7d838c",
            explode=(0, 0, -12), description="Two at the bottom end, two beside the keys.", source="bought")
    wiring_parts(asm, p, "each switch")
    asm.export()


if __name__ == "__main__":
    export(build())
