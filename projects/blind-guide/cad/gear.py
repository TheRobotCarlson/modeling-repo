"""AXIS Gear shade motor (GR-ZB01-W) — reference model to design the guide around.

Millimetres, Z up. X is width, the front face is at -Y, the back (wall side) at +Y.

Only the three envelope numbers are from the manufacturer. Everything marked
EST is scaled from the manual's line drawings and the box photos and must be
checked with calipers before a printed part depends on it.
"""

import math

from build123d import Box, Compound, Cylinder, Pos, RectangleRounded, Rot, Sphere, extrude

from modelkit import Assembly

# --- from the manufacturer's dimension drawing (partner documentation v1.4, p.5)
W, D, H = 46.0, 38.0, 165.0
# --- box label says 43 x 47 x 169; 47 is read here as depth including the bracket
BRACKET_D = 47.0 - D  # 9 mm, inferred

# --- EST: scaled from drawings / photos
CORNER_R = 7.0
BAND = 1.5                      # width of the metal-look rim on the front
BUTTON = (20.0, 18.0, 16.0)     # w, h, distance from top edge
STRIP = (3.0, 96.0, 46.0)       # w, h, distance from top edge
COVER = (42.0, 58.0, 4.0)       # back cover w, h, distance from top edge
COG_PITCH_R = 16 * 6.0 / (2 * math.pi)   # 16 pockets at 6 mm bead pitch
COG_T, COG_DROP = 10.0, 32.0    # thickness, axis distance below the top
BEAD_D, BEAD_PITCH = 4.5, 6.0   # common roller-shade chain; the real chain is unmeasured
GROOVE_X, GROOVE_H = 17.0, 75.0
BRACKET_H, BRACKET_Z0 = 62.0, 12.0

front, back = -D / 2, D / 2


def slab(w, h, r, y0, y1, zc, xc=0.0):
    """Rounded rectangle in the XZ plane, extruded from y0 to y1."""
    s = extrude(RectangleRounded(w, h, r), y1 - y0)   # z in [0, depth]
    return Pos(xc, y1, zc) * Rot(90, 0, 0) * s        # depth now runs y1 -> y0


# --- body ------------------------------------------------------------------
housing = slab(W, H, CORNER_R, front, back, H / 2)
band = slab(W, H, CORNER_R, front, front + 3, H / 2) - slab(
    W - 2 * BAND, H - 2 * BAND, CORNER_R - BAND, front, front + 3, H / 2
)
housing -= band

cog_z = H - COG_DROP
cover_zc = H - COVER[2] - COVER[1] / 2
housing -= slab(COVER[0], COVER[1], 4, back - 2, back, cover_zc)                 # cover seat
housing -= Pos(0, back - 9, cog_z) * Box(38, 14, 50)                             # cogwheel bay
for sx in (-1, 1):
    housing -= Pos(sx * COG_PITCH_R, back - 9, H - 5) * Cylinder(3.6, 14)        # chain exits, top
    housing -= Pos(sx * GROOVE_X, back - 1.5, GROOVE_H / 2) * Box(3.2, 3, GROOVE_H)  # bracket grooves
housing -= Pos(0, 0, 3) * Box(10, 5, 6)                                          # power port, bottom

button = slab(BUTTON[0], BUTTON[1], 4, front - 0.6, front, H - BUTTON[2] - BUTTON[1] / 2)
strip = slab(STRIP[0], STRIP[1], 1.4, front - 0.3, front, H - STRIP[2] - STRIP[1] / 2)
top_buttons = Compound(children=[Pos(x, -9, H + 0.3) * Box(7, 4, 0.6) for x in (-12, 0, 12)])
cover = slab(COVER[0] - 0.4, COVER[1] - 0.4, 3.8, back - 2, back, cover_zc)

