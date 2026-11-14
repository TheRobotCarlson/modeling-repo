"""__TITLE__ — starter assembly. Millimetres, Z up. Run via `make build`."""

from build123d import Align, Box, Cylinder, Pos

from modelkit import Assembly

PLATE = (80, 60, 6)
POST_D, POST_H = 12, 70
BOSS_H = 10
CAP_D, CAP_H = 24, 8
FIT = 0.2  # diametral clearance for printed slip fits

bottom = (Align.CENTER, Align.CENTER, Align.MIN)

plate = Box(*PLATE, align=bottom) + Pos(0, 0, PLATE[2]) * Cylinder(POST_D, BOSS_H, align=bottom)
plate -= Pos(0, 0, 2) * Cylinder(POST_D / 2 + FIT / 2, PLATE[2] + BOSS_H, align=bottom)
for sx in (-1, 1):
    for sy in (-1, 1):
        plate -= Pos(sx * 32, sy * 22, 0) * Cylinder(2.2, PLATE[2], align=bottom)

post = Pos(0, 0, 2) * Cylinder(POST_D / 2, POST_H, align=bottom)

cap = Pos(0, 0, 2 + POST_H - 6) * (
    Cylinder(CAP_D / 2, CAP_H, align=bottom)
    - Cylinder(POST_D / 2 + FIT / 2, 6, align=bottom)
)

asm = Assembly("__SLUG__", "main", title="__TITLE__", description="Plate, post and cap.")
asm.add("plate", plate, "Base plate", material="PETG", color="#4f7cac", explode=(0, 0, -30),
        description="Printed base with a socket for the post and four M4 clearance holes.")
asm.add("post", post, "Post", material="Aluminum 6061", color="#b8bec6", source="bought",
        description="12 mm aluminium rod, cut to 70 mm.", notes=["cut length: measure"])
asm.add("cap", cap, "Cap", material="PETG", color="#e0a23c", explode=(0, 0, 35),
        description="Printed cap, slip fit on the post.")
asm.export()
