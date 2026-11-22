"""Desk organizer: three ways to hold the same things, from most modular to most compact.

  modular   4 x 4 Gridfinity plate, four modules, three free cells      168 x 168 mm
  combined  4 x 3 Gridfinity plate, three modules, one free cell        168 x 126 mm
  block     one printed block, no grid                                  163 x 100 mm

The pockets are the same in all three; only how they are grouped changes. Each
pocket is the item plus FIT per side, shallow enough that most of the item stands
proud. The USB stick and YubiKey drop into rounded basins instead. The pen, the
brush and the metal stick live in the empty corners round the glasses case.

Item sizes: the user's, in inches, unless marked SOURCE or EST. The desk space is
at most 9 x 7 in.
"""

import math

from build123d import Axis, Box, Cylinder, Pos, RectangleRounded, RegularPolygon, extrude, fillet

import _grid as G
from _grid import BASE, FIT, UNIT, bin_block, cell_centre, inner
from modelkit import Assembly

IN = 25.4
DESK = (9 * IN, 7 * IN)         # the space on the desk, from the user: 229 x 178 mm

# --- the things, millimetres ---------------------------------------------------------
AIRPODS = (50.1, 21.2, 46.2)    # SOURCE: apple.com/airpods-4/specs (case W x D x H)
AIRPODS_R = 9.5                 # EST: plan-view corner radius of the case
GRIP = (4 * IN, 1 * IN, 110.0)  # standing up: 4 x 1 in footprint from the user; height EST
PEN_D, PEN_L = 10.0, 110.0      # EST: one small pen
BRUSH = (0.8 * IN, 0.3 * IN, 150.0)        # handle base from the user; length EST
GLASSES_SIDE, GLASSES_L = 2.8 * IN, 155.0  # triangular case: side from the user; length EST
USB = (0.7 * IN, 1.5 * IN, 8.0)            # thickness EST
YUBIKEY = (0.5 * IN, 1.6 * IN, 3.3)        # thickness EST (YubiKey 5 NFC class)
STICK_D, STICK_L = 0.2 * IN, 3 * IN        # taken as a round rod, stood upright

# --- pockets, each centred on (x, y) of whatever it is cut into ------------------------
# t is the top of the part the pocket is cut into, mm above its bottom.

# Round the glasses case (flat side to the front, point to the back), relative to the
# centre of the triangle's bounding box: pen and brush either side of the point, the
# stick in the gap beside the right-hand face.
PEN_AT = (26.0, 26.0)
BRUSH_AT = (-25.5, 26.5)        # long side across, so nothing reaches past the point
STICK_AT = (33.0, -8.0)
GLASSES_DEPTH = 18.0            # the case sits this deep
HOLE_DEPTH = 30.0               # pen, brush and stick go deeper, so they do not wobble


def glasses_group(x, y, t):
    side = GLASSES_SIDE + 2 * FIT * math.sqrt(3)
    cut, dy = G.triangle_pocket(side, t - GLASSES_DEPTH, t)
    hf = t - HOLE_DEPTH
    cut += Pos(*PEN_AT, 0) * G.round_pocket(PEN_D + 2 * FIT, hf, t)
    cut += Pos(*STICK_AT, 0) * G.round_pocket(STICK_D + 2 * FIT, hf, t)
    cut += Pos(*BRUSH_AT, hf) * extrude(RectangleRounded(BRUSH[0] + 2 * FIT, BRUSH[1] + 2 * FIT, 1.5),
                                        HOLE_DEPTH + 5)
    tri = RegularPolygon(GLASSES_SIDE / math.sqrt(3), 3, rotation=90)
    items = {
        "glasses_case": Pos(0, dy, t - GLASSES_DEPTH) * extrude(tri, GLASSES_L),
        "pen": Pos(*PEN_AT, hf) * Cylinder(PEN_D / 2, PEN_L, align=BASE),
        "brush": Pos(*BRUSH_AT, hf) * Box(*BRUSH, align=BASE),
        "metal_stick": Pos(*STICK_AT, hf) * Cylinder(STICK_D / 2, STICK_L, align=BASE),
    }
    m = Pos(x, y, 0)
    return m * cut, {k: m * v for k, v in items.items()}


_SIDE = GLASSES_SIDE + 2 * FIT * math.sqrt(3)
GLASSES_BOX = (_SIDE + 3.0, _SIDE * math.sqrt(3) / 2 + 3.0)     # the pocket with its corner reliefs


