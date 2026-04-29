# Self-Hosted GIS Web UIs — Synthesis

The goal: replace QGIS Desktop with a Docker-served web UI for visualizing GeoJSON setback outputs (`envelopes.geojson`, `setback_strips.geojson`) from `sopo_setbacks.py`. Target user: someone who finds QGIS hard to use.

## Findings by Theme

### The QGIS Dependency Trap

Several "web UI" options actually require QGIS Desktop as a preparation step:

- **Lizmap** (source: `lizmap-docker-compose`): Runs QGIS Server behind a PHP web client. You must still use QGIS Desktop to create `.qgs` project files, configure symbology, and run the Lizmap plugin to generate `.qgs.cfg` configuration files. The Docker stack then serves those pre-authored projects. **Net QGIS dependency: still present.** You trade QGIS-for-viewing for QGIS-for-authoring.

This is fine if one person (GIS-savvy) authors the project once and many people (non-savvy) browse it. But if the goal is "no QGIS at all," Lizmap does not achieve it.

### True QGIS-independent Options

These options can ingest the GeoJSON outputs via a web UI (or command line) and serve a web map with zero QGIS involvement:

1. **GeoServer via Kartoza Docker** (source: `kartoza-geoserver-docker`): A production GeoServer Docker image with PostGIS. GeoServer has a sophisticated web admin panel for uploading data, publishing layers, styling (SLD/CSS), and previewing maps. The built-in Layer Preview gives an instant OpenLayers-based web map for each layer. **Pro:** powerful, standards-compliant, well-maintained Docker image (v2.28.3, April 2026). **Con:** Java-based (heavier), admin UI is technical (not user-friendly map browser).

2. **pg_tileserv + pg_featureserv** (source: `pg-tileserv-pg-featureserv`): Two lightweight Go servers. pg_featureserv provides a built-in HTML web UI with interactive maps for browsing PostGIS tables (at `/collections/{name}/items.html`). Much lighter than GeoServer — 3 containers total (PostGIS + pg_tileserv + pg_featureserv). **Pro:** extremely lightweight, built-in map viewer with zero frontend code. **Con:** no built-in styling (sld/css), read-only, single-purpose.

3. **GeoNode** (source: `geonode-platform`): Full spatial data infrastructure platform. Upload GeoJSON via web UI, publish layers, style them, create map compositions — all in a browser. **Pro:** most user-friendly, closest to "ArcGIS Online but self-hosted." **Con:** heavy stack (~8 containers), complex setup, overkill for single-user map viewing.

### The Middle Ground: Custom Frontend + Tile Server

The most common production pattern seen across sources:

```
PostGIS (with ogr2ogr-loaded GeoJSON) → pg_tileserv (vector tiles) → MapLibre GL JS (GPU-accelerated browser map)
```

All components Dockerized. The frontend is a static HTML page served by Nginx, pointing at the tile server URL. This gives a polished, self-hosted, GPU-accelerated web map with zero desktop GIS.

Prebuilt Docker patterns exist:
- `docker-nginx-leaflet`: Nginx + Leaflet container for previewing tile servers
- `tileserver-gl` (MapTiler): Open-source map server with built-in MapLibre viewer

Data ingestion stays command-line but is a one-liner:
```bash
ogr2ogr -f PostgreSQL PG:"dbname=gis" envelopes.geojson
```

### Community Consensus

The r/selfhosted thread (`selfhosted-reddit-thread`) confirmed:
- GIS self-hosting has a learning curve but Docker helps enormously
- Lizmap is the most common recommendation for "web QGIS"
- Multiple components are inevitable (at minimum: database + tile server + frontend)
- Many people are surprised by the complexity

## Convergence

All sources agree on the architecture:
1. Store spatial data in PostGIS (or GeoPackage/MBTiles)
2. Serve it via a tile/feature server (GeoServer, pg_tileserv, TileServer GL)
3. Display it with a browser map library (MapLibre GL JS or Leaflet)

## Gaps

- No source evaluated **kepler.gl** or **Felt** (mentioned in the README as alternatives) — these are cloud-hosted, not self-hosted Docker options
- QGIS Server (`qgis/qgis-server` Docker image) without Lizmap was not explored — could serve WMS directly from the `.qgs` project file already in this repo (`sopo_gis.qgs`)
- GeoPackage (`*.gpkg`) as a zero-config alternative to PostGIS was not deeply evaluated. `ogr2ogr` can convert GeoJSON to GeoPackage, and GeoServer can serve GeoPackage directly without PostGIS.

## Recommendation for sopo-gis-setbacks

For the specific use case of "view two GeoJSON outputs on a web map":

1. **Quickest path (minutes):** `pg_featureserv` + `ogr2ogr` — 3 Docker containers, instant web map UI, zero frontend code. Load GeoJSON into PostGIS, browse at `http://localhost:9000/collections/setback_strips/items.html`.

2. **More configurable:** GeoServer via Kartoza Docker — load data via admin UI or REST API, Layer Preview for instant viewing, more styling options.

3. **Full platform (overkill):** GeoNode — if you want user accounts, data catalogs, map composition tools, all in-browser.

4. **DIY polished viewer:** pg_tileserv + MapLibre GL JS frontend in Nginx — gives full control over styling, popups, layer toggles.

The existing `sopo_gis.qgs` project file could also be served directly via `qgis/qgis-server` Docker image as a WMS, but that still requires QGIS to maintain the project file.
