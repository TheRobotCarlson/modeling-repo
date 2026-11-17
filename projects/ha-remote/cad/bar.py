"""The bar: five buttons, 44 x 120 mm and 15 mm thick.

Same construction as the puck. The shell, a TPU keypad panel and five caps print
as one piece, top face down. The base screws on from below and hooks under the
top end with a tongue, so the end under the buttons cannot spring away.

Layout, top to bottom: one round main button, a 2 x 2 block of square keys, then
the battery, then the radio kit with USB-C in the bottom end. The antennas lie
along the side walls beside the battery.
"""

from build123d import Axis, Box, Circle, Pos, RectangleRounded, Rot, extrude, offset

from _parts import (BASE, BATT_L, CELL_W, KIT_L, KIT_W, LORA_FPC, USB_OUT, WIFI_FPC, Z_USB,
                    battery, fpc_flat, keypad, kit, screw_m2, slab, tact)
from modelkit import Assembly

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
BATT_Y = -17.3
TONGUE_W = 14.0


def plan(w, l, r):
    return RectangleRounded(w, l, r)


def build():
    p = {}
    # --- bought parts --------------------------------------------------------------
    wio, xiao, usb = (Pos(0, KIT_Y, BASE_T) * Rot(0, 0, -90) * s for s in kit())
    p["wio"], p["xiao"], p["usb"] = wio, xiao, usb
    p["battery"] = Pos(0, BATT_Y, BASE_T) * Rot(0, 0, 90) * battery()
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
    base += Pos(0, stop_y, BASE_T) * Box(12, 0.8, 4, align=BASE)       # between battery and kit
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
        base -= Pos(x, y, -0.01) * Cylinder_(2.1, 1.5)
        s = screw_m2(x, y, 0.1, 8.0 if y < 0 else 7.0)
        screws = s if screws is None else screws + s
    p["base"], p["grip"], p["screws"] = base, grip, screws
    return p


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
    asm.add("battery", p["battery"], "LiPo cell, 502030 class", color="#c9ccd1", mass_g=5.5, explode=(0, 0, 9),
            description="About 250 mAh. Generic size until a cell is chosen.", source="bought",
            notes=["EST: size and mass"])
    asm.add("switches", p["switches"], "6 mm tact switches (5)", color="#30343a", mass_g=2.5, explode=(0, 0, 16),
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
    asm.add("screws", p["screws"], "M2 self-tapping screws (4)", material="Steel", color="#7d838c",
            explode=(0, 0, -12), description="Two 8 mm at the bottom end, two 7 mm by the keys.", source="bought")
    asm.export()


if __name__ == "__main__":
    export(build())
