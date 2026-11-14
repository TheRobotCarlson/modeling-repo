from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT / "projects"
TEMPLATE = ROOT / "templates" / "project"
DATA = ROOT / "site" / "public" / "data"


def data_dir(project: str, *parts: str) -> Path:
    """Generated-output directory for a project (served by the site at /data/<project>/)."""
    d = DATA.joinpath(project, *parts)
    d.mkdir(parents=True, exist_ok=True)
    return d
