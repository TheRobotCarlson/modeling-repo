"""How hard the press pushes, how much fruit the topping cut wastes, and the time it saves.

Berry shape (EST, from supermarket berries): width W 24 to 36 mm, length 1.1 to
1.3 W. A blunt shoulder at the leafy end, a half spheroid of radius W/2 and depth
0.6 W/2, then a cone to the tip.

Cutting: a sharp edge going through strawberry flesh needs a force per millimetre
of edge, K (EST, 0.1 N/mm; the measure page says how to weigh it on a kitchen
scale). A square grid of pitch c crossing a section of area A has 2A/c of edge in
it, so a berry being pushed through needs K * 2A/c. Friction of the pieces in the
cells is left out.
"""

import math

import numpy as np

from modelkit import save_series

CELL = 12.0
K = 0.10                    # N per mm of edge (EST)
BATCH = 27                  # three rows of nine
PINION_R = 8 * CELL / (2 * math.pi)
HANDLE = 215.0              # knob radius on the manual press
EFF = 0.8                   # rack, pinion and stem friction (EST)
SEED = 4

rng = np.random.default_rng(SEED)
W = rng.uniform(24, 36, BATCH)
L = W * rng.uniform(1.1, 1.3, BATCH)


def lying_area(z, w, length):
    """Horizontal section of a berry lying on its side, z above its lowest point.

    Taken as an ellipsoid of length x width x width: close enough for the press.
    """
    r = w / 2
    u = (z - r) / r
    return np.where(np.abs(u) < 1, math.pi * (length / 2) * r * (1 - u ** 2), 0.0)


def press_force(gap, k=K, cell=CELL):
    """Platen force, newtons, with the platen `gap` mm above the grid top.

    Each berry has been pushed in by (its height - gap); the grid's top plane cuts
    it at that height above its bottom.
    """
    depth = np.clip(W - gap, 0, None)
    a = lying_area(depth, W, L)
    return float(np.sum(k * 2 * a / cell))


gaps = np.linspace(40, 0, 161)
force = {f"K = {k:g} N/mm": [press_force(g, k) for g in gaps] for k in (0.05, 0.1, 0.2)}
travel = 40 - gaps
peak = max(force["K = 0.1 N/mm"])
hand = peak * PINION_R / HANDLE / EFF
# Automated press: two NEMA 17s on T8 lead screws. Thrust = 2 pi T eff / lead.
T_MOTOR = 0.30              # N m each, usable at speed (EST: a 0.45 N m motor derated)
MU = 0.15                   # nut friction, brass on stainless (EST)


def screw_thrust(lead_mm, d_mm=8.0):
    lam = math.atan(lead_mm / (math.pi * (d_mm - lead_mm / 2)))
    eff = math.tan(lam) / math.tan(lam + math.atan(MU))
    return 2 * 2 * math.pi * T_MOTOR * eff / (lead_mm / 1000)


THRUST = {lead: round(screw_thrust(lead)) for lead in (2.0, 8.0)}
print(f"  two motors: {THRUST[2.0]} N on 2 mm lead, {THRUST[8.0]} N on 8 mm lead")

save_series("berry-dicer", "force", travel, force,
            title="Platen force, 27 berries lying in the hopper",
            x_label="Platen travel from the tallest berry, mm", y_label="Force, N",
            params={"berries": BATCH, "cell_mm": CELL, "K_N_per_mm": K, "peak_N": round(peak),
                    "peak_high_K_N": round(max(force["K = 0.2 N/mm"])),
                    "thrust_2mm_lead_N": THRUST[2.0], "thrust_8mm_lead_N": THRUST[8.0],
                    "hand_N": round(hand, 1), "handle_mm": HANDLE, "ratio": round(HANDLE / PINION_R, 1)})
print(f"  peak {peak:.0f} N at K={K}, hand {hand:.1f} N")



# --- how much the topping cut takes ------------------------------------------------
def shape_volume(w, length):
    r, a = w / 2, 0.6 * w / 2
    return 2 / 3 * math.pi * r * r * a + math.pi * r * r * (length - a) / 3


def cap_volume(h, w):
    """Volume within h of the leafy end: a slice of the blunt half spheroid."""
    r, a = w / 2, 0.6 * w / 2
    if h <= a:
        return math.pi * r * r / (a * a) * h * h * (3 * a - h) / 3
    return 2 / 3 * math.pi * r * r * a + math.pi * r * r * (h - a) * (1 - (h - a) / (3 * (length_of(w) - a)))


def length_of(w):
    return 1.2 * w


caps = np.linspace(3, 10, 29)
waste = {}
for label, w in (("Small, 24 mm", 24.0), ("Medium, 30 mm", 30.0), ("Large, 36 mm", 36.0)):
    waste[label] = [100 * cap_volume(h, w) / shape_volume(w, length_of(w)) for h in caps]
save_series("berry-dicer", "waste", caps, waste,
            title="Fruit lost with the top, by berry size",
            x_label="Cut distance from the leafy end, mm", y_label="Lost, % of the berry",
            params={"default_cut_mm": 5, "medium_at_5mm_pct": round(waste["Medium, 30 mm"][8], 1),
                    "small_at_5mm_pct": round(waste["Small, 24 mm"][8], 1)})


# --- time each week ----------------------------------------------------------------
KNIFE_S = 10.0              # EST: hull and dice one berry on a board
PLACE_S = 1.5               # EST: lay one berry in the topper tray
ROW_S = 6.0                 # EST: swing the wire, flip the flap, tip the tray
PRESS_S = 25.0              # EST: four clicks and sweeps, per batch
CLEAN = {"knife": 60.0, "tools": 180.0}      # EST: rinse a board; load the parts in the dishwasher


def week_minutes(n):
    rows, batches = math.ceil(n / 9), math.ceil(n / BATCH)
    knife = KNIFE_S * n + CLEAN["knife"]
    manual = PLACE_S * n + ROW_S * rows + PRESS_S * batches + CLEAN["tools"]
    auto = PLACE_S * n + 2.0 * rows + CLEAN["tools"]
    return knife / 60, manual / 60, auto / 60


ns = np.arange(10, 121, 5)
mins = np.array([week_minutes(n) for n in ns])
save_series("berry-dicer", "time", ns,
            {"Knife and board": mins[:, 0], "Manual topper and press": mins[:, 1], "Automated": mins[:, 2]},
            title="Hands-on minutes per week", x_label="Berries per week", y_label="Minutes",
            params={"knife_s_per_berry": KNIFE_S, "place_s": PLACE_S, "row_s": ROW_S, "press_s_per_batch": PRESS_S,
                    "knife_60": round(week_minutes(60)[0], 1), "manual_60": round(week_minutes(60)[1], 1),
                    "auto_60": round(week_minutes(60)[2], 1)})
