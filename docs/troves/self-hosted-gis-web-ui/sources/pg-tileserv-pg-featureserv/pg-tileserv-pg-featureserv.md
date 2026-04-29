---
source-id: "pg-tileserv-pg-featureserv"
title: "pg_tileserv + pg_featureserv — Lightweight PostGIS Tile & Feature Servers"
type: web
url: "https://github.com/CrunchyData/pg_tileserv"
fetched: 2026-04-29T12:00:00Z
hash: "62020d442b9d101b16d061402f2725b087ec845a2ba058380a2742ac881243e9"  # pragma: allowlist secret
---

# pg_tileserv + pg_featureserv

Two companion Go-based servers from CrunchyData that expose PostGIS data as web services — much lighter than GeoServer.

## pg_tileserv (1k stars)

A very thin PostGIS-only tile server. Takes HTTP tile requests, executes SQL, returns MVT (Mapbox Vector Tile) format.

### Docker Quick Start
```
docker run -e DATABASE_URL=postgres://user:pass@host/dbname \  # pragma: allowlist secret
  -p 7800:7800 pramsey/pg_tileserv
```

### Key Features
- Built-in web UI at `http://localhost:7800` — lists all published tables/functions
- Auto-discovers spatial tables and functions
- Table layers: automatically serve any PostGIS table
- Function layers: custom SQL functions `f(z, x, y, params...)` return MVT tiles
- Multi-layer tile requests: combine multiple tables in one request
- CQL filtering, property selection, limit controls
- Configurable resolution, buffer, zoom levels
- Prometheus metrics support

### Configuration
Auto-reads from `./config/pg_tileserv.toml`, `/config/pg_tileserv.toml`, or `/etc/pg_tileserv.toml`. Port defaults to 7800. Environment overrides via `TS_` prefix.

## pg_featureserv (532 stars)

A lightweight RESTful geospatial feature server, implementing the OGC API - Features standard.

### Docker Quick Start
```
docker run -e DATABASE_URL=postgres://user:pass@host/dbname \  # pragma: allowlist secret
  -p 9000:9000 pramsey/pg_featureserv
```

### Key Features
- OGC API - Features compliant (GeoJSON responses)
- Built-in HTML UI with web maps to view spatial data
- Standard query parameters: `limit`, `bbox`, `sortby`, `crs`
- CQL filtering with spatial support
- OpenAPI definition and test UI at `/api.html`
- CORS and GZIP support
- Function layers: custom SQL functions for dynamic queries

### Web UI
```
http://localhost:9000/collections.html        # Browse collections
http://localhost:9000/collections/{name}/items.html  # View features on map
http://localhost:9000/functions.html           # Browse functions
```

## Combined Stack

The typical Docker Compose stack for a lightweight GIS viewer:
- PostgreSQL + PostGIS (`postgis/postgis`)
- pg_tileserv (`pramsey/pg_tileserv`) — vector tiles for fast map rendering
- pg_featureserv (`pramsey/pg_featureserv`) — GeoJSON features for queries/popups
- A simple frontend HTML page with Leaflet or MapLibre GL JS

## Fit for sopo-gis-setbacks

- **Excellent fit**: Much lighter than GeoServer. Docker Compose with 3 containers (PostGIS + pg_tileserv + pg_featureserv).
- pg_featureserv's built-in HTML UI at `/collections/{name}/items.html` gives an instant web map viewer with zero frontend code.
- To use: `shp2pgsql` or `ogr2ogr` to load the GeoJSON setback outputs into PostGIS, then browse immediately.
- For a custom viewer: pg_tileserv serves vector tiles that MapLibre GL JS can render (fast, GPU-accelerated).

## Limitations

- No built-in styling (no SLD/CSS equivalent — styling is client-side in MapLibre/Leaflet)
- No WMS/WFS standards (pg_featureserv uses OGC API - Features, not WFS)
- pg_tileserv requires PostGIS >= 3.0 for MVT tile generation
- pg_featureserv is read-only (no transactional WFS)
- Both are single-purpose servers — they serve data but don't compose maps. The map composition is in the frontend.
