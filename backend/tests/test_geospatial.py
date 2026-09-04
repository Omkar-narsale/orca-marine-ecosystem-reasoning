import pytest
from backend.app.services.geospatial.geometry import (
    point_in_polygon,
    calculate_polygon_intersection,
    haversine_distance_km,
    calculate_centroid,
    create_polygon
)
from backend.app.services.geospatial.geofence import (
    geofence_engine,
    GEOFENCE_MUMBAI_NAVAL_ANCHORAGE
)

def test_point_in_polygon():
    # Square polygon around [19.0, 72.0] to [20.0, 73.0]
    poly_coords = [[19.0, 72.0], [20.0, 72.0], [20.0, 73.0], [19.0, 73.0]]
    
    inside_pt = [19.5, 72.5]
    outside_pt = [21.0, 74.0]
    
    assert point_in_polygon(inside_pt[0], inside_pt[1], poly_coords) is True
    assert point_in_polygon(outside_pt[0], outside_pt[1], poly_coords) is False

def test_polygon_intersection():
    poly1 = [[19.0, 72.0], [19.5, 72.0], [19.5, 72.5], [19.0, 72.5]]
    poly2_overlapping = [[19.2, 72.2], [19.8, 72.2], [19.8, 72.8], [19.2, 72.8]]
    poly3_disjoint = [[20.0, 74.0], [20.5, 74.0], [20.5, 74.5], [20.0, 74.5]]

    inter_res1 = calculate_polygon_intersection(poly1, poly2_overlapping)
    assert inter_res1["intersects"] is True
    assert inter_res1["intersection_type"] == "PARTIAL_INTERSECTION"
    assert inter_res1["area_sq_deg"] > 0

    inter_res2 = calculate_polygon_intersection(poly1, poly3_disjoint)
    assert inter_res2["intersects"] is False
    assert inter_res2["intersection_type"] == "NO_INTERSECTION"

def test_haversine_distance():
    # Mumbai (18.97, 72.82) to Alibag (18.64, 72.87) approx 37 km
    dist = haversine_distance_km(18.97, 72.82, 18.64, 72.87)
    assert 30.0 < dist < 45.0

def test_calculate_centroid():
    poly = [[19.0, 72.0], [20.0, 72.0], [20.0, 73.0], [19.0, 73.0]]
    lat, lon = calculate_centroid(poly)
    assert abs(lat - 19.5) < 0.01
    assert abs(lon - 72.5) < 0.01

def test_geofence_detection_restricted_zone_b():
    # Zone B overlaps with Mumbai Naval Anchorage
    zone_b_coords = [
        [18.86, 72.52],
        [19.08, 72.52],
        [19.08, 72.76],
        [18.86, 72.76]
    ]
    eval_b = geofence_engine.evaluate_zone_geofence("zone-b", zone_b_coords)
    assert eval_b["restricted"] is True
    assert len(eval_b["intersections"]) >= 1
    assert any("Naval Anchorage" in inter["name"] for inter in eval_b["intersections"])

def test_geofence_detection_clear_zone_c():
    # Zone C is in Alibag offshore shelf and outside restrictions
    zone_c_coords = [
        [18.42, 72.55],
        [18.75, 72.55],
        [18.75, 72.86],
        [18.42, 72.86]
    ]
    eval_c = geofence_engine.evaluate_zone_geofence("zone-c", zone_c_coords)
    assert eval_c["restricted"] is False
    assert eval_c["intersections"] == []
