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

from _parts import (BATT_L, CAP_BODY, CELL_W, GAP_Z, KIT_L, KIT_W, LORA_FPC, RES_D, RES_L, USB_OUT,
                    WIFI_FPC, Z_USB, BASE, battery, capacitor, fpc_arc, keypad, kit, pad, resistor_y,
                    screw_m2, slab, tact, wire)
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
    kloc = Pos(0, KIT_Y, BASE_T) * Rot(0, 0, 90)
    wio, xiao, usb = (kloc * s for s in kit())
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
    for sx in (-1, 1):                                  # kit back stops, apart so the battery wires pass
        base += Pos(sx * 6.5, KIT_Y - KIT_L / 2 - 0.9, BASE_T) * Box(3, 1.0, 4, align=BASE)
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
    p.update(wiring(kloc, sw_z))
    return p


def wiring(kloc, sw_z):
    """Wires, as they could be run. Paths are a plan, not a measurement.

    Battery leads leave the cell's right end, climb over it and run up the right
    side, then cross in front of the switch and slide into the gap between the two
    boards to the battery pads. The divider lies on the floor left of the switch.
    The two switch wires run over the kit, above the battery leads.
    """
    under = GAP_Z + BASE_T + 0.4               # XIAO underside: the battery pads
    gap = GAP_Z + BASE_T                       # wire centre between the boards
    zb, zl, zs = 8.0, 10.9, sw_z + 2.5         # over the battery, over the USB-C port, at the switch
    zr = BASE_T + RES_D / 2 + 0.05             # resistor axis, just off the floor
    bp, bn, d0, d1, g = (pad(kloc, n) for n in ("BAT+", "BAT-", "D0", "D1", "GND"))
    end, ly = BATT_L / 2, BATT_Y                # cell's lead end
    sx = 6.0                                    # switch half width
    rx, r1, r2 = -13.5, 16.5, 8.5               # divider column; R1 and R2 lower ends
    j = r1 - 1.0                                # divider middle
    cx, cy = -17.0, 11.5                        # capacitor beside R2
    leg = CAP_BODY[1] / 2 - 0.21                # legs 5.08 apart
    cz = zr + 0.4

    red = wire(
        [(end, ly - 3.5, 4.6), (end + 0.6, ly - 3.5, 4.6), (end + 0.6, ly - 3.5, zb), (12, ly - 3.5, zb),
         (12, 8, zb), (bp[0], 8, zb), (bp[0], 8, gap), (bp[0], bp[1], gap), (bp[0], bp[1], under)],
        [(bp[0], bp[1], gap), (rx, bp[1], gap), (rx, r1 + RES_L + 1, gap), (rx, r1 + RES_L + 1, zr),
         (rx, r1 + RES_L, zr)])
    black = wire(
        [(end, ly - 1.5, 4.6), (end + 0.6, ly - 1.5, 4.6), (end + 0.6, ly - 1.5, zb), (13, ly - 1.5, zb),
         (13, 9, zb), (bn[0], 9, zb), (bn[0], 9, gap), (bn[0], bn[1], gap), (bn[0], bn[1], under)],
        [g, (g[0], g[1], zl), (2.5, g[1], zl), (2.5, sx + 0.6, zl), (2.5, sx + 0.6, zs), (2.5, sx, zs)],
        [(rx, r2, zr), (rx, r2 - 1, zr), (rx, 2.5, zr), (rx, 2.5, zs), (-sx, 2.5, zs)],
        [(cx, cy - leg, cz), (cx, cy - leg, zr), (cx, r2 - 1, zr), (rx, r2 - 1, zr)])
    sense = wire(
        [(rx, r1, zr), (rx, r2 + RES_L, zr)],
        [(cx, cy + leg, cz), (cx, cy + leg, zr), (cx, j, zr), (rx, j, zr)],
        [(rx, j, zr), (-11.6, j, zr), (-11.6, j, 7.55), (-11.6, d0[1], 7.55), (d0[0], d0[1], 7.55), d0])
    signal = wire([d1, (d1[0], d1[1], zl), (-2.5, d1[1], zl), (-2.5, sx + 0.6, zl), (-2.5, sx + 0.6, zs),
                   (-2.5, sx, zs)])
    divider = (resistor_y(rx, r1, r1 + RES_L, zr) + resistor_y(rx, r2, r2 + RES_L, zr)
               + capacitor(cx, cy, cz))
    return {"wire-red": red, "wire-black": black, "wire-sense": sense, "wire-signal": signal,
            "divider": divider}


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
    wiring_parts(asm, p, "the switch")
    asm.export()


WIRING = "Wiring"


def wiring_parts(asm, p, button):
    w = dict(source="bought", layer=WIRING, notes=["Route is a plan, not measured", "EST: battery pad position"])
    asm.add("wire-red", p["wire-red"], "Battery + wires", color="#c8382f", mass_g=0.2,
            description="Cell + to the XIAO's BAT+ pad, and BAT+ to the top of the divider.", **w)
    asm.add("wire-black", p["wire-black"], "Ground wires", color="#2a2c30", mass_g=0.3,
            description=f"Cell - to BAT-, GND to {button}, and the divider's bottom to the nearest switch ground.", **w)
    asm.add("wire-sense", p["wire-sense"], "Battery sense (D0)", color="#e8e6df", mass_g=0.1,
            description="The divider's middle to D0, with the capacitor's other leg.", **w)
    asm.add("wire-signal", p["wire-signal"], "Button wires", color="#e3b232", mass_g=0.2,
            description=f"D1 - D5 to {button}." if button != "the switch" else "D1 to the switch.", **w)
    asm.add("divider", p["divider"], "Battery divider: 2 x 1 MOhm + 100 nF", color="#c9a66b", mass_g=0.6,
            description="Two resistors in series from BAT+ to ground, the capacitor across the lower one.",
            **{**w, "notes": ["EST: body sizes"]})


if __name__ == "__main__":
    export(build())
