"""Write simulation results where the site's <Chart> component can find them."""

import json
from typing import Mapping, Sequence

from .paths import data_dir


def save_series(
    project: str,
    name: str,
    x: Sequence[float],
    series: Mapping[str, Sequence[float]],
    *,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    params: Mapping[str, object] | None = None,
    digits: int = 5,
):
    """Save one x axis and one or more named y series as sim/<name>.json.

    `params` records the inputs the run used, so a page can quote them
    instead of repeating numbers by hand.
    """

    def rnd(v):
        return [float(f"{float(a):.{digits}g}") for a in v]

    out = {
        "name": name,
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "x": rnd(x),
        "series": [{"name": k, "y": rnd(v)} for k, v in series.items()],
        "params": dict(params or {}),
    }
    for s in out["series"]:
        if len(s["y"]) != len(out["x"]):
            raise ValueError(f"series {s['name']!r} length differs from x")
    path = data_dir(project, "sim") / f"{name}.json"
    path.write_text(json.dumps(out))
    print(f"  sim  {path.relative_to(path.parents[4])}")
    return path
