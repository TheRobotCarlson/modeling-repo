"""Will the shade's bottom bar slide down the ramp, or sit on it?

The bar rests on a ramp tilted `theta` from horizontal. Friction (coefficient mu)
holds it; so does the shade, which hangs like a pendulum and pulls the bar back
towards where it wants to hang. With the bar pushed x sideways on a drop of
length L below the roller, the pull-back is W*x/L. Balancing forces along and
across the ramp, the bar slides when

    theta > atan(mu) + atan(x / L)
"""

import sys

import numpy as np

sys.path.insert(0, "cad")
from _dims import OVERLAP_MAX, RAMP_DEG  # noqa: E402

from modelkit import save_series  # noqa: E402

DROP_MIN = 150.0   # mm from roller to the motor's top: shortest plausible (EST: measure)

mu = np.linspace(0.05, 1.6, 150)
swing = np.degrees(np.arctan(OVERLAP_MAX / DROP_MIN))
needed = np.degrees(np.arctan(mu)) + swing
mu_limit = float(np.tan(np.radians(RAMP_DEG - swing)))

save_series(
    "blind-guide", "ramp", mu,
    {"Steepness needed to slide": needed, "Ramp as designed": np.full_like(mu, RAMP_DEG)},
    title="How steep the ramp must be, by how grippy its surface is",
    x_label="friction coefficient between bar and ramp", y_label="ramp angle from horizontal (deg)",
    params={"ramp_angle_deg": RAMP_DEG, "sideways_push_mm": OVERLAP_MAX, "shortest_drop_mm": DROP_MIN,
            "pendulum_allowance_deg": round(swing, 1), "slides_up_to_friction_of": round(mu_limit, 2)},
)
