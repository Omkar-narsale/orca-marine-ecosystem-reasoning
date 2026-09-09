"""
Full Test Suite for Official IMD Meteorological & Cyclone Architecture.
Validates:
- All 10 official IMD query builders
- IMD response parsers (including cyclone track, wind swaths, uncertainty cones)
- IMD location resolution mapping
- IMD normalization & authority tagging
- IMD health inspector
"""

import pytest
from datetime import datetime, timezone

from backend.app.services.imd.query_builder import imd_query_builder
from backend.app.services.imd.registry import resolve_imd_location, IMD_COASTAL_REGISTRY
from backend.app.services.imd.parser import imd_response_parser
from backend.app.services.imd.normalizer import imd_normalizer
from backend.app.services.imd.health import imd_health_inspector
from backend.app.schemas.query_plan import AuthorityType

# =============================================================================
# 1. IMD QUERY BUILDER TESTS (10 ENDPOINTS)
# =============================================================================

def test_imd_builder_current_weather():
    q = imd_query_builder.build_current_weather("43003", 18.97, 72.82)
    assert q["endpoint"] == "/api/v1/current_wx"
    assert q["params"]["station_id"] == "43003"
    assert "lat=18.97" in q["url"]

def test_imd_builder_location_forecast():
    q = imd_query_builder.build_location_forecast("43347", 10.767, 79.843, days=5)
    assert q["endpoint"] == "/api/v1/cityforecastloc"
    assert q["params"]["station_id"] == "43347"
    assert q["params"]["days"] == 5

def test_imd_builder_district_nowcast():
    q = imd_query_builder.build_district_nowcast("TN_NAGAPATTINAM")
    assert q["endpoint"] == "/api/v1/districtnowcast"
    assert q["params"]["district_id"] == "TN_NAGAPATTINAM"

def test_imd_builder_district_warning():
    q = imd_query_builder.build_district_warning("MH_MUMBAI")
    assert q["endpoint"] == "/api/v1/districtwarning"
    assert q["params"]["district_id"] == "MH_MUMBAI"

def test_imd_builder_sea_bulletin():
    q = imd_query_builder.build_sea_bulletin("North Arabian Sea")
    assert q["endpoint"] == "/api/v1/seabulletin"
    assert q["params"]["sea_area"] == "North Arabian Sea"

def test_imd_builder_coastal_bulletin():
    q = imd_query_builder.build_coastal_bulletin("North Maharashtra Coast")
    assert q["endpoint"] == "/api/v1/coastalbulletin"
    assert q["params"]["coastal_zone"] == "North Maharashtra Coast"

def test_imd_builder_fishermen_warning():
    q = imd_query_builder.build_fishermen_warning("Tamil Nadu Coast")
    assert q["endpoint"] == "/api/v1/fishermenwarning"
    assert q["params"]["coastal_region"] == "Tamil Nadu Coast"

def test_imd_builder_cyclone_endpoints():
    track_q = imd_query_builder.build_cyclone_track("ARB-01")
    wind_q = imd_query_builder.build_cyclone_wind("ARB-01")
    cone_q = imd_query_builder.build_cyclone_cone("ARB-01")

    assert track_q["endpoint"] == "/api/v1/cyclone_track"
    assert wind_q["endpoint"] == "/api/v1/cyclone_wind"
    assert cone_q["endpoint"] == "/api/v1/cyclone_cou"

def test_imd_builder_validation_errors():
    with pytest.raises(ValueError, match="station_id required"):
        imd_query_builder.build_current_weather("", 18.97, 72.82)

    with pytest.raises(ValueError, match="district_id required"):
        imd_query_builder.build_district_warning("")

# =============================================================================
# 2. IMD LOCATION RESOLUTION TESTS
# =============================================================================

def test_imd_location_resolution_coastal_cities():
    cities = ["Nagapattinam", "Mumbai", "Goa", "Kochi", "Chennai", "Visakhapatnam"]
    for city in cities:
        res = resolve_imd_location(city)
        assert res["station_id"]
        assert res["district_id"]
        assert res["marine_region"]
        assert res["confidence"] >= 0.90

# =============================================================================
# 3. IMD PARSER & NORMALIZATION TESTS
# =============================================================================

def test_imd_parser_current_weather():
    payload = {
        "station_id": "43347",
        "station_name": "Nagapattinam Port",
        "lat": 10.767,
        "lon": 79.843,
        "temp": 29.4,
        "humidity": 82.0,
        "wind_speed": 15.5,
        "wind_dir": "NE (045°)",
        "condition": "Scattered Clouds"
    }
    model = imd_response_parser.parse_current_weather(payload)
    assert model.station_id == "43347"
    assert model.temperature_c == 29.4
    assert model.wind_speed_kt == 15.5

    records = imd_normalizer.normalize_current_weather(model)
    assert len(records) == 1
    rec = records[0]
    assert rec.source == "IMD"
    assert rec.value == 15.5
    assert rec.metadata["authority_type"] == AuthorityType.OFFICIAL_OBSERVATION.value

def test_imd_parser_fishermen_warning():
    payload = {
        "coastal_region": "North Maharashtra Coast",
        "severity": "High Alert",
        "wind_speed_range_kt": "30-40",
        "headline": "Gale wind speed reaching 35-45 knots likely over North Maharashtra coast.",
        "instructions": "Fishermen are advised not to venture into sea."
    }
    model = imd_response_parser.parse_fishermen_warning(payload)
    assert model.severity == "High Alert"
    assert "Fishermen" in model.instructions

    records = imd_normalizer.normalize_fishermen_warning(model, 19.30, 72.53)
    assert len(records) == 1
    assert records[0].data_type == "warning"
    assert records[0].metadata["authority_type"] == AuthorityType.OFFICIAL_WARNING.value

def test_imd_parser_cyclone_geometries():
    cone_payload = {
        "cyclone_id": "CYCLONE-ARABIAN-01",
        "name": "Biparjoy",
        "cone_polygon": [
            [16.0, 68.0],
            [19.0, 69.5],
            [22.0, 68.5],
            [19.0, 67.0]
        ]
    }
    cone = imd_response_parser.parse_cyclone_cone(cone_payload)
    assert cone.name == "Biparjoy"
    assert len(cone.cone_polygon) == 4

@pytest.mark.anyio
async def test_imd_health_inspector():
    health = await imd_health_inspector.check_health()
    assert health.source_id == "IMD_MARINE"
    assert health.name == "IMD"
    assert health.health_state in ("HEALTHY", "DEGRADED")
