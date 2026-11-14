"""modelkit build [project ...]   run every project's CAD / physics / KiCad exports
modelkit new <slug> [--title T]  start a project from templates/project
modelkit list
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

from .paths import DATA, PROJECTS, ROOT, TEMPLATE, data_dir


def projects():
    return sorted(p.parent.name for p in PROJECTS.glob("*/project.yaml"))


def run_scripts(slug: str) -> bool:
    ok = True
    pdir = PROJECTS / slug
    for sub in ("cad", "physics"):
        for script in sorted((pdir / sub).glob("[!_]*.py")):
            print(f"{slug}/{sub}/{script.name}")
            r = subprocess.run([sys.executable, str(script)], cwd=pdir)
            ok &= r.returncode == 0
    return ok


def run_kicad(slug: str) -> bool:
    """Export schematic SVGs, a BOM CSV and a board GLB/STEP for each KiCad project."""
    pros = sorted((PROJECTS / slug / "electronics").glob("**/*.kicad_pro"))
    if not pros:
        return True
    cli = shutil.which("kicad-cli")
    if not cli:
        print(f"{slug}: kicad-cli not on PATH, skipping {len(pros)} KiCad project(s)")
        return True
    ok = True
    for pro in pros:
        out = data_dir(slug, "electronics", pro.stem)
        sch, pcb = pro.with_suffix(".kicad_sch"), pro.with_suffix(".kicad_pcb")
        jobs = []
        if sch.exists():
            jobs += [
                ["sch", "export", "svg", "--exclude-drawing-sheet", "-o", str(out), str(sch)],
                ["sch", "export", "pdf", "-o", str(out / "schematic.pdf"), str(sch)],
                ["sch", "export", "bom", "-o", str(out / "bom.csv"), str(sch)],
            ]
        if pcb.exists():
            jobs += [
                ["pcb", "export", "glb", "--subst-models", "-f", "-o", str(out / "board.glb"), str(pcb)],
                ["pcb", "export", "step", "--subst-models", "-f", "-o", str(out / "board.step"), str(pcb)],
            ]
        for job in jobs:
            print(f"{slug}: kicad-cli {' '.join(job[:3])}")
            ok &= subprocess.run([cli, *job]).returncode == 0
    return ok


def cmd_build(args):
    slugs = args.projects or projects()
    unknown = set(slugs) - set(projects())
    if unknown:
        sys.exit(f"unknown project(s): {', '.join(sorted(unknown))}")
    failed = [s for s in slugs if not (run_scripts(s) & run_kicad(s))]
    if failed:
        sys.exit(f"FAILED: {', '.join(failed)}")
    print(f"built {len(slugs)} project(s) -> {DATA.relative_to(ROOT)}/")


def cmd_new(args):
    slug = args.slug
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit("slug must be lowercase letters, digits and dashes")
    dest = PROJECTS / slug
    if dest.exists():
        sys.exit(f"{dest} already exists")
    shutil.copytree(TEMPLATE, dest)
    title = args.title or slug.replace("-", " ").title()
    for f in dest.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".yaml", ".mdx", ".md"}:
            f.write_text(f.read_text().replace("__SLUG__", slug).replace("__TITLE__", title))
    print(f"created {dest.relative_to(ROOT)}/ — next: make build && make dev")


def main():
    ap = argparse.ArgumentParser(prog="modelkit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("projects", nargs="*")
    b.set_defaults(fn=cmd_build)
    n = sub.add_parser("new")
    n.add_argument("slug")
    n.add_argument("--title")
    n.set_defaults(fn=cmd_new)
    sub.add_parser("list").set_defaults(fn=lambda a: print("\n".join(projects())))
    os.chdir(ROOT)
    args = ap.parse_args()
    args.fn(args)
