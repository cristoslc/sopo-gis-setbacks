---
source-id: "selfhosted-reddit-thread"
title: "r/selfhosted: Self Hosted Maps Instance"
type: forum
url: "https://www.reddit.com/r/selfhosted/comments/hegowt/self_hosted_maps_instance/"
fetched: 2026-04-29T12:00:00Z
hash: "07bc399ae6c01a12516081e0a3d58348c9c445e91b57e6fdfcaa2ae0ab947d4a"  # pragma: allowlist secret
---

# r/selfhosted: Self Hosted Maps Instance

Discussion thread from r/selfhosted on options for self-hosted web map instances.

## Key Recommendations from the Thread

**Lizmap**: "A managed web UI in front of QGIS Server with docker stacks on github." Recommended as a first look.

**GeoServer + GeoNode**: "Other projects worth looking at are geoserver and geonode."

**TileMill / TileServer**: Multiple mentions of Docker-based tile server setups. "TileMill integrates them nicely and Docker definitely helps with the setup. Maybe it is overkill for your use case."

## Community Observations

- General surprise at the complexity of self-hosting maps: "I didn't realize there was so much to just setting up a map instance."
- Confirmation that Docker solutions exist but GIS has a learning curve: "GIS has a bit of a learning curve but there is a strong open source community so there are a lot of resources out there."
- Multiple components are typical: "All in all, there are at least half a dozen components involved."

## Practical Docker Stacks Mentioned

- Lizmap + QGIS Server + PostgreSQL/PostGIS
- GeoServer + GeoNode (full platform)
- OpenMapTiles stack (tile generation + serving)
- TileServer GL with custom MBTiles