def airpods_pocket(x, y, depth, t):
    w, d = AIRPODS[0] + 2 * FIT, AIRPODS[1] + 2 * FIT
    cut = Pos(x, y, t - depth) * extrude(RectangleRounded(w, d, AIRPODS_R + FIT), depth + 5)
    case = Pos(x, y, t - depth) * extrude(RectangleRounded(AIRPODS[0], AIRPODS[1], AIRPODS_R), AIRPODS[2])
    case = fillet(case.faces().sort_by(Axis.Z)[-1].edges(), 4.0)
    return cut, {"airpods_case": case}


def grip_pocket(x, y, depth, t):
    cut = Pos(x, y, t - depth) * extrude(RectangleRounded(GRIP[0] + 2 * FIT, GRIP[1] + 2 * FIT, 2.0), depth + 5)
    return cut, {"grip_trainer": Pos(x, y, t - depth) * Box(*GRIP, align=BASE)}


BASIN_W, BASIN_GAP, BASIN_R_SIDE = 38.0, 3.5, 12.0


def basins(x, y, length, depth, t, r_bottom=9.0):
    """Two rounded basins side by side, running front to back: the USB stick and the YubiKey."""
    cut, items = None, {}
    for sx, key, size in ((-1, "usb_stick", USB), (1, "yubikey", YUBIKEY)):
        bx = x + sx * (BASIN_W + BASIN_GAP) / 2
        c = Pos(bx, y, 0) * G.scoop(length, BASIN_W, t - depth, t, BASIN_R_SIDE, r_bottom)
        cut = c if cut is None else cut + c
        items[key] = Pos(bx, y, t - depth) * Box(*size, align=BASE)
    return cut, items


# --- Gridfinity modules: each returns (cut, items) round the origin ------------------------
def _glasses_module(t):
    return glasses_group(0, 0, t)


def _grip_module(t):
    return grip_pocket(0, 0, 30.0, t)


def _airpods_module(t):
    return airpods_pocket(0, 0, 20.0, t)


def _smalls_module(t):
    return basins(0, 0, inner(2) - 2.0, 13.0, t)


def _hub_module(t):
    """AirPods along the back, both basins in front: 2 x 2."""
    edge = inner(2) / 2
    ay = edge - 1.0 - (AIRPODS[1] + 2 * FIT) / 2
    cut, items = airpods_pocket(0, ay, 20.0, t)
    front, back = -edge + 1.0, ay - (AIRPODS[1] + 2 * FIT) / 2 - 2.4
    c2, i2 = basins(0, (front + back) / 2, back - front, 15.0, t, r_bottom=7.0)
    return cut + c2, {**items, **i2}


# module: (cells across, cells deep, height units), its lower-left cell, what is cut into it
VARIANTS = {
    "modular": dict(
        title="Modular, 4 x 4", grid=(4, 4),
        modules={
            "grip":    ((3, 1, 6), (0, 3), _grip_module),
            "glasses": ((2, 2, 5), (0, 1), _glasses_module),
            "smalls":  ((2, 2, 3), (2, 1), _smalls_module),
            "airpods": ((2, 1, 4), (0, 0), _airpods_module),
        },
        free=[(3, 3), (2, 0), (3, 0)]),
    "combined": dict(
        title="Combined, 4 x 3", grid=(4, 3),
        modules={
            "grip":    ((3, 1, 6), (0, 2), _grip_module),
            "glasses": ((2, 2, 5), (0, 0), _glasses_module),
            "hub":     ((2, 2, 4), (2, 0), _hub_module),
        },
        free=[(3, 2)]),
    "block": dict(title="One block", grid=None, modules={}, free=[]),
}

# --- one block: two bands. Back: grip and AirPods. Front: glasses group, then the basins.
BLOCK_WALL, BLOCK_RIB, BLOCK_H, BLOCK_R = 2.0, 2.4, 35.0, 6.0
BACK_D = GRIP[1] + 2 * FIT
FRONT_D = GLASSES_BOX[1]
BLOCK_W = math.ceil(max(2 * BLOCK_WALL + GRIP[0] + 2 * FIT + BLOCK_RIB + AIRPODS[0] + 2 * FIT,
                        2 * BLOCK_WALL + GLASSES_BOX[0] + BLOCK_RIB + 2 * BASIN_W + BASIN_GAP))
