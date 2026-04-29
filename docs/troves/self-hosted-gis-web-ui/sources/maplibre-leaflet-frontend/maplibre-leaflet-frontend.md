---
source-id: "maplibre-leaflet-frontend"
title: "MapLibre GL JS and Leaflet — Browser-based Map Frontends"
type: web
url: "https://maplibre.org/"
fetched: 2026-04-29T12:00:00Z
hash: "3065e007e45e36ba70e2fe5809daaa268c1d1055e0370126c772afc4ac90f503"  # pragma: allowlist secret
---

# MapLibre GL JS and Leaflet — Browser-based Map Frontends

Self-hosted GIS web UIs are typically composed of a **backend server** (GeoServer, pg_tileserv) + a **browser frontend library** (MapLibre GL JS or Leaflet).

## MapLibre GL JS

- Community fork of mapbox-gl-js (BSD-3-Clause license)
- GPU-accelerated WebGL rendering of vector tiles
- Slippy map with full pan/zoom/rotate/tilt
- Style specification for defining layer appearance
- Custom layer API for integration (Deck.gl, data overlays)
- Production users include NYT, Volkswagen, many governments
- Can be self-hosted — bundle JS/CSS into any static site or Docker container

### Minimal self-hosting
```html
<script src="maplibre-gl.js"></script>
<link href="maplibre-gl.css" rel="stylesheet" />
<div id="map"></div>
```

Point at any tile server (self-hosted or not):
```js
const map = new maplibregl.Map({
  container: 'map',
  style: { version: 8, sources: { ... }, layers: [ ... ] }
});
```

## Leaflet

- Lightweight library (~28KB JS)
- Simpler API, less GPU-dependent
- Plugins for heatmaps, clustering, routing, drawing tools
- Works with raster tiles (WMS, XYZ) out of the box
- Vector tile support via plugin (`Leaflet.VectorGrid`)
- Easier to get started but less performant for large datasets

## Docker-friendly Frontend Pattern

```
docker-compose.yml:
  postgis:      postgis/postgis:16-3.4
  pg_tileserv:  pramsey/pg_tileserv
  frontend:     nginx:alpine (serving index.html + maplibre-gl.js)
```

The frontend is a static HTML page in an nginx container, pointing at the pg_tileserv tile URL. This gives a complete self-hosted, GPU-accelerated web map with zero desktop GIS dependency.

## Prebuilt Docker Map Viewers

- **docker-nginx-leaflet** (github.com/openfirmware/docker-nginx-leaflet): Nginx + Leaflet in a Docker image for previewing tile servers. Configurable via env vars to point at any compatible tile server.
- **tileserver-gl** (github.com/maptiler/tileserver-gl): Open-source map server that renders vector/raster tiles and serves a built-in web viewer via MapLibre GL JS. Docker: `docker run -v $(pwd):/data -p 8080:8080 maptiler/tileserver-gl`.
