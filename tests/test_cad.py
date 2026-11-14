import json
import struct

from build123d import Align, Box, Pos

from modelkit import Assembly, paths


def glb_json(path):
    d = path.read_bytes()
    return json.loads(d[20 : 20 + struct.unpack("<I", d[12:16])[0]])


def test_export_places_parts_in_the_viewer_frame(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "DATA", tmp_path)
    asm = Assembly("t", "a")
    asm.add("box", Pos(0, 0, 50) * Box(10, 20, 30, align=Align.MIN), material="PETG", explode=(0, 0, 10))
    m = asm.export()

    out = tmp_path / "t" / "cad" / "a"
    assert {f.name for f in out.iterdir()} == {"box.glb", "box.stl", "box.step", "a.step", "manifest.json"}
    part = m["parts"][0]
    assert part["size_mm"] == [10, 20, 30]
    assert part["mass_g"] == round(6000 / 1000 * 1.27, 2)

    # Placement must be in the vertices (metres), not in an unconverted node translation.
    g = glb_json(out / "box.glb")
    assert all("translation" not in n for n in g["nodes"])
    zs = [a for a in g["accessors"] if len(a.get("min", [])) == 3]
    assert min(a["min"][2] for a in zs) == 0.05 and max(a["max"][2] for a in zs) == 0.08
