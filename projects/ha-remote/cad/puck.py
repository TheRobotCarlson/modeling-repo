"""The puck: one big button, 72 mm across and 16 mm tall.

Two prints. The shell, the TPU ring and the cap are one multi-material print, top
face down, so the cap comes off the printer already sitting in its spring. The base
carries everything inside and screws on from below.

Inside, at floor level: the battery across the front, the radio kit at the back
with its USB-C port at the wall, and a 12 mm switch in the middle on a pedestal.
The two FPC antennas curl around the inside of the wall, left and right.
"""

import math

from build123d import Axis, Box, Circle, Cylinder, Pos, Rot

from _parts import (BATT_L, CELL_W, KIT_L, KIT_W, LORA_FPC, USB_OUT, WIFI_FPC, Z_USB, BASE,
                    battery, fpc_arc, keypad, kit, screw_m2, slab, tact)
from modelkit import Assembly

R_OUT, WALL, TOP_T, BASE_T = 36.0, 2.0, 2.0, 2.0
R_IN = R_OUT - WALL
H = 16.0                          # shell height; the cap is flush with the top
CAP_R, PANEL_R = 15.5, 22.0
STEM_Z = 12.0                     # bottom of the cap's stem
SW_GAP = 0.2                      # stem to switch, at rest
BOSS_R, BOSS_AT, BOSS_ANG = 2.75, 29.0, (40, 140, 220, 320)
FIT = 0.2                         # base to shell bore, per side

KIT_Y = R_IN - 0.9 - KIT_L / 2 - USB_OUT     # USB face 0.9 mm inside the wall
BATT_Y = -18.5


def build():
    p = {}
    # --- bought parts --------------------------------------------------------------
    wio, xiao, usb = (Pos(0, KIT_Y, BASE_T) * Rot(0, 0, 90) * s for s in kit())
    p["wio"], p["xiao"], p["usb"] = wio, xiao, usb
    p["battery"] = Pos(0, BATT_Y, BASE_T) * battery()
    sw, sw_h = tact(12)
    sw_z = STEM_Z - SW_GAP - sw_h
    p["switch"] = Pos(0, 0, sw_z) * sw
    p["fpc-wifi"] = fpc_arc(R_IN, *WIFI_FPC, 0, 3.5)
    p["fpc-lora"] = fpc_arc(R_IN, *LORA_FPC, 180, 3.0)

    # --- shell ---------------------------------------------------------------------
    shell = Cylinder(R_OUT, H, align=BASE)
    shell = shell.fillet(3.5, shell.edges().group_by(Axis.Z)[-1])
    shell = shell.fillet(1.0, shell.edges().group_by(Axis.Z)[0])
    shell -= Cylinder(R_IN, H - TOP_T, align=BASE)
    for a in BOSS_ANG:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        boss = Pos(BOSS_AT * c, BOSS_AT * s, BASE_T) * Cylinder(BOSS_R, H - TOP_T - BASE_T + 0.01, align=BASE)
        rib = Pos((BOSS_AT + 3) * c, (BOSS_AT + 3) * s, BASE_T) * Rot(0, 0, a) * Box(6, 1.6, H - TOP_T - BASE_T + 0.01, align=BASE)
        shell += boss + rib
        shell -= Pos(BOSS_AT * c, BOSS_AT * s, BASE_T - 0.01) * Cylinder(0.8, 10, align=BASE)
    # USB-C port: through the wall at the back
    port = Pos(0, R_IN + 1, BASE_T + Z_USB) * Box(9.8, 6, 4.0)
    shell -= port.fillet(1.6, port.edges().filter_by(Axis.Y))
    # light window: the top thins to 0.6 mm over the XIAO's charge LED (EST position)
    shell -= Pos(-6.0, KIT_Y + 7.0, H - TOP_T - 0.01) * Cylinder(1.6, TOP_T - 0.6, align=BASE)

    tpu, caps, cut = keypad(H, Circle(PANEL_R), [(Circle(CAP_R), (0, 0), 3.0, STEM_Z)])
    shell -= cut
    p["shell"], p["ring"], p["cap"] = shell, tpu, caps[0]

    # --- base: floor, pedestal, cradles --------------------------------------------
    base = Cylinder(R_IN - FIT, BASE_T, align=BASE)
    ped = Pos(0, 0, BASE_T) * Box(13, 13, sw_z + 0.6 - BASE_T, align=BASE)
    ped -= Pos(0, 0, sw_z) * Box(12.2, 12.2, 1, align=BASE)
    ped -= Pos(0, -6, sw_z - 1.0) * Box(14, 2.0, 2, align=BASE)       # leg and wire channel
    for y in (-4.5, 4.5):                                              # the switch's positioning bosses
        ped -= Pos(0, y, sw_z - 1.6) * Cylinder(1.1, 2, align=BASE)
    base += ped
    for sx in (-1, 1):
        base += Pos(sx * (BATT_L / 2 + 1.0), BATT_Y + 4.5, BASE_T) * Box(1.2, 6, 3, align=BASE)   # battery end stops
        base += Pos(sx * (KIT_W / 2 + 1.0), KIT_Y - 1.5, BASE_T) * Box(1.2, 14, 3, align=BASE)  # kit cradle
    base += Pos(0, BATT_Y + CELL_W / 2 + 1.2, BASE_T) * Box(24, 1.0, 3, align=BASE)     # battery inner wall
    base += Pos(0, KIT_Y - KIT_L / 2 - 0.9, BASE_T) * Box(12, 1.0, 4, align=BASE)       # kit back stop
    grip = None
    for sx in (-1, 1):
        g = Pos(sx * (KIT_W / 2 + 0.18), KIT_Y - 1.5, BASE_T + 0.5) * Box(0.4, 10, 2.5, align=BASE)
        grip = g if grip is None else grip + g
    feet = Pos(0, 0, -0.6) * (Cylinder(26, 1.2, align=BASE) - Cylinder(22, 1.2, align=BASE))
    base -= feet
    grip += feet
    screws = []
    for a in BOSS_ANG:
        x, y = BOSS_AT * math.cos(math.radians(a)), BOSS_AT * math.sin(math.radians(a))
        base -= Pos(x, y, -0.01) * Cylinder(1.2, BASE_T + 0.1, align=BASE)
        base -= Pos(x, y, -0.01) * Cylinder(2.1, 1.7, align=BASE)
        screws.append(screw_m2(x, y, 0.1))
    p["base"], p["grip"] = base, grip
    p["screws"] = screws[0] + screws[1] + screws[2] + screws[3]
    return p


