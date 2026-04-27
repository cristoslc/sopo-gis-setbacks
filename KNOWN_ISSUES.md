# Known Issues

**Project:** sopo-setbacks
**Status as of:** 2026-04-27 (v0, initial build)
**Author:** Cristos + Claude (Opus 4.7), single-session build

This file catalogs everything that's wrong, incomplete, or fragile in the
current implementation. Severity reflects how much it could mislead a user
who treats an output as authoritative; "workaround" describes what to do
right now without code changes.

---

## A. Modeling gaps (the ordinance says X, the code does Y)

### A.1 — Shoreland Overlay is not applied
- **Severity:** HIGH for any parcel within ~250 ft of Casco Bay, the Fore
  River, the Stroudwater, Long Creek, Trout Brook, or any mapped wetland.
- **What's wrong:** The Shoreland Overlay imposes setbacks of typically
  75 ft (Limited Residential / Stream Protection) or 100 ft (Resource
  Protection) from the normal high-water mark. These supersede the
  underlying base district. The current code applies only the base
  district's setbacks.
- **Workaround:** For any parcel intersecting the shoreland zone overlay
  (visible in AxisGIS as the "shoreland zoning overlay" layer), do not
  trust this tool's output. Cross-check manually against Article XIII of
  Chapter 27 and the relevant overlay subdistrict.
- **Fix path:** see `PLANNED_ENHANCEMENTS.md` §1.

### A.2 — "Abutting residential" conditional setbacks not modeled
- **Severity:** MEDIUM for commercial/village districts; LOW elsewhere.
- **What's wrong:** Districts C, VC, and VE have 0-ft side/rear setbacks
  by default, but jump to 15 ft when abutting a residential district or
  a property in residential use. The code uses the unconditional value
  (0 ft for side/rear in C, etc.) which is permissive — outputs may show
  buildable area where the ordinance would require a 15-ft strip.
- **Workaround:** For C/VC/VE parcels adjacent to any residential parcel
  (A, AA, G-series, VR), increase side and rear setbacks to 15 ft
  manually before publishing.
- **Fix path:** see `PLANNED_ENHANCEMENTS.md` §2.

### A.3 — Height-conditional setbacks not modeled
- **Severity:** LOW for typical 1-2 story residential; HIGH for any
  4+ story proposal.
- **What's wrong:** Several districts require side/rear yards of "50% of
  building height" when the building exceeds 30 ft. Parcel data has no
  building height, so we apply only the base setback.
- **Workaround:** Treat outputs as valid only for buildings ≤ 30 ft. For
  taller proposals, increase side/rear by `0.5 × proposed_height` (in
  feet) above the base.
- **Fix path:** out of scope for v1 — would require a separate
  proposed-building-height input per parcel.

### A.4 — Secondary Front Yard rules approximated
- **Severity:** LOW–MEDIUM for corner lots only.
- **What's wrong:** The ordinance treats one street as the Primary Front
  Yard (full setback) and the other as a Secondary Front Yard (greater
  of: median front-yard setback of nearby properties along that street,
  OR the side-yard setback). The code treats every street-facing edge as
  full Primary Front Yard. This is **conservative** (envelope is smaller
  than legally allowed), so it won't approve illegal construction, but
  it may flag legal designs as out-of-spec.
- **Workaround:** For corner lots, manually relax the Secondary Front
  Yard to the side-yard setback as a first approximation.
- **Fix path:** see `PLANNED_ENHANCEMENTS.md` §4.

### A.5 — Contract zones (G-2 through G-6) unsupported
- **Severity:** HIGH for any parcel zoned G-2 through G-6.
- **What's wrong:** Each G-series contract zone has property-specific
  dimensional standards baked into its rezoning ordinance — there is no
  single rule that applies. The current YAML schema is district-keyed,
  not parcel-keyed.
- **Workaround:** Set the unknown-district policy to `lenient` (current
  default), which skips these parcels rather than producing wrong
  output. They simply won't appear in the overlay layer.
- **Fix path:** see `PLANNED_ENHANCEMENTS.md` §5.

---

## B. Data completeness (the rules table is partial)

### B.1 — Most districts missing from `districts.yaml`
- **Severity:** Depends on which district your area of interest falls in.
- **What's wrong:** v0 ships with seed entries for G, C, VC, VE only. The
  YAML has TODO markers for A, AA, G-2..G-6, LB, SP, CS, and the
  industrial districts.
- **Workaround:** Add entries as needed using the schema in
  `districts.yaml`. Each entry needs a `source` citation and `verified`
  date for auditability.

### B.2 — Some seed values are unverified placeholders
- **Severity:** MEDIUM — incorrect output without an obvious tell.
- **What's wrong:** The G district entries for `side` (8 ft) and `rear`
  (25 ft) are educated guesses based on typical Maine residential zoning
  patterns and partial search-result excerpts; they have `verified: null`
  in the YAML. The front yard (20 ft) and accessory setbacks (6 ft) are
  cited and verified against `Sec. 27-554`.
- **Workaround:** Cross-check against the current Chapter 27 PDF before
  using G-district outputs. Update `verified` to today's date once
  confirmed.

---

## C. Implementation caveats

### C.1 — `front_proximity_ft` is hardcoded at 30 ft
- **Severity:** LOW.
- **What's wrong:** The threshold for "edge close enough to a street to
  count as front" is a hardcoded 30 ft. Parcels separated from the road
  by a wide right-of-way, ditch, or planted strip may be misclassified
  if the centerline sits more than 30 ft from the nearest lot edge.
- **Workaround:** None at the CLI level — would require code edit. If
  you see no envelope features for a parcel that clearly should have
  one, this is a likely cause.

