"""The LoRa gateway: a third kit on USB power, on a desk or shelf in the office.

A low box, 74 x 42 x 18 mm. The kit lies on the floor at the right with USB-C out
of the back. The LoRa antenna runs along the inside of the front wall and the Wi-Fi
antenna along the right end, so neither sits over the board. The left end is a
walled-off, vented chamber for an optional SHT40 temperature and humidity sensor,
kept away from the board's heat. The user LED shows through a light pipe and
blinks for every packet heard.

The shell prints top face down in one piece with the light pipe. The base carries
the partition wall, hooks under the left end with a tongue and takes two screws at
each side of the main compartment.
"""

from build123d import Align, Axis, Box, Pos, RectangleRounded, Rot, extrude

from _parts import (BASE, FPC_T, GAP_Z, KIT_L, KIT_W, LED_USER, LORA_FPC, USB_OUT, WIFI_FPC,
                    Z_USB, Z_XIAO_TOP, fpc_flat, kit, light_pipe, pad, screw_m2, sht40_board, wire)
from modelkit import Assembly

W, D, H, CORNER = 74.0, 42.0, 18.0, 3.0
WALL, TOP_T, BASE_T = 2.0, 2.0, 2.0
IN_W, IN_D = W - 2 * WALL, D - 2 * WALL
FIT = 0.2

KIT_X = 18.0
KIT_Y = IN_D / 2 - 0.7 - USB_OUT - KIT_L / 2      # USB face 0.7 mm inside the back wall
PART_X = (-14.0, -12.4)                          # partition between the sensor chamber and the rest
SENSOR_AT = (-25.0, 0.0)
SENSOR_Z = BASE_T + 3.0                          # on two rails, open underneath
BOSSES = [(-9.8, -15.5), (-9.8, 15.5), (31.0, -15.5), (31.0, 15.5)]
BOSS_R = 2.5
TONGUE_W = 14.0
NOTCH = (-6.0, 6.0, 10.3)                        # wire notch in the partition: y range, bottom z
PRINT_TOP = "Shell and light pipe: one print, top face down"
PRINT_BASE = "Base and its TPU: one print, floor down"


def Cyl(r, h):
    from build123d import Cylinder
    return Cylinder(r, h, align=BASE)


