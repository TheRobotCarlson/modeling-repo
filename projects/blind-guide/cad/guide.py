"""Shade guide v0: a cap for the top of the AXIS Gear with a ramp on the glass side.

The shade's bottom bar lands on the glass-side edge of the motor's top. The ramp
catches it above that edge and slides it towards the glass, onto a thin skin that
runs down the motor's side. Glass is at -X here; `guide-mirrored` is the other hand.

Prints front face down (Y up): the whole part is one profile pulled along Y, so it
needs no support and the layer lines run along the direction the bar slides.
"""

import math

from build123d import Box, Plane, Polygon, Pos, Rot, extrude, mirror

import gear as g
from _dims import OVERLAP_MAX, RAMP_DEG
from modelkit import Assembly

FIT = 0.3          # clearance to the motor, per side
SKIN = 1.2         # glass-side wall: the gap there is "just large enough for something thin"
WALL = 2.4         # room-side wall
TOP = 2.0          # plate over the motor's top
FRONT = 2.0        # front lip
SKIN_DROP, WALL_DROP, FRONT_DROP = 40.0, 30.0, 14.0   # how far each wall reaches down
RAMP_START = 4.0   # ramp begins this far below the motor's top, on the skin
CHAIN_GAP = 0.8    # ramp stops this far short of the glass-side chain run
SLOT_W = 9.0       # chain slots, open to the back so the cap goes on around the chain
PAD_T, PAD_RECESS = 0.8, 0.5

H, W = g.H, g.W
x_g = -(W / 2 + FIT + SKIN)                       # outer face, glass side
x_f = W / 2 + FIT + WALL                          # outer face, room side
z_top = H + FIT + TOP
x_a = -(g.COG_PITCH_R + g.BEAD_D / 2 + CHAIN_GAP)  # ramp crest
z_r0 = H - RAMP_START
z_a = z_r0 + (x_a - x_g) * math.tan(math.radians(RAMP_DEG))
y0 = g.front - FIT - FRONT
y1 = g.back + g.BRACKET_D - 0.5                   # reaches back over the wall mount
chain_y = g.back - 9

reach = x_a - (-W / 2)                             # how much of the motor's top the ramp covers
assert reach >= OVERLAP_MAX, f"ramp covers {reach:.1f} mm, bar overlaps up to {OVERLAP_MAX}"


def prism(pts, ya, yb):
    """Polygon in the XZ plane, pulled from ya to yb along Y."""
    return Pos(0, yb, 0) * Rot(90, 0, 0) * extrude(Polygon(*pts, align=None), yb - ya, dir=(0, 0, 1))


profile = [
    (x_g + 1.0, H - SKIN_DROP), (x_g, H - SKIN_DROP + 6),   # feathered lower edge
    (x_g, z_r0), (x_a, z_a), (x_a, z_top),                  # skin, ramp, crest
    (x_f, z_top), (x_f, H - WALL_DROP),
]
body = prism(profile, y0, y1)
body -= g.slab(W + 2 * FIT, H + 2 * FIT, g.CORNER_R + FIT, g.front - FIT, y1 + 1, H / 2)   # the motor
body -= Pos(0, (g.back + FIT + y1 + 1) / 2, H + FIT - 50) * Box(80, y1 + 1 - g.back - FIT, 100)  # open back
body -= Pos(0, (y0 - 1 + g.front - FIT) / 2, H - FRONT_DROP - 50) * Box(80, g.front - FIT - y0 + 1, 100)  # short front lip
for sx in (-1, 1):
    ya = chain_y - SLOT_W / 2
    body -= Pos(sx * g.COG_PITCH_R, (ya + y1 + 1) / 2, H + 14) * Box(SLOT_W, y1 + 1 - ya, 30)

pad_side = Pos(W / 2 + PAD_T / 2, 0, H - 18) * Box(PAD_T, 24, 16)
pad_front = Pos(0, g.front - PAD_T / 2, H - 8.5) * Box(20, PAD_T, 7)
body -= pad_side
body -= pad_front

# --- export -------------------------------------------------------------------
BODY = dict(material="PETG", color="#2f6fb7", source="printed")
PAD = dict(material="TPU", color="#e0803a", source="printed")
BODY_DESC = ("Rigid cap. The ramp on the glass side meets the shade's bottom bar above the "
             "motor and slides it sideways onto the thin skin.")

asm = Assembly("blind-guide", "guide", title="Guide on the motor",
               description="Cap with a glass-side ramp, shown on the AXIS Gear.")
ref = dict(source="bought", notes=["reference only"])
asm.add("housing", g.housing, "AXIS Gear", color="#f1f1ee", mpn="GR-ZB01-W", mass_g=314,
        description="The motor, for reference.", **ref)
asm.add("band", g.band, "Rim", color="#8b93a5", description="Motor rim.", **ref)
asm.add("button", g.button, "Power button", color="#dfe3e8", description="Stays uncovered.", **ref)
asm.add("strip", g.strip, "Touch strip", color="#bcd0ea", description="Stays uncovered.", **ref)
asm.add("chain", g.chain, "Shade chain", color="#9aa1a8",
        description="Runs up through the two slots in the cap.", **ref)
asm.add("cog", g.cog, "Cogwheel", color="#d6d3c8", description="Drives the chain.", **ref)
asm.add("cover", g.cover, "Back cover", color="#e4e4df", description="Covers the cogwheel.", **ref)
asm.add("bracket", g.bracket, "Mounting bracket", color="#d9d9d3", description="Wall bracket.", **ref)
asm.add("guide-body", body, "Guide body", explode=(0, 0, 55), description=BODY_DESC,
        notes=["fit to motor: test print", f"ramp covers {reach:.1f} mm of the top: measure the overlap"], **BODY)
asm.add("pad-side", pad_side, "Grip pad, side", explode=(14, 0, 55),
        description="Soft 75A TPU pad that presses on the motor's room-side face.", **PAD)
asm.add("pad-front", pad_front, "Grip pad, front", explode=(0, -14, 55),
        description="Soft 75A TPU pad that presses on the motor's front, above the power button.", **PAD)
asm.export()

flip = Assembly("blind-guide", "guide-mirrored", title="Guide, mirrored",
                description="The same cap for a motor with the glass on its other side.")
flip.add("guide-body", mirror(body, Plane.YZ), "Guide body", description=BODY_DESC, **BODY)
flip.add("pad-side", mirror(pad_side, Plane.YZ), "Grip pad, side", explode=(-14, 0, 0),
         description="75A TPU grip pad.", **PAD)
flip.add("pad-front", mirror(pad_front, Plane.YZ), "Grip pad, front", explode=(0, -14, 0),
         description="75A TPU grip pad.", **PAD)
flip.export()
print(f"  ramp: {RAMP_DEG:.0f} deg, crest {z_a - H:.1f} mm above the motor, covers {reach:.1f} mm of its top")