### C.2 — Longest-edge fallback when no streets provided
- **Severity:** MEDIUM if you skip the `--streets` argument.
- **What's wrong:** Without street centerlines, the code picks the
  *longest* edge as front. This works for typical suburban lots (long
  side faces street) but fails for deep narrow lots where the short
  edge faces the street, and for flag lots, irregular subdivisions, and
  parcels along curving roads.
- **Workaround:** Always provide `--streets`. If you must run without,
  spot-check outputs against AxisGIS aerials.

### C.3 — UTM Zone 19N introduces ~0.1 m scale distortion
- **Severity:** Negligible.
- **What's wrong:** UTM is conformal but not equidistant; at South
  Portland's latitude, scale factor is ~0.99986. A 25-ft setback
  becomes a 7.62 m buffer that's actually applied as ~7.61 m on the
  ground — error of about 4 mm.
- **Workaround:** None needed. Documented for completeness because the
  test tolerance (0.2 m) was set with this in mind.

### C.4 — No handling of multi-polygon parcels
- **Severity:** LOW.
- **What's wrong:** Parcels with `MultiPolygon` geometry (e.g. a parcel
  split by a road or waterbody) are processed per-component, with each
  component getting its own setback envelope. This may produce odd
  output for parcels where the components are legally a single lot.
- **Workaround:** For known-affected parcels, dissolve components
  upstream before running.

### C.5 — Output target is QGIS/ArcGIS, not AxisGIS
- **Severity:** Not a bug — by design — but worth restating.
- **What's wrong:** AxisGIS (CAI Tech) is a hosted viewer and does not
  accept user-uploaded layers. The original question that started this
  project was "I can't find the setbacks layer on AxisGIS" — the
  answer is that there isn't one and AxisGIS won't host one you build.
  The intended consumption path is QGIS, ArcGIS Pro, kepler.gl, Felt,
  or back into the City's ArcGIS Hub if they accept community layers.
- **Workaround:** Use one of the above clients.

---

## D. Build-log: bugs found and fixed during the v0 build

These are recorded so we don't reintroduce them. The tests in
`test_sopo_setbacks.py` were what caught both.

### D.1 — Wrong CRS code (EPSG:2802)
- **Discovered:** during first test run, all envelope bounds were `nan`.
- **Cause:** I selected `EPSG:2802` thinking it was "NAD83 / Maine West
  (US survey feet)". It's actually `NAD83(HARN) / Maine East` in
  *meters*. The buffer-by-feet against a meter-scale projection
  produced numerical garbage at the inward-buffer step (parcel
  collapsed to nothing).
- **Fix:** switched to `EPSG:26919` (UTM Zone 19N, NAD83, meters) and
  added a `FT_TO_M = 0.3048` conversion at every spot where a setback
  distance meets a geometry operation.
- **Lesson:** never trust the CRS code in your head — verify with
  `pyproj.CRS(code).axis_info` before committing.

### D.2 — Rear-edge classifier picked adjacent corners on rectangles
- **Discovered:** by `test_directional_envelope_no_streets_uses_longest_edge_as_front`,
  which expected horizontal insets of `~10 ft` (side) and got one
  `~10 ft` and one `~20 ft` (rear).
- **Cause:** the original heuristic picked the rear edge as "the edge
  whose midpoint is farthest from the front edge's midpoint." For a
  rectangle where front is the right edge, the bottom edge's midpoint
  is √(width² + (height/2)²) away from the right midpoint, which can
  exceed `width` (the distance to the actual opposite/left edge). Result:
  bottom misclassified as rear.
- **Fix:** use perpendicular distance from the front edge's *line of
  support* (infinite line through the front edge), not midpoint-to-
  midpoint distance. New helper: `_perp_distance_to_line()`.
- **Lesson:** for "find the edge most opposite this edge," use perp
  distance to the supporting line, not point-to-point distance.

### D.3 — Edge-endpoint proximity flagged adjacent edges as 'front'
- **Discovered:** by `test_directional_envelope_with_streets`, where
  side edges that touched the street's east-west line at a shared
  corner were misclassified as front.
- **Cause:** the proximity test was `edge.distance(streets) <= 30 ft`.
  For two perpendicular line segments sharing a corner, the
  edge-to-edge distance is 0 regardless of which way the edge runs.
- **Fix:** test the *midpoint* of each edge against the streets, not
  the whole edge. Side edges' midpoints are far from the cross-street;
  only the front edge's midpoint is close.
- **Lesson:** for "which edge faces this line," use a midpoint check,
  not a min-distance check.

---

## Provenance

This file was authored from a single chat session on 2026-04-27 between
Cristos (South Portland resident, Head of Platform Engineering at Bureau
Veritas) and Claude (Opus 4.7), in response to "I can't find the
setbacks layer on AxisGIS" → "can you pull the ordinance and write a
function to build an overlay I can import as a layer?"

Sources consulted during the build:
- South Portland City Code Chapter 27, sections 27-534 (Residential A),
  27-554 (Residential G), 27-78x (Commercial C), 27-811 (Village
  Extension), and the Knightville/Mill Creek zoning amendments. Citations
  in `districts.yaml`.
- City of South Portland ArcGIS Hub
  (`city-of-south-portland-southportland.hub.arcgis.com`), specifically
  the "Parcels for download" dataset.
- South Portland 2040 resources page for the inventory of layers
  available on AxisGIS.
- pyproj CRS metadata to resolve the EPSG:2802 confusion.

The full build, including the two bugs caught above, fits in one
~400-line module + ~280-line test file + a YAML config. Tests pass in
under a second on a laptop.
