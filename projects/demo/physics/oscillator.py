"""Starter physics model: the post as a damped oscillator, numeric vs closed form."""

import numpy as np
from scipy.integrate import solve_ivp

from modelkit import save_series

M = 0.050   # kg, cap mass (placeholder)
K = 180.0   # N/m, lateral stiffness (placeholder)
C = 0.12    # N s/m, damping (placeholder)
X0 = 5.0    # mm, initial deflection

t = np.linspace(0, 2.0, 400)
sol = solve_ivp(lambda _, y: [y[1], -(K * y[0] + C * y[1]) / M], (0, t[-1]), [X0, 0], t_eval=t, rtol=1e-8)

wn = np.sqrt(K / M)
zeta = C / (2 * np.sqrt(K * M))
envelope = X0 * np.exp(-zeta * wn * t)

save_series(
    "demo", "oscillator", t,
    {"Deflection": sol.y[0], "Decay envelope": envelope},
    title="Free vibration after a 5 mm push",
    x_label="time (s)", y_label="deflection (mm)",
    params={"mass_kg": M, "stiffness_N_per_m": K, "damping_Ns_per_m": C,
            "natural_freq_Hz": round(wn / (2 * np.pi), 2), "damping_ratio": round(zeta, 4)},
)
