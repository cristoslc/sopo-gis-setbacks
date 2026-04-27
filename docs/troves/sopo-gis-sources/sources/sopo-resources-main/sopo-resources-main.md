---
source-id: sopo-resources-main
path: "RESOURCES.md"
---

# Resources — South Portland, ME GIS & Zoning Data

**File:** `RESOURCES.md` (project root)
**Type:** Curated reference list maintained by the `sopo-setbacks` project
**Last updated:** Inferred from project context (2026-04-27)

## Purpose

A curated list of data sources, portals, and references useful for building, verifying, and extending the `sopo-setbacks` overlay.

## City of South Portland — Primary Portals

| Resource | URL | What you'll find |
|----------|-----|----------------|
| **ArcGIS Online (Organization)** | <https://southportland.maps.arcgis.com/home/index.html> | City-managed ArcGIS Online org. Browse users, groups, and content. |
| **ArcGIS Hub — South Portland GIS** | <https://city-of-south-portland-southportland.hub.arcgis.com/> | Public open-data portal. Downloadable feature services for parcels, zoning districts, streets, aerial imagery, council districts, and neighborhoods. |
| **AxisGIS — Property Maps** | <https://www.axisgis.com/South_PortlandME/> | CAI Technologies hosted viewer. Layers: aerial imagery, tax parcels, streets, topography, city infrastructure, FEMA flood zones, shoreland zoning overlay. |
| **AxisGIS — Next-Gen Viewer** | <https://next.axisgis.com/South_PortlandME/> | Updated AxisGIS interface with the same underlying parcel/tax map data. |
| **Vision Government Solutions — Assessor** | <https://gis.vgsi.com/southportlandme/> | Assessor's online database. Search by Map-Block-Lot (MBLU) or address. Links to tax bills and payment. |
| **Tax Maps (PDF download)** | <https://www.southportland.gov/168/Tax-Maps> | Official city tax map PDFs for download. |
| **Land Use Maps & Regulations** | <https://www.southportland.gov/251/Land-Use-Maps-Regulations> | Central landing page for zoning maps, subdivision regulations, and related planning documents. |
| **Planning Department** | <https://www.southportland.org/242/Planning> | Maintains the Zoning Ordinance and Subdivision Ordinance. Links to Code of Ordinances. |
| **City Site Map** | <https://www.southportland.org/sitemap> | Quick index to Assessor's Online Database, GIS Database, building codes, and charter/ordinances. |

## Zoning & Comprehensive Plan Maps

| Resource | URL | Notes |
|----------|-----|-------|
| **Comprehensive Plan & Zoning Maps** | <https://www.arcgis.com/apps/webappviewer/index.html?id=3c82c619da2f4d02ae3960adab2db764> | ArcGIS Web AppViewer. Layers include Key Land Use Policy Areas, Future Land Use Plan (2012 Comprehensive Plan), current council districts, neighborhoods, zoning districts, and tax parcels. |
| **SoPo 2040 — Resources** | <https://southportland2040.com/resources> | South Portland 2040 comprehensive plan website. Aggregates links to AxisGIS property maps and ArcGIS Online comprehensive plan / zoning map layers. |
| **Zoneomics — South Portland Zoning** | <https://www.zoneomics.com/zoning-maps/maine/south-portland> | Third-party zoning data aggregator. Useful for quick cross-checks of district boundaries and land-use allocations (subscription required for full reports). |

## State & Regional GIS Data

| Resource | URL | What you'll find |
|----------|-----|----------------|
| **Maine GeoLibrary (new)** | <https://mainegeolibrary-maine.hub.arcgis.com/> | Upgraded open-data portal for statewide GIS layers: parcels, elevation, hydrography, conservation lands, transportation, etc. |
| **Maine Office of GIS (MEGIS) — Legacy Catalog** | <https://www.maine.gov/megis/catalog/> | Older catalog interface; being superseded by the GeoLibrary Hub above. |
| **Maine Land Use Planning Commission (LUPC)** | <https://www.maine.gov/dacf/lupc/plans_maps_data/digital_maps_data.html> | Digital zoning shapefiles and web map services for unorganized / deorganized areas of Maine. Not directly applicable to South Portland (an organized city), but useful for regional context. |

## Regulatory References

| Document | How to access | Relevance to setbacks tool |
|----------|---------------|---------------------------|
| **City Code — Chapter 27 (Zoning)** | Linked from Planning page (<https://www.southportland.org/242/Planning>) or Code of Ordinances page | The canonical source for setback distances, height limits, and conditional rules. District setback tables are transcribed from sections like `27-524` (AA), `27-534` (A), `27-554` (G), `27-7xx` / `27-8xx` (commercial & village districts). |
| **Shoreland Zoning Overlay** | Referenced in AxisGIS and Chapter 27 | Supersedes base-district setbacks within the shoreland zone (typically 75–100 ft from high-water mark). Requires a separate polygon overlay not yet modeled in this tool. |
| **FEMA Flood Zones** | Available in AxisGIS and ArcGIS Hub | May affect buildable area independent of zoning setbacks. |

## Data Formats & Access Patterns

- **Parcels with zoning attributes** — Published on the ArcGIS Hub as a downloadable feature service. Export as GeoJSON or query the FeatureServer REST endpoint directly.
- **Street centerlines** — Available from the ArcGIS Hub or Maine GeoLibrary. Used by `sopo_setbacks.py` to classify parcel edges as front / side / rear.
- **Zoning district polygons** — Available from the ArcGIS Hub. Useful for visual validation and for future features such as "abutting residential district" conditional rules.
- **Aerial imagery** — Available in both AxisGIS and ArcGIS Online. Useful for ground-truthing irregular parcels and shoreland boundaries.

## Tips for Contributors

1. **Start with the ArcGIS Hub** when downloading fresh parcel data — it is the city's official open-data portal and the zoning attributes are joined in.
2. **Cross-check setback values** against the City Code PDF (Chapter 27) before marking any district as `verified` in `districts.yaml`.
3. **Use AxisGIS for visual QA** — load the generated `setback_strips.geojson` and `envelopes.geojson` in QGIS, then compare against the aerial + parcel layers in AxisGIS.
4. **Report stale links** — Municipal GIS URLs change when platforms are upgraded. If you find a dead link in this file, please open an issue or PR.

## Note about large-scale data downloads

This document does **not** include actual downloaded GIS datasets (e.g. parcel shapefiles, aerial imagery tiles, or full zoning polygon exports). For bulk data, use the ArcGIS Hub export feature or contact the City of South Portland Assessor's Office directly.
