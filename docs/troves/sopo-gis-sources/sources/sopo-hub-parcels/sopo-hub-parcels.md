---
source-id: sopo-hub-parcels
url: "https://city-of-south-portland-southportland.hub.arcgis.com/datasets/parcels-for-download"
---

# Parcels for download | City of South Portland

**Dataset Title:** Parcels for download
**Publisher:** City of South Portland
**Type:** Feature Service (hosted on ArcGIS Online / Hub)
**Description:** Parcels with AxisGIS derived attributes.
**Access URL:** https://southportland.maps.arcgis.com/home/item.html?id=7fa4a9a2a2d04df7a63f4d7d2e4c0f94

## What this provides

- Tax-parcel polygons for the entire City of South Portland, Maine.
- Attributes derived from AxisGIS (the city's hosted tax-map viewer maintained by CAI Technologies). Key fields typically include `zoning`, `MAP_LOT`, `OWNER`, `ADDRESS`, `ACRES`, `LAND_VAL`, `BUILDING_VAL`, etc.
- The dataset is exposed as a downloadable feature service (GeoJSON, Shapefile, File Geodatabase, CSV, KML) and as a **FeatureServer REST endpoint** for programmatic querying.

## Why it matters for setback analysis

The parcel layer is the *spatial substrate* for any setback overlay. It provides:
1. **Lot geometry** — the polygon boundary to which setbacks are applied.
2. **Zoning attribute** — the district code (e.g. `AA`, `A`, `G`, `C`, `VC`, `VE`) that indexes into the setback rules table (`districts.yaml`).
3. **Map-Block-Lot (MBLU) identifier** — a stable parcel ID (`MAP_LOT`) that can be used to cross-reference Assessor records, AxisGIS tax-map PDFs, and the Vision Government Solutions assessor database.

## What it does *not* contain

- **Setback dimensions** — these live in Chapter 27 of the City Code, not in the parcel attribute table.
- **Street centerlines** — a separate layer (available on the same Hub or from the Maine GeoLibrary) is needed to reliably classify parcel edges as front / side / rear.
- **Shoreland overlay** — the shoreland zone polygon is a separate layer; parcels within the Resource Protection / Shoreland Overlay are subject to 75–100 ft setbacks from the high-water mark, superseding base-district setbacks.

## Known REST endpoint quirks

The ArcGIS REST Services Directory (`services6.arcgis.com`) returns `Invalid URL` for direct JSON queries in some contexts. The recommended access pattern is via the **ArcGIS Hub item page** or the **MapServer/FeatureServer export endpoints** documented on the item page.

## Access patterns

| Format | How to get it |
|--------|---------------|
| GeoJSON | Use the Hub `Download` button or query `.../query?where=1%3D1&f=geojson` |
| Shapefile | Hub download |
| CSV | Hub download (centroids only) |
| REST API | `https://services6.arcgis.com/3Rq2DJt0dT6dKCGn/ArcGIS/rest/services/Parcels_for_download/FeatureServer/0` |

## Related layers on the same Hub

- Zoning Districts
- Council District Boundaries
- Neighborhoods
- Street centerlines (may be under a separate dataset titled "Streets")

## Citation

City of South Portland. *Parcels for download*. ArcGIS Online item. Accessed 2026-04-27.
