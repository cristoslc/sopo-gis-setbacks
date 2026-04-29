---
source-id: "lizmap-docker-compose"
title: "Lizmap Stack with Docker Compose"
type: web
url: "https://github.com/3liz/lizmap-docker-compose"
fetched: 2026-04-29T12:00:00Z
hash: "b31a0bb8c306ae1398af743f58f5934b0b3fe6dea1d68877a35376f3cbc79fed"  # pragma: allowlist secret
---

# Lizmap Stack with Docker Compose

Run a complete Lizmap stack with test data using Docker Compose, providing a web-based GIS interface that reads QGIS project files.

## Components

- Lizmap Web Client
- QGIS Server with Py-QGIS-Server
- PostgreSQL with PostGIS
- Redis

## Quick Start

**Linux:**
```
./configure.sh configure
docker compose pull
docker compose up -d
```

**Windows:**
```
configure.bat
docker compose --env-file .env.windows up
```

**Specific version:**
```
LIZMAP_VERSION_TAG=3.9 ./configure.sh configure
```

## Accessing

Open browser at `http://localhost:8090`. Default login is `admin` / `admin`, password change required at first login.

## Adding Projects

1. Create a directory in `lizmap/instances`
2. Visit `http://localhost:8090/admin.php/admin/maps/`
3. In the Lizmap admin panel, add the directory
4. Add one or more QGIS projects with the Lizmap CFG file in the directory

## Notes

- This is a sample configuration for testing. For production, adjustments are needed.
- Requires Docker Engine and Docker Compose plugin.
- To expose to another system, prefix docker command with `LIZMAP_PORT=EXTERNAL_IP:80`.
- The Lizmap service starts two toy projects that must be configured in the Lizmap interface.
- QGIS project files (`.qgs` / `.qgz`) must be prepared in QGIS Desktop with the Lizmap plugin before serving.

## QGIS Dependency

Lizmap **requires QGIS Desktop** to prepare the project files. It is not a standalone web UI — it's a web front-end for QGIS Server. You must still author your `.qgs` project file in QGIS Desktop (adding layers, symbology, labels), save it with the Lizmap plugin to generate the `.qgs.cfg` configuration file, and then copy both into the docker-mapped directory.

## Docker Stack Components

- `3liz/lizmap-web-client`: PHP-FPM container
- `3liz/py-qgis-server`: QGIS Server container
- `postgis/postgis`: PostGIS database
- `redis:alpine`: Redis caching
