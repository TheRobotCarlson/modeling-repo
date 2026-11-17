"""Assemble build123d parts and export everything the site and a workshop need.

For each part: STEP + STL (downloads) and GLB (web viewer).
For the assembly: one STEP and a manifest.json the viewer and tables read.

Model in millimetres, Z up.
"""

import json
from dataclasses import dataclass, field

from build123d import Compound, Location, export_gltf, export_step, export_stl
from build123d.topology import Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

from .paths import data_dir

# density in g/cm^3
MATERIALS = {
    "PLA": 1.24,
    "PETG": 1.27,
    "ABS": 1.05,
    "ASA": 1.07,
    "Nylon": 1.14,
    "TPU": 1.21,
    "Aluminum 6061": 2.70,
    "Steel": 7.85,
    "Stainless 304": 8.00,
    "Brass": 8.50,
    "Copper": 8.96,
    "FR4": 1.85,
    "Acrylic": 1.18,
    "Polycarbonate": 1.20,
    "Carbon fiber": 1.60,
}

SOURCES = ("printed", "machined", "bought", "pcb")


def baked(shape):
    """Copy of `shape` with its placement applied to the geometry itself.

    The glTF writer emits a shape's Location as a node translation without
    converting it from Z-up to Y-up, so a part placed with Pos(0, 0, 50) lands
    50 mm sideways in the viewer. Baking leaves nothing for it to get wrong.
    """
    moved = BRepBuilderAPI_Transform(
        shape.wrapped.Located(Location().wrapped), shape.location.wrapped.Transformation(), True
    ).Shape()
    return Shape.cast(moved)


@dataclass
class Part:
    id: str
    shape: object
    name: str
    material: str | None = None
    color: str = "#9aa3ad"
    source: str = "printed"
    explode: tuple[float, float, float] = (0, 0, 0)
    description: str = ""
    mpn: str = ""
    mass_g: float | None = None  # override for bought parts with a datasheet mass
    notes: list[str] = field(default_factory=list)
    layer: str = ""  # optional overlay (e.g. "Wiring"): hidden in the viewer until toggled on

    def mass(self) -> tuple[float | None, str]:
        """(grams, where the number came from)."""
        if self.mass_g is not None:
            return self.mass_g, "given"
        if self.material in MATERIALS:
            return self.shape.volume / 1000 * MATERIALS[self.material], "volume x density"
        return None, "unknown"


class Assembly:
    def __init__(self, project: str, name: str, title: str = "", description: str = ""):
        self.project, self.name = project, name
        self.title, self.description = title or name, description
        self.parts: list[Part] = []

    def add(self, id: str, shape, name: str = "", **kw) -> Part:
        """Add a positioned shape. `explode` is the mm offset at full explode."""
        if any(p.id == id for p in self.parts):
            raise ValueError(f"duplicate part id {id!r}")
        if kw.get("source", "printed") not in SOURCES:
            raise ValueError(f"source must be one of {SOURCES}")
        mat = kw.get("material")
        if mat and mat not in MATERIALS and kw.get("mass_g") is None:
            raise ValueError(f"unknown material {mat!r}; add it to MATERIALS or pass mass_g")
        part = Part(id=id, shape=baked(shape), name=name or id, **kw)
        self.parts.append(part)
        return part

    def export(self):
        out = data_dir(self.project, "cad", self.name)
        for old in out.iterdir():
            old.unlink()
        entries, total, lo, hi = [], 0.0, [1e9] * 3, [-1e9] * 3
        for p in self.parts:
            p.shape.label = p.id
            export_step(p.shape, str(out / f"{p.id}.step"))
            export_stl(p.shape, str(out / f"{p.id}.stl"))
            export_gltf(p.shape, str(out / f"{p.id}.glb"), binary=True)
            bb = p.shape.bounding_box()
            mn, mx = tuple(bb.min), tuple(bb.max)
            lo = [min(a, b) for a, b in zip(lo, mn)]
            hi = [max(a, b) for a, b in zip(hi, mx)]
            mass, mass_from = p.mass()
            total += mass or 0
            entries.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "source": p.source,
                    "material": p.material,
                    "mpn": p.mpn,
                    "color": p.color,
                    "mass_g": None if mass is None else round(mass, 2),
                    "mass_from": mass_from,
                    "volume_mm3": round(p.shape.volume, 1),
                    "size_mm": [round(b - a, 2) for a, b in zip(mn, mx)],
                    "explode_mm": list(p.explode),
                    "description": p.description,
                    "notes": p.notes,
                    "layer": p.layer,
                    "files": {k: f"{p.id}.{k}" for k in ("glb", "stl", "step")},
                }
            )
        export_step(
            Compound(label=self.name, children=[p.shape for p in self.parts]),
            str(out / f"{self.name}.step"),
        )
        manifest = {
            "project": self.project,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "units": "mm, Z up (GLB files are metres, Y up)",
            "size_mm": [round(b - a, 2) for a, b in zip(lo, hi)],
            "mass_g": round(total, 2),
            "assembly_step": f"{self.name}.step",
            "parts": entries,
        }
        (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
        print(f"  cad  {self.name}: {len(entries)} parts, {total:.1f} g")
        return manifest
