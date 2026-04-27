# Planned Enhancements

**Project:** sopo-setbacks
**Roadmap as of:** 2026-04-27 (post v0)
**Author:** Cristos + Claude (Opus 4.7), single-session build

This file enumerates work that would extend `sopo-setbacks` past v0.
Items are ordered by priority. "Effort" is rough; "depends on" calls out
external data or upstream work needed before this can ship.

A core principle: keep the YAML rules table as the single
ordinance-knowledge surface. New modeling capabilities should extend the
schema, not introduce parallel sources of truth. The whole tool is small
enough to audit in one sitting and that's worth preserving.

---

## §1 — Shoreland Overlay support [P0]

The single biggest correctness gap in v0. The Shoreland Overlay
typically imposes 75 ft (Limited Residential / Stream Protection) or
100 ft (Resource Protection) setbacks from the normal high-water mark,
and supersedes the underlying base district.

**Approach:**
- Add a `--shoreland` argument accepting a GeoJSON of overlay subdistricts
  (Resource Protection, Limited Residential, Stream Protection, etc.),
  each polygon tagged with its subdistrict code.
- Add a `shoreland_overlay:` section to `districts.yaml` mapping each
  subdistrict code to its setback distance from the water line.
- Need a separate input for the high-water mark itself (line geometry).
- For each parcel intersecting an overlay subdistrict, compute a
  `water_setback` strip = buffer(high_water_mark, distance) clipped to
  the parcel. Take the **union** with the base-district setback strips
  (overlay is more restrictive, so union → take the worse one).

**Data sources:**
- Maine DEP publishes shoreland zone subdistrict mapping; the City
  carries a derivative on AxisGIS as the "shoreland zoning overlay"
  layer. Both are likely available via the City's ArcGIS Hub or via the
  Maine GeoLibrary.
- High-water mark: typically derived from MHW lines in NOAA data or
  manually digitized for inland water bodies.

**Effort:** ~1 day. Mostly plumbing — the geometry op (buffer water line,
clip to parcel, union with base setbacks) is straightforward. The data
acquisition (finding the right overlay polygon source) is the bigger
unknown.

**Depends on:** none structural. Can ship without §2 or §3.

---

## §2 — Conditional "abutting residential" rules [P1]

Districts C, VC, and VE have side/rear setbacks of 0 ft by default but
15 ft (or more) when abutting a residential district or property in
residential use.

**Approach:**
- Extend the YAML schema to allow per-direction conditional values:
  ```yaml
  C:
    front: 15
    side:
      default: 0
      when_abutting:
        - districts: [A, AA, G, G-2, G-3, G-4, G-5, G-6, VR]
          value: 15
    rear:
      default: 0
      when_abutting:
        - districts: [A, AA, G, G-2, G-3, G-4, G-5, G-6, VR]
          value: 15
  ```
- In the geometry layer: for each edge classified as side/rear,
  compute the parcel(s) on the opposite side of that edge (small
  outward buffer, intersect with parcels-FC). If any neighbor's
  district matches a `when_abutting.districts` entry, use the
  conditional value; else use `default`.
- Caches help — adjacency is parcel-to-parcel and you'll often hit the
  same neighbor pair many times in a batch.

**Effort:** ~1.5 days. The schema and geometry are clean; the testing
matrix is the bigger cost (need synthetic adjacency cases).

**Depends on:** parcels FC including district attribute on every parcel
(not just the ones being processed). True today via the ArcGIS Hub
"Parcels for download" dataset.

---

## §3 — Complete the districts table [P1, ongoing]

Transcribe the full Chapter 27 dimensional standards into
`districts.yaml`. v0 has G, C, VC, VE only.

**Priority order** (by parcel count likely affected, descending):
1. Residential A (`Sec. 27-534`) — the most common SoPo zoning
2. Residential AA (`Sec. 27-524`)
3. Local Business / LB (`Sec. 27-704`)
4. Suburban Commercial / CS (`Sec. 27-739`)
5. Spring Point / SP (`Sec. 27-732`)
6. Village Residential / VR
7. Industrial districts (I, IH, etc.)
8. Mill Creek Core / MCC and other special districts

For each: read the dimensional standards section, fill in
`front`/`side`/`rear`/`accessory_*`, capture conditional rules in
`notes`, cite the section in `source`, and stamp `verified` with the
date.

**Also re-verify the v0 seed:** the G entry's `side` (8 ft) and `rear`
(25 ft) values are unverified placeholders — see KNOWN_ISSUES B.2.

**Effort:** ~2-3 hours per district to do carefully (read the section,
note conditionals, transcribe, verify). About 12-15 districts to do →
maybe 3-5 working sessions total. Ideal candidate to delegate to a
Claude Code session against the official Chapter 27 PDF, with each
district transcribed into a separate commit for audit.

**Depends on:** access to the current Chapter 27. Cristos has the
full PDF; the ordinance is also on the City's website and in BoardDocs.

---