BLOCK_D = math.ceil(2 * BLOCK_WALL + FRONT_D + BLOCK_RIB + BACK_D)


def block():
    t, w, d = BLOCK_H, BLOCK_W, BLOCK_D
    b = extrude(RectangleRounded(w, d, BLOCK_R), t)
    x0, y0 = -w / 2 + BLOCK_WALL, -d / 2 + BLOCK_WALL
    yb = d / 2 - BLOCK_WALL - BACK_D / 2
    gw, aw = GRIP[0] + 2 * FIT, AIRPODS[0] + 2 * FIT
    bx0, bx1 = x0 + GLASSES_BOX[0] + BLOCK_RIB, w / 2 - BLOCK_WALL
    parts = [
        grip_pocket(x0 + gw / 2, yb, 30.0, t),
        airpods_pocket(w / 2 - BLOCK_WALL - aw / 2, yb, 20.0, t),
        glasses_group(x0 + GLASSES_BOX[0] / 2, y0 + FRONT_D / 2, t),
        basins((bx0 + bx1) / 2, y0 + FRONT_D / 2, FRONT_D, 15.0, t),
    ]
    items = {}
    for cut, its in parts:
        b -= cut
        items.update(its)
    return b, items


def place(size, cell, grid):
    (nx, ny, _), (i, j) = size, cell
    x0, y0 = cell_centre(i, j, *grid)
    return Pos(x0 + (nx - 1) * G.PITCH / 2, y0 + (ny - 1) * G.PITCH / 2, 0)


def build(variant="combined"):
    """Every part and item in place: ({part: shape}, {item: shape})."""
    v = VARIANTS[variant]
    if v["grid"] is None:
        b, items = block()
        return {"block": b}, items
    p, items = {"baseplate": G.baseplate(*v["grid"])}, {}
    for name, (size, cell, fn) in v["modules"].items():
        cut, its = fn(size[2] * UNIT)
        m = place(size, cell, v["grid"])
        p[name] = m * (bin_block(*size) - cut)
        items.update({k: m * s for k, s in its.items()})
    return p, items


# --- export ------------------------------------------------------------------------------
LABELS = {
    "glasses": ("Glasses stand, 2 x 2 x 5", "#6c8f5a",
                "Glasses case on its end, 18 mm deep; pen, brush and metal stick 30 mm deep round it."),
    "grip": ("Grip stand, 3 x 1 x 6", "#b0674a", "103 x 27 mm slot, 30 mm deep: the trainer stands upright."),
    "airpods": ("AirPods dock, 2 x 1 x 4", "#3f9a96", "Case stands upright, 20 mm in the pocket."),
    "smalls": ("Smalls tray, 2 x 2 x 3", "#d0a03c", "Two rounded basins, 13 mm deep."),
    "hub": ("AirPods and smalls hub, 2 x 2 x 4", "#3f9a96", "AirPods along the back, two rounded basins in front."),
    "block": ("Organizer block", "#6c8f5a", "Everything in one 35 mm tall print, no grid."),
}
ITEM_NAMES = {
    "airpods_case": "AirPods 4 case", "grip_trainer": "Grip trainer (height EST)", "pen": "Pen (size EST)",
    "brush": "Keyboard brush", "glasses_case": "Glasses case (length EST)", "usb_stick": "USB stick",
    "yubikey": "YubiKey", "metal_stick": "Metal stick",
}


def export(variant):
    p, items = build(variant)
    v = VARIANTS[variant]
    asm = Assembly("desk-organizer", variant, title=f"Desk organizer: {v['title'].lower()}",
                   description=f"{v['title']}: the same pockets, grouped differently.")
    for k, shape in p.items():
        if k == "baseplate":
            nx, ny = v["grid"]
            asm.add(k, shape, f"Baseplate, {nx} x {ny}", material="PLA", color="#8a9099",
                    description=f"Open Gridfinity frame, {nx * 42} x {ny * 42} mm. One print.")
            continue
        name, color, desc = LABELS[k]
        asm.add(k, shape, name, material="PLA", color=color, explode=(0, 0, 40), description=desc)
    for k, s in items.items():
        asm.add(f"item_{k}", s, ITEM_NAMES[k], color="#d9d4cc", source="bought", layer="Items",
                explode=(0, 0, 40), description="Yours, for scale and fit.", notes=["reference only"])
    asm.export()


if __name__ == "__main__":
    for name in VARIANTS:
        export(name)
