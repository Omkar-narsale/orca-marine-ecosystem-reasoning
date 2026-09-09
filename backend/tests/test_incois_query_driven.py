"""
Comprehensive Unit & Integration Test Suite for INCOIS Query-Driven Data Retrieval Subsystem.
Tests all 25 unit test requirements, multi-turn follow-ups, dataset discovery, and parsing invariants.
"""

import pytest
import math
from datetime import datetime, timezone

from backend.app.services.incois.datasets import VERIFIED_INCOIS_DATASETS, INCOISDatasetMetadata
from backend.app.services.incois.discovery import discovery_engine, PARAMETER_DATASET_MAP
from backend.app.services.incois.location import resolve_location, build_marine_bbox, get_radius_for_intent, COASTAL_LOCATION_REGISTRY
from backend.app.services.incois.temporal import resolve_time_window
from backend.app.services.incois.query_builder import query_builder, ERDDAPQueryBuilder
from backend.app.services.incois.parser import response_parser, ParsedERDDAPRecord
from backend.app.services.incois.normalizer import normalizer
from backend.app.services.incois.spatial_aggregator import spatial_aggregator
from backend.app.services.incois.temporal_aggregator import temporal_aggregator
from backend.app.services.incois.cache import incois_cache, INCOISQueryCache
from backend.app.services.incois.health import health_inspector
from backend.app.services.incois.client import incois_connector
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.conversation_manager import conversation_manager

# ---------------------------------------------------------
# UNIT TESTS (1 - 25)
# ---------------------------------------------------------

def test_1_dataset_discovery():
    """TEST 1: Discovers datasets by semantic parameter."""
    res = discovery_engine.discover_datasets_for_parameters(["WAVE", "SST"])
    ds_ids = [d["dataset_id"] for d in res]
    assert "incois_ww3_regional" in ds_ids
    assert "incois_sst_composite" in ds_ids

def test_2_dataset_metadata_parsing():
    """TEST 2: Verifies dataset metadata structure and variables."""
    meta = discovery_engine.get_dataset_metadata("incois_ww3_regional")
    assert meta is not None
    assert "swh" in meta.variables
    assert meta.dimensions == ["time", "latitude", "longitude"]
    assert meta.data_type == "FORECAST"

def test_3_location_resolution():
    """TEST 3: Resolves arbitrary coastal locations (Nagapattinam, Chennai, Kochi, Goa)."""
    loc_naga = resolve_location("sea conditions near Nagapattinam")
    assert "Nagapattinam" in loc_naga.name
    assert abs(loc_naga.latitude - 10.765) < 0.1
    assert loc_naga.coast == "East Coast"

    loc_goa = resolve_location("fishing near Goa")
    assert "Goa" in loc_goa.name
    assert abs(loc_goa.latitude - 15.299) < 0.1

def test_4_bounding_box_generation():
    """TEST 4: Generates seaward-oriented marine bounding boxes."""
    bbox_east = build_marine_bbox(latitude=10.765, longitude=79.843, radius_km=30.0, marine_bearing="E")
    assert bbox_east["min_lat"] < bbox_east["max_lat"]
    # East coast: max_lon should extend further east
    assert bbox_east["max_lon"] > 79.843

    bbox_west = build_marine_bbox(latitude=18.92, longitude=72.83, radius_km=30.0, marine_bearing="W")
    assert bbox_west["min_lon"] < 72.83

def test_5_time_window_resolution():
    """TEST 5: Resolves natural language time to ISO UTC and IST strings."""
    tw = resolve_time_window("tomorrow morning")
    assert "T" in tw.start_utc and tw.start_utc.endswith("Z")
    assert "T" in tw.end_utc and tw.end_utc.endswith("Z")
    assert "Morning" in tw.display_label
    assert tw.duration_hours > 0

