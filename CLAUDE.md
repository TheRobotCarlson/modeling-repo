# Modeling notebook

Common workspace for hardware modeling projects; see README.md for layout and commands.

- `make build` (model data) → `make site` (static build) → `make test`. Run all three before calling work done; open the page in a browser for anything visual.
- New project: `make new name=<slug>`. Never hand-copy another project.
- CAD is build123d, mm, Z up. Export only through `modelkit.Assembly` — it bakes part placement into geometry because the glTF writer mishandles shape Locations (tests/test_cad.py guards this).
- Shared Python goes in `lib/modelkit`; shared page components in `site/src/components` and must be registered in `components/mdx.ts`.
- `site/public/data/` is generated. Do not commit it or edit it by hand.
- Page voice: one bold lead sentence per section, short paragraph, depth inside `<details>`. Say plainly what is modeled versus built or measured.
- Part numbers go in `bom.yaml`; never invent an MPN — leave it empty and the site flags the row.
- Charts: at most 3 series, one y axis; split otherwise.