## §4 — Secondary Front Yard precise modeling [P2]

Corner lots: the ordinance treats one street as Primary Front (full
setback) and the other as Secondary Front, where Secondary = greater
of (a) the median front-yard setback of properties within 300 ft along
the secondary street, when ≥3 measurable properties exist, or (b) the
side-yard setback of the applicable district.

**Approach:**
- Designate the Primary Front as the longer street-facing edge (or
  per City convention if known).
- For the Secondary Front, walk a 300-ft buffer along the relevant
  street, find existing buildings on those parcels (tax-parcel
  building footprints if available, or assessor data with building
  setback measurements), compute median, fall back to side setback.

**Caveat:** rule (a) needs building footprint data, which the City
publishes but is less reliable than parcel boundaries. Rule (b) is
trivial.

**Effort:** ~1 day for rule (b) only as a v1; rule (a) is a v2 feature.

**Depends on:** §3 (need side-yard values for all districts).

---

## §5 — Contract zone (G-2..G-6) support [P2]

Each G-series contract zone has property-specific dimensional standards
in its rezoning ordinance. Schema needs to support per-parcel rules.

**Approach:**
- Add a `contract_zones:` section to YAML keyed by parcel ID (Map/Lot):
  ```yaml
  contract_zones:
    "62/9":          # G-6, see Sec. 27-1081
      district: G-6
      front: 25
      side: 10
      rear: 25
      source: "Sec. 27-1081 (Conditional Residential Use District G-6)"
      verified: 2026-XX-XX
  ```
- In the lookup: parcel ID match wins over district match.

**Effort:** ~30 min schema + lookup change, plus the ordinance-reading
work to transcribe each contract zone (variable, depends on count).

**Depends on:** parcel data including the Map/Lot ID in a known field.

---

## §6 — Direct ArcGIS REST integration [P2, nice-to-have]

Right now you have to download GeoJSON from the City's ArcGIS Hub
manually before running. A `--from-arcgis-rest <feature_server_url>`
mode would query the FeatureServer directly, paginate, and feed the
geometry pipeline.

**Approach:**
- Use `requests` (or stdlib `urllib`) to hit the `/query` endpoint with
  `f=geojson&where=1=1&outFields=*&returnGeometry=true&resultRecordCount=2000`,
  paginate via `resultOffset`.
- Cache responses to disk so reruns don't re-fetch.

**Effort:** ~3 hours. Pagination logic + a couple of edge cases (large
result sets, transient 503s).

**Depends on:** the City's hub URL stability. The "Parcels for download"
dataset is the canonical source.

---

## §7 — GeoPackage output [P3]

GeoJSON is universal but verbose, and QGIS workflows benefit from
having layers grouped in a single `.gpkg` file with proper
attribute-table indexing.

**Approach:** add `--out-gpkg <path>` that writes both layers (envelopes,
strips) into one GeoPackage. Use `fiona` or `pyogrio` for the writer.
Keep the GeoJSON outputs as default for portability.

**Effort:** ~2 hours.

**Depends on:** none.

---

## §8 — Visualization / QC tool [P3]

A small companion script that takes the output GeoJSONs and emits an
HTML page with each parcel's envelope rendered for spot-check. Useful
when iterating on the rules table or after fixing an edge-classifier
bug.

**Approach:** Folium or Leaflet. Or hand-rolled SVG per-parcel for
print-ready review packets.

**Effort:** ~3 hours.

**Depends on:** none.

---

## Out of scope (deliberately not on this list)

- **Zoning ordinance text parsing.** The temptation to write a parser
  that reads Chapter 27 and auto-populates the YAML is real. Don't.
  The ordinance is unstructured prose with edge-case footnotes; the
  YAML is a much better human-curated digest. Time spent transcribing
  is time spent **understanding** the rules — that work has its own
  value beyond the resulting data.
- **Variance / appeals modeling.** Whether a setback can be varied is a
  human judgment. The tool should not pretend otherwise.
- **AxisGIS plugin / direct upload.** AxisGIS doesn't accept user
  layers. Pursuing this is fighting the platform.
- **3D / building-envelope-with-height.** Too ambitious for the
  precision available in the data.

---

## Provenance

This roadmap was sketched in the same chat session on 2026-04-27 that
produced v0 (see `KNOWN_ISSUES.md` Provenance section). The triggering
question was "I can't find the setbacks layer on AxisGIS" — the answer
turned out to be that no such layer exists because setbacks are a *rule
applied to geometry*, not pre-drawn geometry. v0 builds the geometry
from the rules and the parcel data; this roadmap is what it would take
to make that geometry trustworthy enough to use without a human in the
loop on every parcel.

Suggested cadence: tackle §1 (Shoreland) as the next session — it's the
biggest correctness win — then alternate between §3 (district
transcription, low-risk and parallelizable) and §2 (abutting-residential,
medium effort, finishes the C/VC/VE story). §4 onward are quality-of-life
work that can wait until a real use case demands them.