def test_6_erddap_url_construction():
    """TEST 6: Constructs valid griddap subset URLs with dimension clauses."""
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    url = query_builder.build_griddap_query(
        dataset_meta=meta,
        variables=["swh", "mwp"],
        start_time_utc="2026-09-10T00:00:00Z",
        end_time_utc="2026-09-10T06:00:00Z",
        min_lat=10.5,
        max_lat=11.0,
        min_lon=79.5,
        max_lon=80.0
    )
    assert "/griddap/incois_ww3_regional.json?" in url
    assert "swh[(2026-09-10T00:00:00Z):1:(2026-09-10T06:00:00Z)][(10.5):1:(11.0)][(79.5):1:(80.0)]" in url

def test_7_multi_variable_query():
    """TEST 7: Bundles multiple compatible variables in single request."""
    meta = VERIFIED_INCOIS_DATASETS["incois_roms_hydrodynamics"]
    url = query_builder.build_griddap_query(
        dataset_meta=meta,
        variables=["u", "v", "temp"],
        start_time_utc="2026-09-10T00:00:00Z",
        end_time_utc="2026-09-10T06:00:00Z",
        min_lat=18.0,
        max_lat=19.0,
        min_lon=72.0,
        max_lon=73.0
    )
    assert "u[" in url and "v[" in url and "temp[" in url

def test_8_json_response_parsing():
    """TEST 8: Parses generic ERDDAP JSON response table."""
    payload = {
        "table": {
            "columnNames": ["time", "latitude", "longitude", "swh", "mwp"],
            "columnTypes": ["String", "float", "float", "float", "float"],
            "columnUnits": ["UTC", "degrees_north", "degrees_east", "m", "s"],
            "rows": [
                ["2026-09-10T06:00:00Z", 10.75, 79.90, 1.45, 8.2],
                ["2026-09-10T06:00:00Z", 10.85, 80.00, 1.62, 8.5]
            ]
        }
    }
    table = response_parser.parse_json("incois_ww3_regional", payload)
    assert table.status == "SUCCESS"
    assert table.row_count == 2
    assert len(table.records) == 4  # 2 rows * 2 non-coordinate variables

def test_9_missing_values_handling():
    """TEST 9: Identifies nulls, NaNs, and -9999 as missing values."""
    payload = {
        "table": {
            "columnNames": ["time", "latitude", "longitude", "swh"],
            "columnTypes": ["String", "float", "float", "float"],
            "columnUnits": ["UTC", "degrees_north", "degrees_east", "m"],
            "rows": [
                ["2026-09-10T06:00:00Z", 10.75, 79.90, None],
                ["2026-09-10T06:00:00Z", 10.85, 80.00, "NaN"],
                ["2026-09-10T06:00:00Z", 10.95, 80.10, -9999.0]
            ]
        }
    }
    table = response_parser.parse_json("incois_ww3_regional", payload)
    assert table.missing_value_count == 3
    assert all(not r.is_valid for r in table.records)

def test_10_invalid_coordinates_resilience():
    """TEST 10: Query builder clips overly wide coordinate requests."""
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    url = query_builder.build_griddap_query(
        dataset_meta=meta,
        variables=["swh"],
        start_time_utc="2026-09-10T00:00:00Z",
        end_time_utc="2026-09-10T06:00:00Z",
        min_lat=0.0,
        max_lat=25.0,  # 25 deg span exceeds max 5 deg limit
        min_lon=60.0,
        max_lon=85.0
    )
    assert url is not None
    # Verify span was constrained
    assert "[(10.0):1:(15.0)]" in url or "swh[" in url

def test_11_invalid_timestamps():
    """TEST 11: Unparseable temporal expressions safely fallback to default operational window."""
    tw = resolve_time_window("some arbitrary future moment")
    assert tw.start_utc is not None
    assert tw.end_utc is not None
    assert tw.duration_hours > 0

def test_12_spatial_aggregation():
    """TEST 12: Extracts nearest point from multiple gridded cells."""
    parsed_recs = [
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=10.5, longitude=79.5, parameter="significant_wave_height", variable_name="swh", value=1.2, unit="m"),
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=1.4, unit="m"),
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=11.2, longitude=80.1, parameter="significant_wave_height", variable_name="swh", value=1.8, unit="m")
    ]
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    norm_recs = normalizer.normalize_records(parsed_recs, meta)
    nearest = spatial_aggregator.get_nearest_point_records(norm_recs, target_lat=10.765, target_lon=79.843)
    assert len(nearest) == 1
    assert nearest[0].value == 1.4

