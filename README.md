# Suomen järvet — a live map of Finland's lakes

An interactive map of Finland's lakes on a real OpenStreetMap basemap, built entirely from open data. Inspired by the Norway river-flow map.

**Live:** https://nanwer.github.io/suomen-jarvet/

## What it shows

- **Every named lake** — all 59,084 lakes in SYKE's register (≥1 ha). Search any by name and fly to it; click for area, max/mean depth, volume, shoreline, watershed and nearest town, plus **Get directions** (Google Maps) and **Open in OpenStreetMap**.
- **Four mix-and-match layers** on live data:
  - **Water level** — ~790 SYKE gauges, coloured by 14-day trend, with a 120-day history chart
  - **Temperature** — ~165 surface-water-temperature sites from Järvi-meriwiki (mostly citizen readings), with a recent sparkline and a citizen/authority badge
  - **Ice-out** — spring ice break-up dates
  - **Named lakes** — the full register (the "no live data, still a lake" layer)
- **Finnish by default**, with an English toggle.

Finland has ~188,000 lakes counting every pond over 5 ares; the 59,084 shown here are the ones large enough (≥1 ha) to be named and catalogued. The smaller ponds appear on the basemap.

## Data & license

All open data under **CC BY 4.0** — please attribute **SYKE / Järvi-meriwiki**:

- **SYKE Hydrologiarajapinta** (OData) — water level, ice-out
- **SYKE Järvirajapinta** (OData) — the lake register
- **Järvi-meriwiki** Semantic MediaWiki `ask` API — citizen surface-water temperatures
- Basemap © OpenStreetMap contributors © CARTO
- Nearest-town points © OpenStreetMap contributors (Overpass)

## How it works

A **static site** — no server or database. [`build.py`](build.py) (zero dependencies, Python stdlib only) fetches the open APIs and writes `dist/index.html` + `dist/lakes.geojson`. A scheduled **GitHub Action** re-runs the build every 6 hours and redeploys to GitHub Pages, so the readings stay fresh.

## Build & preview locally

```bash
python3 build.py
python3 -m http.server -d dist 8000
# open http://localhost:8000
```

## Optional: custom domain

To serve at your own domain (e.g. `jarvet.nophil.org`): add a `CNAME` line to the build that writes your domain into `dist/CNAME`, then point a DNS `CNAME` record at `nanwer.github.io`. Nothing else changes.
