# Electronics

Put KiCad projects here, one folder each (`electronics/<board>/<board>.kicad_pro`).
`make build` runs `kicad-cli` on every project it finds and exports the
schematic (SVG + PDF), a BOM CSV and the board as GLB + STEP to
`site/public/data/__SLUG__/electronics/<board>/`.

Chosen parts also go in `../bom.yaml` with manufacturer part numbers.
