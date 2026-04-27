# sopo-setbacks

Build a zoning-setback overlay layer for South Portland, ME from parcel
geometry + Chapter 27 dimensional rules.

## What this produces

Two GeoJSON `FeatureCollection`s (EPSG:4326) suitable for loading into QGIS,
ArcGIS Pro, Felt, kepler.gl, or any GIS client:

- **`envelopes.geojson`** — the *buildable envelope* for each parcel (the
  polygon you may build inside, after setbacks).
- **`setback_strips.geojson`** — the *no-build setback rings* (parcel minus
  envelope). This is the typical "overlay" view — colored stripes around lot
  edges showing where construction is restricted.

Each feature carries the source district, the front/side/rear setbacks
applied, and the citation (e.g. `Sec. 27-554`) so any reviewer can audit a
result back to the ordinance.

## Why not just use AxisGIS?

AxisGIS (CAI Tech) is a hosted viewer — it doesn't accept user-uploaded
overlays. The City's [ArcGIS Hub](https://city-of-south-portland-southportland.hub.arcgis.com/)
publishes parcels with zoning attributes as a downloadable feature service,
which is what you point this tool at.

## Quick start

```bash
pip install shapely pyproj pyyaml

# 1. Get parcels from the City's ArcGIS Hub — the "Parcels for download"
#    dataset has zoning attributes joined in. Export as GeoJSON (or use
#    the FeatureServer query endpoint).
#    Confirm the zoning field name; common candidates: zoning, ZONING, zone.

# 2. (Optional but strongly recommended) Get street centerlines as GeoJSON.
#    Without them, the tool falls back to a longest-edge heuristic that's
#    fine for axis-aligned suburban lots but unreliable for irregular parcels.

# 3. Run:
python sopo_setbacks.py \
    --parcels parcels.geojson \
    --rules districts.yaml \
    --streets streets.geojson \
    --zoning-field zoning \
    --parcel-id-field MAP_LOT \
    --out-envelopes envelopes.geojson \
    --out-strips setback_strips.geojson
```

## How it works

1. Project parcels (and streets) from WGS84 to UTM Zone 19N (NAD83) so all
   distances are in meters.
2. For each parcel, classify each exterior edge as `front`, `side`, or `rear`:
   - `front`: edges whose midpoint is within ~30 ft of any street centerline.
     Corner lots get multiple front edges (which matches the ordinance's
     Primary/Secondary Front Yard rules approximately).
   - `rear`: of the remaining edges, the one whose midpoint has the greatest
     perpendicular distance from the front edge's line of support. This is
     correct on rectangles where naïve midpoint-distance picks adjacent
     corners.
   - `side`: everything else.
3. For each edge, buffer inward by the corresponding setback (front/side/rear)
   from the rules table.
4. Buildable envelope = parcel minus the union of setback strips.
5. Reproject back to WGS84 and serialize as GeoJSON.

## Known limitations (read these before trusting an output)

This is a v0. It produces a useful approximation, not a permit-grade legal
determination. Specifically:

- **Height-conditional setbacks are not modeled.** Several SoPo districts
  require side/rear yards of "50% of building height" when the building
  exceeds 30 ft — there's no building height in parcel data, so we use the
  base setback only. For taller proposals you must adjust manually.
- **Shoreland Overlay is not applied.** The Resource Protection / Shoreland
  Overlay imposes much stricter setbacks (typically 75 ft or 100 ft from
  the high-water mark) that supersede the base district. This needs the
  shoreland zone polygon as a separate input. Track this as a v1 feature.
- **Conditional "abutting residential" rules are not modeled.** Several
  commercial districts (C, VC, VE) have 0-ft side/rear setbacks unless they
  abut a residential district, in which case they jump to 15 ft. Modeling
  this requires a parcel-to-parcel adjacency check against neighbor zoning.
- **Secondary Front Yard rules are approximated.** On corner lots, SoPo
  treats one street as the Primary Front Yard (full setback) and the other
  as a Secondary Front Yard (median of nearby setbacks or the side yard,
  whichever is greater). We treat all street-facing edges as full front,
  which is conservative.
- **The districts table is incomplete.** `districts.yaml` ships with a seed
  for a handful of districts (G, C, VC, VE) and TODO markers for the rest.
  Some seed values have `verified: null` and need cross-check against the
  current ordinance before relying on them.
- **Contract zones are unsupported.** SoPo has many G-2 through G-6 contract
  zones, each with property-specific dimensional standards in the rezoning
  ordinance. These would need parcel-specific entries.

## Extending the districts table

Open `districts.yaml`. Each district is keyed by its code as it appears in
the parcel data's zoning field. Schema:

```yaml
districts:
  AA:
    front: 30          # feet
    side: 15
    rear: 25
    accessory_side: 6  # optional
    accessory_rear: 6
    notes: |
      Free-text notes — use this for anything you can't capture
      structurally (height-driven adjustments, conditional rules).
    source: "Sec. 27-524"
    verified: 2026-04-27
```

Workflow for transcribing a new district:

1. Find the district's `Space and bulk regulations` section in Chapter 27
   (typically `27-5xx` for residential, `27-7xx` and `27-8xx` for commercial
   and village districts).
2. Note the `Minimum front yards`, `Minimum side and rear yards`, and any
   conditional rules (height, abutting use, shoreland).
3. Add an entry. Set `verified` to today's date.
4. Run the tests: `python test_sopo_setbacks.py`.

## Using the output

In QGIS:
- Drag both `.geojson` files onto the canvas.
- Style `setback_strips` with a transparent red hatch — that's the overlay
  layer you wanted.
- Style `envelopes` with a 30%-opacity green fill if you want to see the
  buildable area highlighted.

If you want to push this back into the City's ArcGIS Hub as a community
layer, the GeoJSONs can be uploaded directly as a hosted feature service.

## Architectural notes

The code is a single module on purpose — small enough to audit in one sitting,
no plugin/loader complexity, and the YAML rules table is the only thing that
needs to change as the ordinance evolves. If/when this grows past one file,
the natural seams are: `rules.py` (table), `geometry.py` (envelope math),
`overlay.py` (orchestrator), `cli.py`, plus a `data/` directory with the YAML
and a few canonical test fixtures.

The tests use synthetic parcels rather than real ones so they run offline and
don't depend on the City's ArcGIS Hub being up.
