"""How hard the press is to turn, and the time it saves over a knife.

Berry shape (EST, from supermarket berries): width W 24 to 36 mm, length 1.1 to
1.3 W.

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
HANDLE = 215.0              # knob radius on the press
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
save_series("berry-dicer", "force", travel, force,
            title="Platen force, 27 berries lying in the hopper",
            x_label="Platen travel from the tallest berry, mm", y_label="Force, N",
            params={"berries": BATCH, "cell_mm": CELL, "K_N_per_mm": K, "peak_N": round(peak),
                    "peak_high_K_N": round(max(force["K = 0.2 N/mm"])),
                    "hand_N": round(hand, 1), "handle_mm": HANDLE, "ratio": round(HANDLE / PINION_R, 1)})
print(f"  peak {peak:.0f} N at K={K}, hand {hand:.1f} N")



# --- time each week ----------------------------------------------------------------
KNIFE_S = 10.0              # EST: hull and dice one berry on a board
HULL_S = 2.0                # EST: pinch the leaves off and drop the berry in the hopper
PRESS_S = 25.0              # EST: four clicks and sweeps, per batch
CLEAN = {"knife": 60.0, "press": 120.0}      # EST: rinse a board; load the cartridge in the dishwasher


def week_minutes(n):
    knife = KNIFE_S * n + CLEAN["knife"]
    press = HULL_S * n + PRESS_S * math.ceil(n / BATCH) + CLEAN["press"]
    return knife / 60, press / 60


ns = np.arange(10, 121, 5)
mins = np.array([week_minutes(n) for n in ns])
even = next(int(n) for n in range(1, 200) if week_minutes(n)[1] < week_minutes(n)[0])
save_series("berry-dicer", "time", ns,
            {"Knife and board": mins[:, 0], "Press": mins[:, 1]},
            title="Hands-on minutes per week", x_label="Berries per week", y_label="Minutes",
            params={"knife_s_per_berry": KNIFE_S, "hull_s_per_berry": HULL_S, "press_s_per_batch": PRESS_S,
                    "knife_60": round(week_minutes(60)[0], 1), "press_60": round(week_minutes(60)[1], 1),
                    "pays_back_above": even})
print(f"  60 berries: knife {week_minutes(60)[0]:.1f} min, press {week_minutes(60)[1]:.1f} min; press wins from {even}")
