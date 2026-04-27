"""
Tests for sopo_setbacks. Uses synthetic parcels in a small region near
South Portland (Casco Bay) so we can verify geometry without real data.

Run with: python test_sopo_setbacks.py
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

from shapely.geometry import LineString, Polygon, mapping, shape

import sopo_setbacks as ss


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ft_to_deg_at(lat: float) -> tuple[float, float]:
    """Approximate degrees per foot at the given latitude. Good enough for
    constructing test fixtures."""
    deg_per_meter_lat = 1 / 111_320.0
    deg_per_meter_lon = 1 / (111_320.0 * math.cos(math.radians(lat)))
    ft_to_m = 0.3048
    return deg_per_meter_lon * ft_to_m, deg_per_meter_lat * ft_to_m


def _rect_parcel(
    west_ft: float,
    south_ft: float,
    w_ft: float,
    h_ft: float,
    origin=(43.6428, -70.2553),
) -> Polygon:
    """Build a rectangular parcel measured in feet from the origin
    (default: South Portland-ish lat/lon)."""
    lat0, lon0 = origin
    dlon, dlat = _ft_to_deg_at(lat0)
    west = lon0 + west_ft * dlon
    east = lon0 + (west_ft + w_ft) * dlon
    south = lat0 + south_ft * dlat
    north = lat0 + (south_ft + h_ft) * dlat
    return Polygon([(west, south), (east, south), (east, north), (west, north)])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_setback_table_loads():
    table = ss.SetbackTable.from_yaml(Path(__file__).parent / "districts.yaml")
    assert "C" in table.rules
    assert table.rules["C"].front == 15
    print("✓ SetbackTable.from_yaml loads districts.yaml")


def test_uniform_envelope_shrinks_parcel():
    """Inward buffer by 25 ft should produce envelope ~25 ft inset on every
    side. Check the envelope's bbox is inset by ~25 ft from the parcel's."""
    parcel_4326 = _rect_parcel(0, 0, 100, 200)  # 100x200 ft rectangle
    parcel = ss.project_to_working(parcel_4326)

    rules = ss.SetbackRules(front=25, side=10, rear=20)
    env = ss.uniform_envelope(parcel, rules)

    # max_setback=25 ft = 7.62 m → uniform inset of ~7.62 m
    expected_m = 25 * ss.FT_TO_M
    minx, miny, maxx, maxy = parcel.bounds
    e_minx, e_miny, e_maxx, e_maxy = env.bounds

    tol = 0.2  # meters; UTM scale distortion contributes ~0.1m at this lat
    assert (
        abs((e_minx - minx) - expected_m) < tol
    ), f"Left inset {e_minx - minx:.3f} != {expected_m:.3f}"
    assert abs((maxx - e_maxx) - expected_m) < tol
    assert abs((e_miny - miny) - expected_m) < tol
    assert abs((maxy - e_maxy) - expected_m) < tol
    print("✓ uniform_envelope produces correct uniform inset")


def test_directional_envelope_no_streets_uses_longest_edge_as_front():
    """200x100 parcel with no streets: longest edge (200ft) becomes front,
    opposite edge becomes rear, others side. With front=25, side=10, rear=20,
    we expect the long sides to be inset 25 (top/bottom) and short sides 10.

    Actually wait — long edges run E-W along the top/bottom. The longest
    edge classified as front = the bottom edge (first in iteration order
    among equal-length, or whichever shapely picks). The opposite (top)
    becomes rear. Left/right become side.
    Expected insets: top/bottom = 25 OR 20 (depending which is front),
    left/right = 10."""
    parcel_4326 = _rect_parcel(
        0, 0, 100, 200
    )  # w=100ft, h=200ft → long sides are vertical
    parcel = ss.project_to_working(parcel_4326)

    rules = ss.SetbackRules(front=25, side=10, rear=20)
    env = ss.directional_envelope(parcel, rules, streets=None)

    minx, miny, maxx, maxy = parcel.bounds
    e_minx, e_miny, e_maxx, e_maxy = env.bounds

    # The longest edges are the left and right vertical edges (200 ft each).
    # The horizontal edges (100 ft) become side, so left/right insets should
    # be {25, 20}*FT_TO_M and top/bottom insets should be 10*FT_TO_M.
    horizontal_insets = [e_miny - miny, maxy - e_maxy]
    vertical_insets = [e_minx - minx, maxx - e_maxx]
    expected_side = 10 * ss.FT_TO_M
    expected_front_rear = sorted([20 * ss.FT_TO_M, 25 * ss.FT_TO_M])

    tol = 0.2
    assert all(
        abs(v - expected_side) < tol for v in horizontal_insets
    ), f"horizontal (side) insets should be ~{expected_side:.2f}m, got {horizontal_insets}"
    actual = sorted(vertical_insets)
    assert all(
        abs(a - e) < tol for a, e in zip(actual, expected_front_rear)
    ), f"vertical insets should be ~{expected_front_rear}, got {actual}"
    print("✓ directional_envelope (no streets) classifies edges correctly")


def test_directional_envelope_with_streets():
    """Same parcel, but now place a street centerline along the BOTTOM edge.
    The bottom edge should become front (25 ft), top becomes rear (20 ft),
    sides become side (10 ft)."""
    parcel_4326 = _rect_parcel(0, 0, 100, 200)
    parcel = ss.project_to_working(parcel_4326)

    # Street running E-W just below the parcel, in WGS84
    south_y = parcel_4326.bounds[1] - 1e-5
    street_4326 = LineString(
        [
            (parcel_4326.bounds[0] - 1e-4, south_y),
            (parcel_4326.bounds[2] + 1e-4, south_y),
        ]
    )
    street = ss.project_to_working(street_4326)

    rules = ss.SetbackRules(front=25, side=10, rear=20)
    env = ss.directional_envelope(parcel, rules, streets=street)

    minx, miny, maxx, maxy = parcel.bounds
    e_minx, e_miny, e_maxx, e_maxy = env.bounds

    tol = 0.2
    # Bottom = front = 25 ft inset
    assert (
        abs((e_miny - miny) - 25 * ss.FT_TO_M) < tol
    ), f"bottom inset {e_miny - miny:.3f}"
    # Top = rear = 20 ft inset
    assert (
        abs((maxy - e_maxy) - 20 * ss.FT_TO_M) < tol
    ), f"top inset {maxy - e_maxy:.3f}"
    # Sides = 10 ft inset
    assert abs((e_minx - minx) - 10 * ss.FT_TO_M) < tol
    assert abs((maxx - e_maxx) - 10 * ss.FT_TO_M) < tol
    print("✓ directional_envelope picks correct front edge from street")


def test_corner_lot_two_streets():
    """Corner lot: streets along south AND east edges. Both should be 'front'
    so both get the front setback. The remaining two edges: one becomes rear
    (the one most opposite the front midpoints), one becomes side."""
    parcel_4326 = _rect_parcel(0, 0, 100, 100)
    parcel = ss.project_to_working(parcel_4326)

    minx, miny, maxx, maxy = parcel_4326.bounds
    south_st = LineString([(minx - 1e-4, miny - 1e-5), (maxx + 1e-4, miny - 1e-5)])
    east_st = LineString([(maxx + 1e-5, miny - 1e-4), (maxx + 1e-5, maxy + 1e-4)])
    streets = ss.project_to_working(south_st).union(ss.project_to_working(east_st))

    rules = ss.SetbackRules(front=25, side=10, rear=20)
    env = ss.directional_envelope(parcel, rules, streets=streets)

    e_minx, e_miny, e_maxx, e_maxy = env.bounds
    pminx, pminy, pmaxx, pmaxy = parcel.bounds
    tol = 0.2
    # Bottom and right should both be 25 ft (front) = 7.62 m
    assert abs((e_miny - pminy) - 25 * ss.FT_TO_M) < tol
    assert abs((pmaxx - e_maxx) - 25 * ss.FT_TO_M) < tol
    print("✓ corner lot: two street-facing edges both get front setback")


def test_envelope_smaller_than_parcel():
    """Sanity: envelope area must always be < parcel area for non-zero setbacks."""
    parcel_4326 = _rect_parcel(0, 0, 100, 200)
    parcel = ss.project_to_working(parcel_4326)
    rules = ss.SetbackRules(front=20, side=10, rear=15)
    env = ss.directional_envelope(parcel, rules, streets=None)
    assert env.area < parcel.area
    assert env.area > 0
    strips = ss.setback_strips(parcel, env)
    # Areas should sum to parcel area (within float tolerance)
    assert abs((env.area + strips.area) - parcel.area) < 1.0
    print("✓ envelope + strips == parcel area")


def test_build_overlay_end_to_end():
    """Run the full pipeline on a 3-parcel synthetic FeatureCollection."""
    parcels_fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": "P1", "zoning": "G"},
                "geometry": mapping(_rect_parcel(0, 0, 100, 150)),
            },
            {
                "type": "Feature",
                "properties": {"id": "P2", "zoning": "C"},
                "geometry": mapping(_rect_parcel(150, 0, 100, 150)),
            },
            {
                "type": "Feature",
                "properties": {"id": "P3", "zoning": "MYSTERY_ZONE"},
                "geometry": mapping(_rect_parcel(300, 0, 100, 150)),
            },
        ],
    }
    table = ss.SetbackTable.from_yaml(Path(__file__).parent / "districts.yaml")

    env_fc, strip_fc = ss.build_overlay(parcels_fc, table)

    # P1 (G) and P2 (C) should produce features; P3 is unknown -> skipped (lenient)
    ids = sorted([f["properties"]["id"] for f in env_fc["features"]])
    assert ids == ["P1", "P2"], f"unexpected ids: {ids}"

    # P2 has front=15, side=0, rear=0 → envelope is parcel minus a 15ft front strip
    p2_env_feat = next(f for f in env_fc["features"] if f["properties"]["id"] == "P2")
    p2_env = shape(p2_env_feat["geometry"])
    p2_parcel = shape(parcels_fc["features"][1]["geometry"])
    # Envelope area should be roughly 85% of parcel area (15ft setback on the
    # shortest dimension, which is 100ft → 85/100).
    p2_parcel_proj = ss.project_to_working(p2_parcel)
    p2_env_proj = ss.project_to_working(p2_env)
    ratio = p2_env_proj.area / p2_parcel_proj.area
    assert 0.80 < ratio < 0.90, f"P2 envelope ratio {ratio:.3f} not in [0.80, 0.90]"

    print("✓ build_overlay end-to-end: 2/3 parcels produced envelopes, areas check")


def test_cli_writes_files():
    """Smoke test the CLI by invoking _main() with a temp dir."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        parcels_path = td / "parcels.geojson"
        env_path = td / "env.geojson"
        strip_path = td / "strips.geojson"

        parcels_fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"id": "X", "zoning": "G"},
                    "geometry": mapping(_rect_parcel(0, 0, 100, 100)),
                }
            ],
        }
        parcels_path.write_text(json.dumps(parcels_fc))

        rc = ss._main(
            [
                "--parcels",
                str(parcels_path),
                "--rules",
                str(Path(__file__).parent / "districts.yaml"),
                "--out-envelopes",
                str(env_path),
                "--out-strips",
                str(strip_path),
            ]
        )
        assert rc == 0
        assert env_path.exists()
        assert strip_path.exists()
        env_data = json.loads(env_path.read_text())
        assert len(env_data["features"]) == 1
        print("✓ CLI writes envelope and strip GeoJSONs")


if __name__ == "__main__":
    test_setback_table_loads()
    test_uniform_envelope_shrinks_parcel()
    test_directional_envelope_no_streets_uses_longest_edge_as_front()
    test_directional_envelope_with_streets()
    test_corner_lot_two_streets()
    test_envelope_smaller_than_parcel()
    test_build_overlay_end_to_end()
    test_cli_writes_files()
    print("\nAll tests passed.")
