---
source-id: "kartoza-geoserver-docker"
title: "Kartoza docker-geoserver — Production GeoServer Docker Image"
type: web
url: "https://github.com/kartoza/docker-geoserver"
fetched: 2026-04-29T12:00:00Z
hash: "82e55ee67ed961788925303a181c1d89a1abacbae1b56f4275c3d0969fb5ec41"  # pragma: allowlist secret
---

# Kartoza docker-geoserver

A production-ready Docker image for GeoServer, an open source server for sharing geospatial data. Kartoza's image is a popular packaging (706 stars, 434 forks, 38 releases — latest: v2.28.3, April 2026).

## Key Features

- Runs GeoServer in Tomcat behind NGINX
- Configurable via environment variables
- PostGIS database backend (kartoza/postgis)
- Extensions support (stable and community plugins)
- Clustering support
- CORS configuration
- Geoserver monitoring
- Production-oriented defaults

## Quick Start

### Docker Compose:
```
cd compose
docker compose up -d
```
Visit `http://localhost:8600/geoserver`. Admin credentials set in `.env`.

### Docker CLI:
```
docker run -d -p 8600:8080 --name geoserver \
  -e GEOSERVER_ADMIN_PASSWORD=myawesomegeoserver \
  -e GEOSERVER_ADMIN_USER=admin \
  kartoza/geoserver:2.28.3
```

## GeoServer Web UI

GeoServer includes a built-in admin web interface at `/geoserver/web/`:

- **Workspaces**: Organize data by project namespace
- **Stores**: Define data sources (shapefiles, PostGIS, GeoPackage, GeoTIFF, WMS cascading)
- **Layers**: Publish and configure styling (SLD/CSS)
- **Layer Preview**: Built-in OpenLayers viewer for each published layer
- **Layer Groups**: Combine multiple layers into a single map request
- **Security**: Role-based access, service-level restrictions

## OGC Services

Publishes data via open standards:
- **WMS**: Web Map Service — rendered map images
- **WFS**: Web Feature Service — vector data (GeoJSON, GML, Shapefile)
- **WMTS**: Web Map Tile Service — cached tiles
- **WCS**: Web Coverage Service — raster data

## QGIS-independent Workflow

1. Start GeoServer + PostGIS via Docker
2. Load GeoJSON/Shapefile data via GeoServer admin UI (or REST API)
3. Publish layers, set styles
4. Access Layer Preview (built-in OpenLayers viewer) at GeoServer web UI
5. Or embed layers in a custom Leaflet/OpenLayers/MapLibre HTML page

## Fit for sopo-gis-setbacks

- **Good fit**: GeoServer + PostGIS via Docker is a standard stack for serving spatial data via a web UI.
- GeoServer's admin panel is a web UI, not a desktop GIS — but it's a technical admin panel, not a user-friendly map browser.
- Layer Preview gives an instant web map view of any published layer.
- For a polished viewer, you'd still want to add a Leaflet/MapLibre HTML frontend on top.
