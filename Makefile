.PHONY: setup build dev site test new clean

setup:            ## install Python and Node dependencies
	uv sync
	cd site && pnpm install

build:            ## run every project's CAD, physics and KiCad exports
	uv run modelkit build $(project)

dev: build        ## rebuild model data, then serve the site with live reload
	cd site && pnpm dev

site: build       ## static build into site/dist
	cd site && pnpm build

test:
	uv run pytest -q
	cd site && pnpm astro check

new:              ## make new name=my-project title="My project"
	uv run modelkit new $(name) $(if $(title),--title "$(title)")

clean:
	rm -rf site/public/data site/dist site/.astro
