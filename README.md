# Suomen järvet — a live map of Finland's lakes

A single static page that fetches everything live in your browser. No server, no build step, no database, no scheduled job.

**Live:** https://nanwer.github.io/suomen-jarvet/

## What it shows

- **Real lake outlines from OpenStreetMap**, loaded for the current viewport as you zoom in (not a point map).
- **Live measurements**, fetched straight from the source APIs when the page loads:
  - Water level — SYKE gauges, coloured by 14-day trend
  - Surface temperature — Järvi-meriwiki, mostly citizen readings
  - Ice-out — SYKE, spring break-up dates
- **One card per lake.** Click a lake and its temperature, water level and nearest town are merged into a single card, with directions.
- Search via OpenStreetMap Nominatim. Finnish by default, English toggle. Installable as a PWA.

## How it works

`index.html` is the whole app. On load and as you pan, it calls, from the browser:

- **SYKE Hydrologiarajapinta** (OData) — water level, ice-out
- **Järvi-meriwiki** Semantic MediaWiki `ask` API — surface temperature
- **OpenStreetMap Overpass** — lake polygons for the current view
- **OpenStreetMap Nominatim** — search

All of these send `Access-Control-Allow-Origin: *`, so the browser can call them directly. There is no build and no cron, so the readings are genuinely real-time. (An earlier version baked the data server-side into a committed GeoJSON file; that is gone.)

## Data & license

Open data under **CC BY 4.0** — attribute **SYKE / Järvi-meriwiki**. Basemap © OpenStreetMap contributors © CARTO. Lakes, towns and search © OpenStreetMap contributors.

## Run locally

Any static server from the repo root, e.g.:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

`icons.py` regenerates the PWA icons (needs Pillow); everything else is plain HTML/JS with no dependencies to install.
