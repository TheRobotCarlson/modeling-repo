# Modeling notebook

A shared workspace for hardware modeling projects. Each project holds its CAD,
physics models, electronics and bill of materials, plus a short series of pages
that explain the model piece by piece. The pages build into one static site.

## Quick start

```sh
make setup     # uv sync + pnpm install
make dev       # export all model data, then serve the site at localhost:4321
make new name=my-project title="My project"
```

Needs [uv](https://docs.astral.sh/uv/), Node 22+ with pnpm, and (for
electronics) KiCad 8+ with `kicad-cli` on the PATH.

## Layout

```
projects/<slug>/
  project.yaml        title, summary, status, order on the home page
  cad/*.py            build123d scripts -> STEP, STL, GLB + manifest.json
  physics/*.py        numpy/scipy models -> JSON series for charts
  electronics/        KiCad projects, exported by kicad-cli
  bom.yaml            line items with manufacturer part numbers and cost
  pages/NN-name.mdx   the narrative, one page per file, in filename order
lib/modelkit/         shared Python: Assembly export, save_series, the CLI
templates/project/    what `modelkit new` copies
site/                 Astro site: layout, 3D viewer, chart and table components
tests/
```

`make build` runs every `cad/*.py` and `physics/*.py` (files starting with `_`
are skipped, so use those for shared helpers) and writes to
`site/public/data/<slug>/`. That directory is generated and not committed.

## Writing a page

Pages are MDX. Lead each section with one bold sentence, then a short
paragraph, then put the depth inside `<details>`. These components are
available without importing them:

| Component | Shows |
|---|---|
| `<ModelViewer assembly="main" />` | Interactive 3D view: orbit, take-apart slider, click a part for details |
| `<PartsTable assembly="main" />` | Every part with source, material, mass and size |
| `<Downloads assembly="main" />` | STL / STEP / GLB links |
| `<Chart sim="oscillator" />` | Line chart of a `save_series` result (up to 3 series) |
| `<Params sim="oscillator" />` | The inputs that run used |
| `<Bom />` | `bom.yaml` as a table with totals and open rows flagged |
| `<Stats><Stat value="3" label="parts" /></Stats>` | Headline numbers |
| `<Callout title="...">` | A caveat the reader must not miss |

Components read the current project automatically; pass `project="other"` to
pull from a different one.

## Modeling conventions

- Millimetres, Z up. `Assembly.add(id, shape, ...)` takes a positioned
  build123d shape; `explode=(x, y, z)` is how far the part moves at full
  take-apart.
- Mass comes from volume × material density (`modelkit.MATERIALS`) unless
  `mass_g` is given, which is the right choice for bought parts.
- Numbers on pages should come from the manifest or a sim's `params`, not be
  retyped. Anything unverified gets a `notes=["...: measure"]` tag.

## Deploying

`.github/workflows/pages.yml` builds and publishes to GitHub Pages on every
push to `main`. Enable it under Settings → Pages → Source: GitHub Actions.
