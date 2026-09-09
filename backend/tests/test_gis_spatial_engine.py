"""
Full Test Suite for ORCA GIS Layer, Bhuvan Adapter & Deterministic Spatial Engine.
Validates:
- Bhuvan Geocoding, Reverse Geocoding, and Routing
- SpatialEngine geometric calculations (point-in-polygon, distances, intersections)
- Route crossing violations through restricted zones
- GIS database layer screening & SpatialContext generation
- Dynamic IMD cyclone geometry overlap screening
- Safety and fail-safe invariants
"""

import pytest

from backend.app.services.geospatial.bhuvan.adapter import bhuvan_adapter
from backend.app.services.geospatial.bhuvan.query_builder import bhuvan_query_builder
from backend.app.services.geospatial.bhuvan.health import bhuvan_health_inspector
from backend.app.services.geospatial.spatial_engine import spatial_engine
from backend.app.services.geospatial.database import (
    gis_database,
    VERIFIED_PORTS,
    VERIFIED_RESTRICTED_ZONES,
    VERIFIED_MARINE_SANCTUARIES
)

# =============================================================================
# 1. BHUVAN ADAPTER TESTS
# =============================================================================

@pytest.mark.anyio
async def test_bhuvan_geocoding():
    res = await bhuvan_adapter.geocode("Nagapattinam", state="Tamil Nadu")
    assert res.location_name
    assert abs(res.latitude - 10.767) < 0.5
    assert abs(res.longitude - 79.843) < 0.5
    assert "BHUVAN" in res.source

@pytest.mark.anyio
async def test_bhuvan_reverse_geocoding():
    res = await bhuvan_adapter.reverse_geocode(10.767, 79.843)
    assert res.village
    assert res.distance_to_settlement_km is not None
    assert "BHUVAN" in res.source

@pytest.mark.anyio
async def test_bhuvan_marine_shortest_path():
    route = await bhuvan_adapter.shortest_path(10.767, 79.843, 13.082, 80.270)
    assert route.distance_km > 200.0
    assert route.duration_min > 0.0
    assert len(route.path_coordinates) >= 2

@pytest.mark.anyio
async def test_bhuvan_health():
    health = await bhuvan_health_inspector.check_health()
    assert health.source_id == "BHUVAN_NRSC"
    assert health.name == "Bhuvan"

# =============================================================================
# 2. DETERMINISTIC SPATIAL ENGINE TESTS
# =============================================================================

def test_spatial_engine_point_in_polygon():
    # Mumbai Harbor Fairway Zone B boundary
    fairway_coords = VERIFIED_RESTRICTED_ZONES[0]["coordinates"]
    
    # Point inside Zone B
    assert spatial_engine.point_in_polygon(18.97, 72.64, fairway_coords) is True
    
    # Point outside Zone B (e.g. Alibag Zone C)
    assert spatial_engine.point_in_polygon(18.58, 72.70, fairway_coords) is False

def test_spatial_engine_distance_calculations():
    # Mumbai to Goa distance ~400-450 km
    d = spatial_engine.calculate_distance(18.97, 72.82, 15.498, 73.827)
    assert 380.0 <= d <= 460.0

def test_spatial_engine_distance_to_coast():
    # Point near Mumbai harbor should be close to coast (< 20 km)
    d = spatial_engine.distance_to_coast(18.97, 72.82)
    assert d < 20.0

def test_spatial_engine_find_nearest():
    nearest = spatial_engine.find_nearest(10.767, 79.843, VERIFIED_PORTS)
    assert nearest is not None
    assert nearest["name"] == "Nagapattinam Port"
    assert nearest["distance_km"] < 5.0

def test_spatial_engine_route_intersects_restricted_zone():
    # Route through Mumbai Fairway Zone B
    transit_corridor = [[18.80, 72.50], [19.15, 72.80]]
    violations = spatial_engine.route_intersects(transit_corridor, VERIFIED_RESTRICTED_ZONES)
    assert len(violations) >= 1
    assert violations[0]["zone_id"] == "ZONE_B_FAIRWAY"

# =============================================================================
# 3. GIS DATABASE & DYNAMIC HAZARD TESTS
# =============================================================================

def test_gis_database_static_screening():
    # Test SpatialContext near Mumbai
    ctx = gis_database.get_spatial_context(18.97, 72.64)
    assert ctx["location"]["lat"] == 18.97
    assert ctx["nearest_port"]["name"] in ("Mumbai Port Trust", "Jawaharlal Nehru Port (JNPT)")
    assert ctx["has_active_restriction"] is True
    assert any(r["zone_id"] == "ZONE_B_FAIRWAY" for r in ctx["restrictions"])

def test_gis_database_dynamic_cyclone_overlap():
    # Simulate active cyclone wind polygon over Arabian Sea
    cyclone_geom = {
        "name": "Cyclone Nilofar",
        "wind_polygon": [
            [18.0, 71.0],
            [20.0, 71.0],
            [20.0, 73.0],
            [18.0, 73.0]
        ]
    }
    # Point inside cyclone wind swath
    ctx_inside = gis_database.get_spatial_context(19.0, 72.0, active_cyclone_geometry=cyclone_geom)
    assert ctx_inside["has_active_hazard_overlap"] is True
    assert ctx_inside["hazard_overlaps"][0]["hazard_type"] == "CYCLONE_GALE_WIND_POLYGON"
    assert ctx_inside["hazard_overlaps"][0]["is_inside"] is True

    # Point outside cyclone wind swath (e.g. Nagapattinam on East Coast)
    ctx_outside = gis_database.get_spatial_context(10.767, 79.843, active_cyclone_geometry=cyclone_geom)
    assert ctx_outside["has_active_hazard_overlap"] is False