def build():
    p = {}
    # --- bought parts --------------------------------------------------------------
    kloc = Pos(KIT_X, KIT_Y, BASE_T) * Rot(0, 0, 90)       # USB-C toward +Y, the back
    p["wio"], p["xiao"], p["usb"] = (kloc * s for s in kit())
    p["sensor"], spads = sht40_board(*SENSOR_AT, SENSOR_Z)
    p["fpc-lora"] = Pos(11.5, -IN_D / 2 + FPC_T / 2, 4.0 + LORA_FPC[1] / 2) * Box(LORA_FPC[0], FPC_T, LORA_FPC[1])
    p["fpc-wifi"] = fpc_flat(IN_W / 2, -WIFI_FPC[0] / 2, *WIFI_FPC, 4.5, +1)
    led = kloc * Pos(*LED_USER, 0)

    # --- shell ---------------------------------------------------------------------
    shell = extrude(RectangleRounded(W, D, CORNER), H)
    shell = shell.fillet(2.0, shell.edges().group_by(Axis.Z)[-1])
    shell = shell.fillet(0.8, shell.edges().group_by(Axis.Z)[0])
    shell -= extrude(RectangleRounded(IN_W, IN_D, CORNER - WALL + 0.01), H - TOP_T)
    for x, y in BOSSES:
        shell += Pos(x, y, BASE_T) * Cyl(BOSS_R, H - TOP_T - BASE_T + 0.01)
        shell -= Pos(x, y, BASE_T - 0.01) * Cyl(0.8, 9.0)
    port = Pos(KIT_X, IN_D / 2 + 1, BASE_T + Z_USB) * Box(9.8, 6, 4.0)
    shell -= port.fillet(1.6, port.edges().filter_by(Axis.Y))
    shell -= Pos(-IN_W / 2 + 0.2, 0, 0.6) * Box(1.8, TONGUE_W + 0.6, 1.6, align=(Align.MAX, Align.CENTER, Align.MIN))
    # Sensor chamber vents: slots in the end, front and back walls low down, and in
    # the top, so air comes in at the side and rises past the sensor.
    for i in range(6):
        x = -32.0 + 3.0 * i
        for sy in (-1, 1):
            shell -= Pos(x, sy * (D / 2 - WALL / 2), 4.0) * Box(1.5, WALL + 1, 8.0, align=BASE)
        shell -= Pos(x, 0, H - TOP_T - 0.5) * Box(1.5, 20.0, TOP_T + 1, align=BASE)
    for i in range(7):
        shell -= Pos(-W / 2 + WALL / 2, -9.0 + 3.0 * i, 4.0) * Box(WALL + 1, 1.5, 8.0, align=BASE)
    # A few slots in the back wall let the board's warm air out of the main compartment.
    for x in (-6.0, -3.0, 0.0, 3.0):
        shell -= Pos(x, D / 2 - WALL / 2, 9.0) * Box(1.5, WALL + 1, 6.0, align=BASE)
    p["pipe"] = light_pipe(led.position.X, led.position.Y, BASE_T + Z_XIAO_TOP + 0.6, H)
    shell -= p["pipe"]
    p["shell"] = shell

    # --- base ----------------------------------------------------------------------
    base = extrude(RectangleRounded(IN_W - 2 * FIT, IN_D - 2 * FIT, CORNER - WALL), BASE_T)
    base += Pos(-IN_W / 2 + FIT, 0, 0.8) * Box(1.4 + FIT, TONGUE_W, 1.2, align=(Align.MAX, Align.CENTER, Align.MIN))
    wall = Pos(sum(PART_X) / 2, 0, BASE_T) * Box(PART_X[1] - PART_X[0], IN_D - 2 * FIT, H - TOP_T - FIT - BASE_T,
                                                 align=BASE)
    y0, y1, zn = NOTCH
    wall -= Pos(sum(PART_X) / 2, (y0 + y1) / 2, zn) * Box(3, y1 - y0, H, align=BASE)
    base += wall
    sx, sy = SENSOR_AT
    for s in (-1, 1):                    # rails under the sensor board's ends
        base += Pos(sx, sy + s * 11.2, BASE_T) * Box(14, 3, SENSOR_Z - BASE_T, align=BASE)
    kit_front = KIT_Y - KIT_L / 2
    for s in (-1, 1):                    # kit cradle: side rails and a front stop
        base += Pos(KIT_X + s * (KIT_W / 2 + 1.0), KIT_Y - 1.5, BASE_T) * Box(1.2, 13, 3, align=BASE)
    base += Pos(KIT_X, kit_front - 0.6, BASE_T) * Box(10, 1.0, 3, align=(Align.CENTER, Align.MAX, Align.MIN))
    grip = None
    for s in (-1, 1):
        g = Pos(KIT_X + s * (KIT_W / 2 + 0.18), KIT_Y - 1.5, BASE_T + 0.5) * Box(0.4, 9, 2.5, align=BASE)
        grip = g if grip is None else grip + g
    for x, y in [(-28, -12), (-28, 12), (24, -12), (24, 12)]:
        foot = Pos(x, y, -0.6) * Cyl(4.0, 1.2)
        base -= foot
        grip += foot
    screws = None
    for x, y in BOSSES:
        base -= Pos(x, y, -0.01) * Cyl(1.2, BASE_T + 0.1)
        base -= Pos(x, y, -0.01) * Cyl(2.1, 1.7)
        s = screw_m2(x, y, 0.1)
        screws = s if screws is None else screws + s
    p["base"], p["grip"], p["screws"] = base, grip, screws
    p.update(wiring(kloc, spads))
    return p