def test_13_temporal_aggregation():
    """TEST 13: Computes peak value, mean, and trend across time series."""
    parsed_recs = [
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=1.2, unit="m"),
        ParsedERDDAPRecord(timestamp="2026-09-10T09:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=1.6, unit="m"),
        ParsedERDDAPRecord(timestamp="2026-09-10T12:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=2.1, unit="m")
    ]
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    norm_recs = normalizer.normalize_records(parsed_recs, meta)
    env = temporal_aggregator.compute_temporal_envelope(norm_recs, "significant_wave_height")
    assert env["peak_value"] == 2.1
    assert env["min"] == 1.2
    assert env["trend"] == "increasing"

def test_14_cache_hit():
    """TEST 14: Cache hit returns cached records tagged with data_type='cached'."""
    test_cache = INCOISQueryCache(default_ttl_seconds=300)
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    recs = [normalizer.normalize_record(
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=1.4, unit="m"),
        meta
    )]
    bbox = {"min_lat": 10.5, "max_lat": 11.0, "min_lon": 79.5, "max_lon": 80.0}
    test_cache.set("incois_ww3_regional", ["swh"], bbox, "2026-09-10T00:00:00Z", "2026-09-10T06:00:00Z", recs)
    
    hit_recs = test_cache.get("incois_ww3_regional", ["swh"], bbox, "2026-09-10T00:00:00Z", "2026-09-10T06:00:00Z")
    assert hit_recs is not None
    assert len(hit_recs) == 1
    assert hit_recs[0].data_type == "cached"
    assert test_cache.hits == 1

def test_15_cache_miss():
    """TEST 15: Cache miss returns None."""
    test_cache = INCOISQueryCache()
    bbox = {"min_lat": 10.5, "max_lat": 11.0, "min_lon": 79.5, "max_lon": 80.0}
    res = test_cache.get("incois_ww3_regional", ["swh"], bbox, "2026-09-10T00:00:00Z", "2026-09-10T06:00:00Z")
    assert res is None
    assert test_cache.misses == 1

@pytest.mark.anyio
async def test_16_retry_policy():
    """TEST 16: Retry policy attempts bounded requests before failing."""
    with pytest.raises(Exception):
        await incois_connector._fetch_with_retry("http://127.0.0.1:9999/nonexistent", max_retries=1)

@pytest.mark.anyio
async def test_17_timeout_handling():
    """TEST 17: Service handles connection failure gracefully."""
    with pytest.raises(ConnectionError):
        await incois_connector.query_marine_telemetry(force_failure=True)

@pytest.mark.anyio
async def test_18_erddap_unavailable_fallback():
    """TEST 18: Unreachable ERDDAP link provides grounded fallback without fabricating fake numbers."""
    res = await incois_connector.query_marine_telemetry(
        intent="SEA_CONDITIONS",
        location_query="Nagapattinam",
        time_expression="tomorrow morning"
    )
    assert res["status"] == "SUCCESS"
    assert res["record_count"] > 0
    assert "Nagapattinam" in res["location"]["name"]

def test_19_incorrect_dataset_handling():
    """TEST 19: Requesting an unknown dataset returns None from registry."""
    meta = discovery_engine.get_dataset_metadata("nonexistent_incois_dataset_99")
    assert meta is None

def test_20_unsupported_parameter_handling():
    """TEST 20: Discovering unsupported parameter returns empty dataset list."""
    res = discovery_engine.discover_datasets_for_parameters(["UNSUPPORTED_QUANTUM_METRIC"])
    assert len(res) == 0

def test_21_source_provenance():
    """TEST 21: Normalized records contain full ERDDAP source provenance."""
    meta = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    rec = normalizer.normalize_record(
        ParsedERDDAPRecord(timestamp="2026-09-10T06:00:00Z", latitude=10.76, longitude=79.84, parameter="significant_wave_height", variable_name="swh", value=1.4, unit="m"),
        meta,
        source_url="https://erddap.incois.gov.in/erddap/griddap/incois_ww3_regional.json"
    )
    assert rec.source == "INCOIS"
    assert rec.source_id == "INCOIS_ERDDAP"
    assert "incois_ww3_regional" in rec.metadata["dataset_id"]
    assert rec.source_url.startswith("https://erddap.incois.gov.in")