PRINT_TOP = "Shell, ring and cap: one print, top face down"
PRINT_BASE = "Base and its TPU: one print, floor down"


def export(p):
    asm = Assembly("ha-remote", "puck", title="Puck",
                   description="Single-button remote, 72 x 16 mm, shown with its parts inside.")
    ref = dict(source="bought", notes=["reference only"])
    asm.add("xiao", p["xiao"], "XIAO ESP32S3", material="FR4", color="#2c6e49", explode=(0, 0, 14),
            description="The microcontroller and battery charger. Sits on top of the radio board.", **ref)
    asm.add("usb", p["usb"], "USB-C port", material="Steel", color="#b9bec5", explode=(0, 0, 14),
            description="Charging. Lines up with the hole in the back wall.", **ref)
    asm.add("wio", p["wio"], "Wio-SX1262 board", material="FR4", color="#1f4e8c", explode=(0, 0, 14),
            description="The LoRa radio, under the XIAO. Put to sleep before every deep sleep.", **ref)
    asm.add("battery", p["battery"], "LiPo cell, 350 mAh", color="#c9ccd1", mass_g=8.2, explode=(0, 0, 10),
            description="Adafruit 2750: 36 x 19.6 x 5.2 mm, protection circuit built in.", source="bought",
            mpn="2750")
    asm.add("switch", p["switch"], "12 mm tact switch", color="#30343a", mass_g=0.85, mpn="B3F-4055", explode=(0, 0, 18),
            description="The click. The cap's stem rests 0.2 mm above it.", source="bought")
    asm.add("fpc-wifi", p["fpc-wifi"], "Wi-Fi antenna (FPC)", color="#c79a3b", mass_g=0.3, explode=(10, 0, 8),
            description="Stuck to the inside of the wall, right side.", source="bought", notes=["EST: size"])
    asm.add("fpc-lora", p["fpc-lora"], "LoRa antenna (FPC)", color="#c79a3b", mass_g=0.4, explode=(-10, 0, 8),
            description="Stuck to the inside of the wall, left side.", source="bought", notes=["EST: size"])
    asm.add("shell", p["shell"], "Shell", material="PLA", color="#eceae4", explode=(0, 0, 40),
            description="Top and wall. Printed top face down with the ring and cap.", notes=[PRINT_TOP])
    asm.add("ring", p["ring"], "Spring ring", material="TPU", color="#3a3f47", explode=(0, 0, 40),
            description="75A TPU. Its U-shaped channel is the button's spring and its seal.", notes=[PRINT_TOP])
    asm.add("cap", p["cap"], "Cap", material="PLA", color="#e0803a", explode=(0, 0, 40),
            description="31 mm cap with a shallow dish. Bonded to the ring, so it cannot fall out.",
            notes=[PRINT_TOP])
    asm.add("base", p["base"], "Base", material="PLA", color="#d8d5cc", explode=(0, 0, 0),
            description="Floor with the switch pedestal and cradles for the battery and kit.", notes=[PRINT_BASE])
    asm.add("grip", p["grip"], "Feet and grips", material="TPU", color="#3a3f47", explode=(0, 0, 0),
            description="TPU foot ring underneath, and two strips that pinch the kit.", notes=[PRINT_BASE])
    asm.add("screws", p["screws"], "M2 x 8 thread-forming screws (4)", material="Steel", color="#7d838c",
            explode=(0, 0, -12), description="Into the shell's bosses.", source="bought")
    asm.export()


if __name__ == "__main__":
    export(build())