def wiring(kloc, spads):
    """Four wires from the sensor's header, through the notch in the partition, to
    the XIAO. SDA and SCL go to D4 and D5 on the near edge; VIN and GND cross over
    the kit to 3V3 and GND on the far edge, higher up so they clear the bus wires.
    """
    d4, d5, v3, g = (pad(kloc, n) for n in ("D4", "D5", "3V3", "GND"))
    sda, scl, gnd, vin = (spads[n] for n in ("SDA", "SCL", "GND", "VIN"))
    hx = sda[0]
    z_sda, z_scl, z_gnd, z_vin = 11.8, 11.0, 12.6, 11.0
    bus = wire(
        [sda, (hx, sda[1], z_sda), (d4[0], sda[1], z_sda), (d4[0], d4[1], z_sda), d4],
        [scl, (hx, scl[1], z_scl), (d5[0] - 2.0, scl[1], z_scl), (d5[0] - 2.0, d5[1], z_scl),
         (d5[0], d5[1], z_scl), d5])
    black = wire([gnd, (hx, gnd[1], z_gnd), (g[0], gnd[1], z_gnd), (g[0], g[1], z_gnd), g])
    supply = wire([vin, (hx, vin[1], z_vin), (v3[0] + 1.5, vin[1], z_vin), (v3[0] + 1.5, v3[1], z_vin),
                   (v3[0], v3[1], z_vin), v3])
    return {"wire-bus": bus, "wire-black": black, "wire-supply": supply}


def export(p):
    asm = Assembly("ha-remote", "gateway", title="Gateway",
                   description="LoRa gateway on USB power, 74 x 42 x 18 mm, shown with its parts inside.")
    ref = dict(source="bought", notes=["reference only"])
    up = 30
    asm.add("xiao", p["xiao"], "XIAO ESP32S3", material="FR4", color="#2c6e49", explode=(0, 0, 10),
            description="Runs ESPHome, on Wi-Fi to Home Assistant all the time.", **ref)
    asm.add("usb", p["usb"], "USB-C port", material="Steel", color="#b9bec5", explode=(0, 0, 10),
            description="Power, from any 5 V USB adapter. Out of the back.", **ref)
    asm.add("wio", p["wio"], "Wio-SX1262 board", material="FR4", color="#1f4e8c", explode=(0, 0, 10),
            description="The LoRa radio, always listening.", **ref)
    asm.add("sensor", p["sensor"], "SHT40 sensor (optional)", color="#1d2a6b", mass_g=1.0, mpn="4885",
            source="bought", explode=(0, 0, 10), notes=["EST: outline and pin order"],
            description="Adafruit 4885. Temperature and humidity for the office, in its own vented chamber.")
    asm.add("fpc-lora", p["fpc-lora"], "LoRa antenna (FPC)", color="#c79a3b", mass_g=0.4, explode=(0, -10, 6),
            description="Along the inside of the front wall.", source="bought", notes=["EST: size"])
    asm.add("fpc-wifi", p["fpc-wifi"], "Wi-Fi antenna (FPC)", color="#c79a3b", mass_g=0.3, explode=(10, 0, 6),
            description="On the right end wall.", source="bought", notes=["EST: size"])
    asm.add("shell", p["shell"], "Shell", material="PLA", color="#eceae4", explode=(0, 0, up),
            description="Top and walls, with vents round the sensor chamber and a tongue slot at the left end.",
            notes=[PRINT_TOP])
    asm.add("pipe", p["pipe"], "Light pipe", material="PLA", color="#dfe9ee", explode=(0, 0, up),
            description="Clear PLA, part of the top print. Blinks for every packet heard.",
            notes=[PRINT_TOP, "EST: LED position"])
    asm.add("base", p["base"], "Base", material="PLA", color="#d8d5cc",
            description="Floor with the kit cradle, the sensor rails and the partition wall.", notes=[PRINT_BASE])
    asm.add("grip", p["grip"], "Feet and grips", material="TPU", color="#3a3f47",
            description="Four TPU feet, and two strips that pinch the kit.", notes=[PRINT_BASE])
    asm.add("screws", p["screws"], "M2 x 8 thread-forming screws (4)", material="Steel", color="#7d838c",
            explode=(0, 0, -12), description="Two each side of the partition and two at the right end.",
            source="bought")
    w = dict(source="bought", layer="Wiring", notes=["Route is a plan, not measured"])
    asm.add("wire-supply", p["wire-supply"], "Sensor supply (3V3)", color="#e07b2a", mass_g=0.05,
            description="3V3 to the sensor's VIN.", **w)
    asm.add("wire-black", p["wire-black"], "Ground wire", color="#2a2c30", mass_g=0.05,
            description="GND to the sensor's GND.", **w)
    asm.add("wire-bus", p["wire-bus"], "Sensor wires", color="#3f7fd0", mass_g=0.1,
            description="SDA (D4) and SCL (D5) to the sensor's header.", **w)
    asm.export()


if __name__ == "__main__":
    export(build())
