# South Portland GIS Data Sources — Synthesis

This trove captures the primary portals, data layers, and regulatory references relevant to building a GIS-based zoning setback tool for the City of South Portland, Maine. No bulk datasets were downloaded; the focus is on portal metadata, access patterns, and cross-references between source types.

---

## Key finding: No pre-computed "setback" GIS layer exists

None of the portals examined (ArcGIS Hub, AxisGIS, Maine GeoLibrary, or third-party aggregators like Zoneomics) publish a ready-made **setback polygon layer**. Setbacks are computed from the intersection of:

1. **Parcel geometry** (provided on the ArcGIS Hub)
2. **Zoning district rules** (defined in Chapter 27 of the City Code)
3. **Street centerlines** (to classify front/side/rear edges)
4. **Shoreland overlay** (where applicable, superseding base setbacks)

This confirms the architectural premise of `sopo_setbacks.py`: the setback layer must be *derived* from parcel geometry + a rules table, not downloaded as a pre-built resource.

---

## Points of agreement across sources

### GIS Hub is the canonical data source

- The **ArcGIS Hub** (`city-of-south-portland-southportland.hub.arcgis.com`) is listed as the official open-data portal in every source examined (project RESOURCES.md, the SoPo 2040 resources page, and the City's own site map).
- It exposes the "Parcels for download" dataset as a downloadable feature service (GeoJSON, Shapefile, CSV, KML) — see `sopo-hub-parcels`.
- Zoning attributes are *joined into* the parcel table (derived from AxisGIS), making it possible to assign a setback rule per parcel without a spatial overlay.

### AxisGIS is the viewer, not the download portal

- AxisGIS (`axisgis.com/South_PortlandME/`) is consistently described as a *hosted viewer* for tax maps, not a bulk data distribution mechanism.
- It provides a richer layer stack than the Hub download page (aerial imagery, topography, city infrastructure, FEMA flood zones, shoreland zoning overlay).
- Its primary role in the setback workflow is **visual QA** — compare generated `setback_strips.geojson` against the aerial + parcel layers.

### Street centerlines are a separate, available layer

- Street centerlines are listed on the ArcGIS Hub (searchable under "Streets") and are available from the Maine GeoLibrary.
- They are a required input for the directional setback model (front/side/rear classification). Without them, `sopo_setbacks.py` falls back to a longest-edge heuristic.

---

## Points of tension / disagreement

### REST endpoint access

- The Hub item page lists a FeatureServer REST URL, but direct JSON queries to `services6.arcgis.com` returned `Invalid URL` when tested.
- **Discrepancy:** The Hub UI expects users to click "Download" or query via the Hub API, while programmatic access via the raw REST endpoint may require different authentication or URL patterns.
- **Resolution:** Use the Hub export button for ad-hoc downloads; for programmatic fetching, use the Hub API or the `query?where=1%3D1&f=geojson` pattern documented in ArcGIS Online docs.

### Legacy vs. current data portals

- The **Maine GeoLibrary** has a new Hub-based portal (`mainegeolibrary-maine.hub.arcgis.com`) that supersedes the old MEGIS catalog.
- However, some state-level layers (e.g., statewide parcel index) may still be easier to find via the legacy catalog.
- **Recommendation:** Default to the new Hub, but keep the legacy URL bookmarked for layers that have not yet migrated.

### Zoning ordinance PDF fragmentation

- Chapter 27 is available as a single PDF from the city's Document Center, but search-engine results also surface *multiple partial PDFs* (e.g., ADU amendments, historic preservation ordinance, A&G zoning regulations from BoardDocs).
- **Risk:** Some partial PDFs may be out of date. The **single canonical PDF** (`CH-27--Zoning-with-New-TOC-format`) should be treated as the ground truth.

---

## Gaps and future sources to investigate

### Shoreland Zoning Overlay polygon

- The shoreland zone is referenced in AxisGIS and in Chapter 27 (Resource Protection Overlay), but a **downloadable polygon** of the shoreland zone boundary has not yet been located on the Hub.
- **Needed for v1:** A separate shoreland setback model that supersedes base-district setbacks within 75–100 ft of the high-water mark.

### Historic Preservation and contract zones

- The city has many **G-2 through G-6 contract zones**, each with property-specific dimensional standards.
- These are not captured in the base `districts.yaml` and would require parcel-specific entries.
- **Needed for v2:** A mechanism to handle contract-zone setbacks (likely via a per-parcel override table).

### Street centerline data completeness

- While the Hub lists a "Streets" layer, it is unclear whether private easements, unimproved roads, or paper streets are included.
- **Needed for accuracy:** A completeness check against the Vision Government Solutions assessor database (which tags each parcel with its fronting street).

### Building footprint / height data

- Height-conditional setbacks ("50% of building height" when exceeding 30 ft) cannot be modeled because there is **no building height attribute** in the parcel data.
- **Potential source:** LiDAR-derived building footprints from the Maine GeoLibrary elevation data, or parcel-specific assessor records.

---

## Regulatory cross-reference

| District | Chapter 27 Section | Status in `districts.yaml` |
|----------|-------------------|---------------------------|
| AA | Sec. 27-524 | Partially transcribed — needs verification against current PDF |
| A  | Sec. 27-534 | Partially transcribed — needs verification |
| G  | Sec. 27-554 | Partially transcribed — needs verification |
| C  | Sec. 27-780 | Partially transcribed — needs verification |
| VC | Sec. 27-7xx / 27-8xx | Needs transcription |
| VE | Sec. 27-7xx / 27-8xx | Needs transcription |
| RF | Sec. 27-5xx | Needs transcription |
| LB | Sec. 27-7xx | Needs transcription |
| IL | Sec. 27-902 | Needs transcription |
| IH | — | Needs transcription |

---

## Recommended workflow for contributors

1. **Get parcels:** Download from the ArcGIS Hub (`Parcels for download`) as GeoJSON.
2. **Get streets:** Download from the Hub or Maine GeoLibrary as GeoJSON.
3. **Transcribe a district:** Open Chapter 27 PDF, find the district's "Space and bulk regulations" section, note the setback values.
4. **Add to `districts.yaml`:** Add the entry, set `verified: <today>`.
5. **Run the tool:** `python sopo_setbacks.py --parcels parcels.geojson --rules districts.yaml --streets streets.geojson ...`
6. **Visual QA:** Load output GeoJSONs in QGIS, compare against AxisGIS aerial + parcel layers.
7. **Iterate:** Fix any misclassified edges or missing districts.

---

## Source cross-links

- `sopo-hub-parcels` — canonical parcel data source
- `sopo-axisgis-viewer` — visual QA and shoreland overlay reference
- `sopo-zoning-ordinance` — canonical setback rules
- `megeolibrary-legacy` — state-level context / historical reference
- `sopo-resources-main` — project-maintained reference list (comprehensive but unverified URLs should be spot-checked)