# --- cogwheel and chain ------------------------------------------------------
cog = Pos(0, back - 9, cog_z) * Rot(90, 0, 0) * Cylinder(COG_PITCH_R + 0.6, COG_T)
cog -= Pos(0, back - 9, cog_z) * Rot(90, 0, 0) * Cylinder(4, COG_T)
beads = []
for i in range(16):
    a = math.radians(i * 22.5)
    p = Pos(COG_PITCH_R * math.cos(a), back - 9, cog_z + COG_PITCH_R * math.sin(a))
    cog -= p * Sphere(BEAD_D / 2 + 0.3)
    if 8 < i < 16:   # lower half of the wheel carries the chain
        beads.append(p * Sphere(BEAD_D / 2))
for sx in (-1, 1):
    for k in range(15):
        beads.append(Pos(sx * COG_PITCH_R, back - 9, cog_z + k * BEAD_PITCH) * Sphere(BEAD_D / 2))
chain = Compound(children=beads)

# --- wall bracket -------------------------------------------------------------
bz = BRACKET_Z0 + BRACKET_H / 2
bracket = Pos(0, back + BRACKET_D - 2, bz) * Box(W, 4, BRACKET_H)                # base plate
for sx in (-1, 1):
    bracket += Pos(sx * (W / 2 - 1.5), back + 2.5, bz) * Box(3, 5, BRACKET_H)    # side walls
    bracket += Pos(sx * GROOVE_X, back + 1, bz) * Box(2.6, 8, BRACKET_H - 12)    # lips
bracket += Pos(0, back + 4, bz) * Box(14, 2, 44)                                 # ratchet tongue
for k in range(7):
    bracket += Pos(0, back + 2.5, bz - 18 + k * 6) * Box(10, 1, 2.5)             # ratchet ribs
for dz in (-BRACKET_H / 2 + 6, BRACKET_H / 2 - 6):
    bracket -= Pos(0, back + BRACKET_D - 2, bz + dz) * Rot(90, 0, 0) * Cylinder(2.2, 4)

# --- export -------------------------------------------------------------------
EST = "estimated from drawings: measure"
asm = Assembly("blind-guide", "gear", title="AXIS Gear shade motor",
               description="Reference model of the bought motor, its bracket and the shade chain.")
asm.add("housing", housing, "Housing", color="#f1f1ee", source="bought", mpn="GR-ZB01-W", mass_g=314,
        description="Motor body, 46 x 38 x 165 mm from the manufacturer's drawing. Mass is the whole unit, from the box.",
        notes=["corner radius, cutouts: measure"])
asm.add("band", band, "Rim", color="#8b93a5", source="bought", explode=(0, -14, 0),
        description="Metal-look band around the front face.", notes=[EST])
asm.add("button", button, "Power button", color="#dfe3e8", source="bought", explode=(0, -26, 0),
        description="Touch button with the AXIS logo: hold to power on, tap to stop.", notes=[EST])
asm.add("strip", strip, "Touch strip", color="#bcd0ea", source="bought", explode=(0, -26, 0),
        description="LED touch strip: top is fully open, bottom fully closed.", notes=[EST])
asm.add("top-buttons", top_buttons, "Set, Group and Pair buttons", color="#c9ccd1", source="bought",
        explode=(0, 0, 14), description="Three physical buttons on the top face.", notes=[EST])
asm.add("cog", cog, "Cogwheel", color="#d6d3c8", source="bought", explode=(0, 24, 0),
        description="Drives the chain. Sits in the upper back, behind the back cover.", notes=[EST])
asm.add("chain", chain, "Shade chain", color="#9aa1a8", source="bought", explode=(0, 24, 0),
        description="The shade's own bead chain: enters through the top and wraps under the cogwheel.",
        notes=["bead size and spacing: measure"])
asm.add("cover", cover, "Back cover", color="#e4e4df", source="bought", explode=(0, 46, 0),
        description="Snaps over the cogwheel. The motor will not power on without it.", notes=[EST])
asm.add("bracket", bracket, "Mounting bracket", color="#d9d9d3", source="bought", explode=(0, 46, 0),
        description="Screws or tapes to the frame. Two lips catch grooves in the motor's back; "
                    "the motor slides down on them to tension the chain.", notes=[EST])
asm.export()