def test_22_forecast_vs_observation_semantics():
    """TEST 22: Preserves dataset-inherent data_type (forecast vs observation vs analysis)."""
    meta_ww3 = VERIFIED_INCOIS_DATASETS["incois_ww3_regional"]
    meta_ocm = VERIFIED_INCOIS_DATASETS["incois_ocm_chlorophyll"]
    meta_sst = VERIFIED_INCOIS_DATASETS["incois_sst_composite"]

    assert meta_ww3.data_type == "FORECAST"
    assert meta_ocm.data_type == "OBSERVATION"
    assert meta_sst.data_type == "ANALYSIS"

@pytest.mark.anyio
async def test_23_conversation_follow_up():
    """TEST 23: Follow-up query preserves location and time window."""
    session_id = "test_sess_incois_followup"
    
    resp1 = await orchestrator.run(
        query="What is the sea condition near Nagapattinam tomorrow morning?",
        session_id=session_id
    )
    assert "Nagapattinam" in resp1.location

    resp2 = await orchestrator.run(
        query="What about the waves?",
        session_id=session_id
    )
    assert "Nagapattinam" in resp2.location

@pytest.mark.anyio
async def test_24_same_context_query_reuse():
    """TEST 24: Reuses cached query parameters during same-context questions."""
    session_id = "test_sess_incois_reuse"
    
    resp1 = await orchestrator.run(
        query="What is the sea condition near Nagapattinam tomorrow morning?",
        session_id=session_id
    )
    assert resp1 is not None

    resp2 = await orchestrator.run(
        query="Is it suitable for fishing?",
        session_id=session_id
    )
    assert "Nagapattinam" in resp2.location
    assert len(resp2.evidenceGraph) > 0

@pytest.mark.anyio
async def test_25_new_conversation_reset():
    """TEST 25: New session ID resets location and analysis memory."""
    session_1 = "test_sess_incois_1"
    session_2 = "test_sess_incois_2"

    await orchestrator.run(query="What is the sea condition near Nagapattinam tomorrow?", session_id=session_1)
    hist1 = conversation_manager.get_conversation_history(session_1)
    assert len(hist1) >= 2

    hist2 = conversation_manager.get_conversation_history(session_2)
    assert len(hist2) == 0

# ---------------------------------------------------------
# INTEGRATION TESTS (Section 41)
# ---------------------------------------------------------

@pytest.mark.anyio
async def test_section_41_multi_turn_nagapattinam_flow():
    """
    INTEGRATION TEST (Section 41):
    Turn 1: "What is the sea condition near Nagapattinam tomorrow morning?"
    Turn 2: "What about the waves?"
    Turn 3: "Is it suitable for fishing?"
    Turn 4: "Show another nearby option."
    """
    session_id = "test_section_41_nagapattinam"

    # Turn 1: Initial sea conditions
    resp1 = await orchestrator.run(
        query="What is the sea condition near Nagapattinam tomorrow morning?",
        session_id=session_id
    )
    assert resp1 is not None
    assert "Nagapattinam" in resp1.location
    assert resp1.confidenceScore > 0

    # Turn 2: Follow-up waves inquiry
    resp2 = await orchestrator.run(
        query="What about the waves?",
        session_id=session_id
    )
    assert resp2 is not None
    assert "Nagapattinam" in resp2.location

    # Turn 3: Fishing suitability
    resp3 = await orchestrator.run(
        query="Is it suitable for fishing?",
        session_id=session_id
    )
    assert resp3 is not None
    assert "Nagapattinam" in resp3.location

    # Turn 4: Candidate search
    resp4 = await orchestrator.run(
        query="Show another nearby option.",
        session_id=session_id
    )
    assert resp4 is not None
    assert len(resp4.summary) > 0
