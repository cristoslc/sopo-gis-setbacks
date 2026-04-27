"""
sopo_setbacks — build a setbacks overlay layer for South Portland, ME.

Inputs:
  - parcels: GeoJSON FeatureCollection of parcel polygons with a zoning
    district attribute (default field name: "zoning")
  - rules:   YAML file mapping district code -> setback distances (feet)
  - streets: (optional) GeoJSON of street centerlines, used for directional
    front-line detection. If omitted, falls back to uniform inward buffer.

Outputs (GeoJSON FeatureCollections):
  - buildable_envelope: per parcel, the polygon you may build inside
  - setback_strips:     per parcel, the no-build setback rings (overlay layer)

Coordinate handling:
  Inputs are assumed to be EPSG:4326 (lon/lat). Internally we project to
  EPSG:2802 (NAD83 / Maine West, US survey feet) so buffer distances in
  feet are correct, then reproject back to 4326 on output.

Limitations (read README):
  - Directional logic uses nearest-street-centerline heuristic; corner lots
    and flag lots may need manual review.
  - Height-conditional setbacks ("50% of building height") are not modeled.
  - Shoreland Overlay is not applied — the overlay's stricter setbacks
    supersede the base district and require separate handling.
  - Secondary Front Yard rules for corner lots are approximated by treating
    every street-facing edge as front.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import yaml
from pyproj import Transformer
from shapely.geometry import (
    LineString,
    MultiPolygon,
    Polygon,
    mapping,
    shape,
)
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform, unary_union

log = logging.getLogger("sopo_setbacks")

# UTM zone 19N (NAD83), meters. Covers all of Maine cleanly with sub-meter
# accuracy; we convert setback distances from feet to meters at the geometry
# boundary via FT_TO_M.
WORKING_CRS = "EPSG:26919"
INPUT_CRS = "EPSG:4326"
FT_TO_M = 0.3048


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

@dataclass
class SetbackRules:
    """Setback distances (feet) for a single zoning district."""

    front: float
    side: float
    rear: float
    accessory_side: Optional[float] = None
    accessory_rear: Optional[float] = None
    notes: str = ""
    source: str = ""
    verified: Optional[str] = None

    @property
    def max_setback(self) -> float:
        """Used by the uniform (non-directional) buffer fallback."""
        return max(self.front, self.side, self.rear)


@dataclass
class SetbackTable:
    """Registry of district -> SetbackRules + unknown-district policy."""

    rules: dict[str, SetbackRules]
    unknown_policy: str = "lenient"  # strict | lenient | conservative
    conservative_fallback: Optional[SetbackRules] = None

    @classmethod
    def from_yaml(cls, path: Path) -> "SetbackTable":
        with open(path) as f:
            data = yaml.safe_load(f)
        rules = {
            code: SetbackRules(**vals)
            for code, vals in (data.get("districts") or {}).items()
        }
        unk = data.get("unknown_district") or {}
        fallback = unk.get("conservative_fallback")
        return cls(
            rules=rules,
            unknown_policy=unk.get("policy", "lenient"),
            conservative_fallback=SetbackRules(**fallback) if fallback else None,
        )

    def lookup(self, district: Optional[str]) -> Optional[SetbackRules]:
        if district and district in self.rules:
            return self.rules[district]
        if self.unknown_policy == "strict":
            raise KeyError(f"District {district!r} not in setback table")
        if self.unknown_policy == "conservative" and self.conservative_fallback:
            log.warning("District %r missing — using conservative fallback", district)
            return self.conservative_fallback
        log.warning("District %r missing — skipping parcel", district)
        return None


# ---------------------------------------------------------------------------
# Geometry: projection helpers
# ---------------------------------------------------------------------------

_to_working = Transformer.from_crs(INPUT_CRS, WORKING_CRS, always_xy=True).transform
_to_input = Transformer.from_crs(WORKING_CRS, INPUT_CRS, always_xy=True).transform


def project_to_working(geom: BaseGeometry) -> BaseGeometry:
    return transform(_to_working, geom)


def project_to_input(geom: BaseGeometry) -> BaseGeometry:
    return transform(_to_input, geom)


# ---------------------------------------------------------------------------
# Geometry: setback envelope computation
# ---------------------------------------------------------------------------

def uniform_envelope(parcel: Polygon, rules: SetbackRules) -> BaseGeometry:
    """
    Conservative envelope: inward buffer using the *largest* setback.
    Always smaller than (or equal to) the legal envelope, but never larger.
    Use when no street centerlines are available.
    """
    return parcel.buffer(-rules.max_setback * FT_TO_M)


def _polygon_edges(poly: Polygon) -> list[LineString]:
    """Yield each segment of the exterior ring as a LineString."""
    coords = list(poly.exterior.coords)
    return [LineString([coords[i], coords[i + 1]]) for i in range(len(coords) - 1)]


def _perp_distance_to_line(point, line_seg: LineString) -> float:
    """Perpendicular distance from a point to the infinite line through line_seg.

    Used to pick the 'rear' edge as the one whose midpoint is farthest from the
    front edge's line of support — this works correctly on rectangles, where
    using midpoint-to-midpoint distance picks adjacent corners instead of the
    truly opposite edge.
    """
    (x1, y1), (x2, y2) = line_seg.coords[0], line_seg.coords[-1]
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return point.distance(line_seg)
    return abs((point.x - x1) * dy - (point.y - y1) * dx) / length


def _classify_edges(
    parcel: Polygon,
    streets: Optional[BaseGeometry],
    front_proximity_ft: float = 30.0,
) -> dict[int, str]:
    """
    Label each exterior edge of the parcel as 'front', 'rear', or 'side'.

    Heuristic:
      - front: edges within front_proximity_ft of any street centerline.
        (Captures corner lots — multiple street-facing edges all count.)
      - rear:  edge with greatest distance to any street centerline among the
        non-front edges, AND roughly opposite the front (longest perpendicular
        distance from the parcel centroid through a front edge).
      - side:  everything else.

    If no streets are provided, picks the longest edge as 'front', the edge
    most opposite by centroid as 'rear', remainder 'side'. Brittle but
    deterministic for testing.
    """
    edges = _polygon_edges(parcel)
    classes: dict[int, str] = {}
    proximity_m = front_proximity_ft * FT_TO_M

    if streets is None:
        # Deterministic fallback: longest edge is front
        front_idx = max(range(len(edges)), key=lambda i: edges[i].length)
        classes[front_idx] = "front"
        # Rear = edge whose midpoint is farthest from the front edge's
        # line of support (perpendicular distance). Correct for rectangles.
        front_edge = edges[front_idx]
        rear_idx = max(
            (i for i in range(len(edges)) if i != front_idx),
            key=lambda i: _perp_distance_to_line(
                edges[i].interpolate(0.5, normalized=True), front_edge
            ),
        )
        classes[rear_idx] = "rear"
        for i in range(len(edges)):
            classes.setdefault(i, "side")
        return classes

    # Streets provided. Use edge MIDPOINTS for proximity (not whole-edge
    # distance, which falsely marks side edges as 'front' when their corner
    # touches the cross-street).
    front_idxs: list[int] = []
    for i, e in enumerate(edges):
        mid = e.interpolate(0.5, normalized=True)
        if mid.distance(streets) <= proximity_m:
            front_idxs.append(i)
            classes[i] = "front"

    if not front_idxs:
        # Defensive: parcel not near any street; treat closest edge by midpoint
        front_idxs = [
            min(
                range(len(edges)),
                key=lambda i: edges[i].interpolate(0.5, normalized=True).distance(streets),
            )
        ]
        classes[front_idxs[0]] = "front"

    # Rear: among non-front edges, the one whose midpoint has the greatest
    # perpendicular distance from any front edge's line of support.
    non_front = [i for i in range(len(edges)) if i not in front_idxs]
    if non_front:
        def perp_to_any_front(idx: int) -> float:
            mid = edges[idx].interpolate(0.5, normalized=True)
            return max(_perp_distance_to_line(mid, edges[fi]) for fi in front_idxs)
        rear_idx = max(non_front, key=perp_to_any_front)
        classes[rear_idx] = "rear"

    for i in range(len(edges)):
        classes.setdefault(i, "side")
    return classes


def directional_envelope(
    parcel: Polygon,
    rules: SetbackRules,
    streets: Optional[BaseGeometry] = None,
) -> BaseGeometry:
    """
    Compute buildable envelope by inward-buffering each edge by its assigned
    setback (front/side/rear) and subtracting from the parcel.

    The "subtract one-sided buffers from the parcel" trick:
      For each edge, we buffer it as a flat strip on the *interior* side using
      a generous buffer that we then intersect with the parcel. The union of
      all such strips is the no-build setback area; the parcel minus that is
      the buildable envelope.
    """
    edges = _polygon_edges(parcel)
    classes = _classify_edges(parcel, streets)

    setback_strips = []
    for i, edge in enumerate(edges):
        kind = classes[i]
        dist_ft = getattr(rules, kind)
        if dist_ft <= 0:
            continue
        dist_m = dist_ft * FT_TO_M
        # Buffer the edge by `dist_m` on both sides, then clip to the parcel
        # interior to keep only the inward-facing strip.
        strip = edge.buffer(dist_m, cap_style=2).intersection(parcel)
        if not strip.is_empty:
            setback_strips.append(strip)

    if not setback_strips:
        return parcel

    no_build = unary_union(setback_strips)
    envelope = parcel.difference(no_build)
    return envelope


def setback_strips(
    parcel: Polygon, envelope: BaseGeometry
) -> BaseGeometry:
    """The no-build region = parcel minus envelope. Useful as an overlay layer."""
    return parcel.difference(envelope)


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------

def _as_polygons(g: BaseGeometry) -> Iterable[Polygon]:
    if isinstance(g, Polygon):
        yield g
    elif isinstance(g, MultiPolygon):
        yield from g.geoms


def build_overlay(
    parcels: dict,
    table: SetbackTable,
    streets: Optional[dict] = None,
    zoning_field: str = "zoning",
    parcel_id_field: str = "id",
) -> tuple[dict, dict]:
    """
    Build buildable-envelope and setback-strip GeoJSON FeatureCollections.

    Args:
        parcels: GeoJSON FeatureCollection of parcel polygons (EPSG:4326)
        table: SetbackTable
        streets: optional GeoJSON FeatureCollection of street centerlines
        zoning_field: property name on each parcel feature holding district code
        parcel_id_field: property name to copy through as the parcel id

    Returns:
        (envelopes_fc, strips_fc) — both GeoJSON FeatureCollections in EPSG:4326
    """
    streets_geom = None
    if streets:
        proj_streets = [
            project_to_working(shape(f["geometry"])) for f in streets["features"]
        ]
        streets_geom = unary_union(proj_streets)

    env_features = []
    strip_features = []
    skipped = 0

    for feat in parcels["features"]:
        props = feat.get("properties", {}) or {}
        district = props.get(zoning_field)
        rules = table.lookup(district)
        if rules is None:
            skipped += 1
            continue

        parcel_geom = shape(feat["geometry"])
        for poly_4326 in _as_polygons(parcel_geom):
            poly = project_to_working(poly_4326)
            env = directional_envelope(poly, rules, streets_geom)
            strip = setback_strips(poly, env)

            base_props = {
                parcel_id_field: props.get(parcel_id_field),
                "zoning": district,
                "front_ft": rules.front,
                "side_ft": rules.side,
                "rear_ft": rules.rear,
                "source": rules.source,
            }

            if not env.is_empty:
                env_features.append({
                    "type": "Feature",
                    "properties": {**base_props, "kind": "envelope"},
                    "geometry": mapping(project_to_input(env)),
                })
            if not strip.is_empty:
                strip_features.append({
                    "type": "Feature",
                    "properties": {**base_props, "kind": "setback"},
                    "geometry": mapping(project_to_input(strip)),
                })

    if skipped:
        log.warning("Skipped %d parcels with unknown districts", skipped)

    return (
        {"type": "FeatureCollection", "features": env_features},
        {"type": "FeatureCollection", "features": strip_features},
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Build SoPo zoning setbacks overlay")
    p.add_argument("--parcels", required=True, type=Path, help="GeoJSON parcels file")
    p.add_argument("--rules", required=True, type=Path, help="districts.yaml")
    p.add_argument("--streets", type=Path, help="GeoJSON street centerlines (optional)")
    p.add_argument("--out-envelopes", type=Path, default=Path("envelopes.geojson"))
    p.add_argument("--out-strips", type=Path, default=Path("setback_strips.geojson"))
    p.add_argument("--zoning-field", default="zoning")
    p.add_argument("--parcel-id-field", default="id")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    table = SetbackTable.from_yaml(args.rules)
    parcels = json.loads(args.parcels.read_text())
    streets = json.loads(args.streets.read_text()) if args.streets else None

    env_fc, strip_fc = build_overlay(
        parcels, table, streets,
        zoning_field=args.zoning_field,
        parcel_id_field=args.parcel_id_field,
    )

    args.out_envelopes.write_text(json.dumps(env_fc))
    args.out_strips.write_text(json.dumps(strip_fc))
    log.info(
        "Wrote %d envelopes -> %s, %d strips -> %s",
        len(env_fc["features"]), args.out_envelopes,
        len(strip_fc["features"]), args.out_strips,
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
