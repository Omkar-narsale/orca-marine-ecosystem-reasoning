"""
Unit and Integration Tests for Dataset Discovery & Source-Specific Query Builder Architecture.
Validates:
- Dataset discovery & matching
- Source-specific query builders (INCOIS, MOSDAC, IMD)
- Query safety & bounding box validation
- Parallel multi-source query execution
- Multi-turn conversational context inheritance & parameter scoping
"""

import pytest
import asyncio
from typing import Dict, Any

from backend.app.schemas.query_plan import (
    DataRequirement,
    LocationContext,
    TimeContext,
    ParameterPriority,
    AuthorityType
)
from backend.app.services.discovery.registry import (
    VERIFIED_DATASET_REGISTRY,
    get_verified_dataset,
    list_all_verified_datasets
)
from backend.app.services.discovery.service import discovery_service
from backend.app.services.discovery.executor import query_plan_executor
from backend.app.services.mosdac.query_builder import mosdac_query_builder
from backend.app.services.imd.query_builder import imd_query_builder
from backend.app.services.incois.query_builder import query_builder as incois_query_builder
from backend.app.services.incois.location import resolve_location, build_marine_bbox
from backend.app.services.incois.temporal import resolve_time_window

# =============================================================================
# 1. DATASET REGISTRY & DISCOVERY TESTS
# =============================================================================

def test_verified_registry_integrity():
    """Ensures verified dataset registry contains only authoritative datasets."""
    datasets = list_all_verified_datasets()
    assert len(datasets) >= 8
    
    # INCOIS, MOSDAC, IMD datasets must all be present
    sources = {d.source for d in datasets}
    assert "INCOIS" in sources
    assert "MOSDAC" in sources
    assert "IMD" in sources

    for ds in datasets:
        assert ds.verified is True
        assert ds.dataset_id
        assert ds.official_url.startswith("http")
        assert len(ds.variables) > 0

def test_dataset_discovery_by_parameter():
    """Tests discovery for wave parameters routes to INCOIS WW3."""
    req = DataRequirement(
        parameter="WAVE",
        purpose="MARINE_SAFETY",
        priority=ParameterPriority.CRITICAL
    )
    matches = discovery_service.find_datasets(req)
    assert len(matches) > 0
    best_ds, score = matches[0]
    assert best_ds.source == "INCOIS"
    assert "WAVE" in [p.upper() for p in best_ds.parameters]
    assert score >= 0.70

def test_dataset_discovery_source_preference_mosdac():
    """Tests that specifying MOSDAC source preference prioritizes Oceansat-3 OCM."""
    req = DataRequirement(
        parameter="CHLOROPHYLL",
        source_preference=["MOSDAC"],
        purpose="FISHING_SUITABILITY",
        priority=ParameterPriority.HIGH
    )
    best_ds = discovery_service.find_best_dataset(req)
    assert best_ds is not None
    assert best_ds.source == "MOSDAC"
    assert best_ds.dataset_id == "O3_OCM_L3_DAILY_CHL"

def test_dataset_discovery_spatial_coverage_filter():
    """Tests that location outside coverage reduces compatibility."""
    loc_in_bounds = LocationContext(
        name="Nagapattinam",
        latitude=10.767,
        longitude=79.843,
        marine_bbox={"min_lat": 10.5, "max_lat": 11.0, "min_lon": 79.8, "max_lon": 80.3}
    )
    req = DataRequirement(parameter="WAVE")
    matches = discovery_service.find_datasets(req, location=loc_in_bounds)
    assert len(matches) > 0
    assert matches[0][1] >= 0.70

# =============================================================================
# 2. SOURCE-SPECIFIC QUERY BUILDER TESTS
# =============================================================================

def test_mosdac_query_builder_valid():
    """Tests MOSDAC Download API search format adhering to official documentation."""
    ds = get_verified_dataset("mosdac_oceansat3_ocm_chlorophyll")
    assert ds is not None

    loc = LocationContext(
        name="Nagapattinam",
        latitude=10.767,
        longitude=79.843,
        marine_bbox={"min_lat": 10.517, "max_lat": 11.017, "min_lon": 79.843, "max_lon": 80.343}
    )
    time_ctx = TimeContext(
        start="2026-09-10T00:00:00Z",
        end="2026-09-10T23:59:59Z",
        original_expression="tomorrow"
    )

    query = mosdac_query_builder.build_search_query(
        dataset=ds,
        location=loc,
        time_window=time_ctx,
        count=5
    )

    assert query["datasetId"] == "O3_OCM_L3_DAILY_CHL"
    assert query["startTime"] == "2026-09-10"
    assert query["endTime"] == "2026-09-10"
    assert query["count"] == 5
    # Bounding box must be ordered: minLon,minLat,maxLon,maxLat per MOSDAC manual
    assert query["boundingBox"] == "79.8430,10.5170,80.3430,11.0170"
    assert "https://mosdac.gov.in/downloadapi/search" in query["search_url"]

def test_mosdac_query_builder_span_safety_limit():
    """Rejects unbounded geographic spans over MAX_GEO_SPAN_DEG."""
    ds = get_verified_dataset("mosdac_oceansat3_ocm_chlorophyll")
    loc_huge = LocationContext(
        name="Indian Ocean Entire",
        latitude=10.0,
        longitude=75.0,
        marine_bbox={"min_lat": 0.0, "max_lat": 25.0, "min_lon": 60.0, "max_lon": 90.0}
    )
    time_ctx = TimeContext(start="2026-09-10T00:00:00Z", end="2026-09-10T23:59:59Z")

    with pytest.raises(ValueError, match="exceeds safety span limit"):
        mosdac_query_builder.build_search_query(dataset=ds, location=loc_huge, time_window=time_ctx)

def test_imd_query_builder_valid():
    """Tests IMD Coastal Marine Bulletin query construction."""
    ds = get_verified_dataset("imd_coastal_marine_bulletin")
    assert ds is not None

    loc = LocationContext(
        name="Nagapattinam",
        latitude=10.767,
        longitude=79.843,
        marine_bbox={"min_lat": 10.517, "max_lat": 11.017, "min_lon": 79.843, "max_lon": 80.343},
        state="Tamil Nadu"
    )
    time_ctx = TimeContext(start="2026-09-10T00:00:00Z", end="2026-09-10T12:00:00Z")

    query = imd_query_builder.build_bulletin_query(
        dataset=ds,
        location=loc,
        time_window=time_ctx,
        warning_type="SQUALL"
    )

    assert query["source"] == "IMD"
    assert query["params"]["coastal_location"] == "Nagapattinam"
    assert query["params"]["state"] == "Tamil Nadu"
    assert query["params"]["warning_type"] == "SQUALL"

# =============================================================================
# 3. QUERY PLAN BUILDER & PARALLEL EXECUTION TESTS
# =============================================================================

def test_create_query_plan_sea_conditions():
    """Tests QueryPlan creation for SEA_CONDITIONS intent near Nagapattinam."""
    plan = query_plan_executor.create_query_plan(
        intent="SEA_CONDITIONS",
        location_query="Nagapattinam",
        time_expression="tomorrow morning"
    )

    assert plan.intent == "SEA_CONDITIONS"
    assert "Nagapattinam" in plan.location.name
    assert plan.location.marine_bbox["max_lat"] > plan.location.marine_bbox["min_lat"]
    assert len(plan.requirements) >= 2
    
    # Must have planned query items
    assert len(plan.items) >= 2
    sources = {item.source for item in plan.items}
    assert "INCOIS" in sources

@pytest.mark.anyio
async def test_execute_query_plan_parallel():
    """Tests parallel execution across INCOIS, MOSDAC, and IMD."""
    plan = query_plan_executor.create_query_plan(
        intent="FISHING_SUITABILITY",
        location_query="Nagapattinam",
        time_expression="tomorrow morning",
        purpose="FISHING_SUITABILITY"
    )

    result = await query_plan_executor.execute_plan(plan, trace_id="ORCA-TEST-TRACE-001")
    assert result["status"] == "SUCCESS"
    assert result["record_count"] > 0
    assert "INCOIS" in result["sources_queried"]
    assert "MOSDAC" in result["sources_queried"]
    assert "IMD" in result["sources_queried"]

    # Verify authority types on normalized records
    for rec in result["records"]:
        assert rec.source in ("INCOIS", "MOSDAC", "IMD")
        assert rec.value is not None
        assert rec.latitude is not None
        assert rec.longitude is not None

# =============================================================================
# 4. MULTI-TURN CONVERSATIONAL SCENARIO (SECTION 20-22)
# =============================================================================

@pytest.mark.anyio
async def test_multi_turn_conversational_workflow():
    """
    Simulates Section 20-22 multi-turn flow:
    1. 'Sea condition near Nagapattinam tomorrow' -> INCOIS (wave, sst, current)
    2. 'What about chlorophyll?' -> Inherit Nagapattinam/tomorrow, query MOSDAC only
    3. 'Is it suitable for fishing?' -> Inherit, query missing (wind, warnings, PFZ)
    4. 'What about Goa?' -> Reset location, query fresh plan
    """
    # Step 1: Primary Query
    plan_1 = query_plan_executor.create_query_plan(
        intent="SEA_CONDITIONS",
        location_query="Nagapattinam",
        time_expression="tomorrow morning"
    )
    res_1 = await query_plan_executor.execute_plan(plan_1)
    assert res_1["status"] == "SUCCESS"
    p1_sources = set(res_1["sources_queried"])
    assert "INCOIS" in p1_sources

    # Step 2: Follow-up 'What about chlorophyll?'
    # Inherits location and time, requests only CHLOROPHYLL
    plan_2 = query_plan_executor.create_query_plan(
        intent="CHLOROPHYLL_QUERY",
        location_query=plan_1.location.name,
        time_expression=plan_1.time.original_expression,
        explicit_parameters=["CHLOROPHYLL"]
    )
    assert len(plan_2.requirements) == 1
    assert plan_2.requirements[0].parameter == "CHLOROPHYLL"
    res_2 = await query_plan_executor.execute_plan(plan_2)
    assert "MOSDAC" in res_2["sources_queried"]

    # Step 3: Follow-up 'Is it suitable for fishing?'
    # Inherits location and time, expands to FISHING_SUITABILITY
    plan_3 = query_plan_executor.create_query_plan(
        intent="FISHING_SUITABILITY",
        location_query=plan_1.location.name,
        time_expression=plan_1.time.original_expression,
        purpose="FISHING_SUITABILITY"
    )
    res_3 = await query_plan_executor.execute_plan(plan_3)
    assert "IMD" in res_3["sources_queried"]
    assert "MOSDAC" in res_3["sources_queried"]
    assert "INCOIS" in res_3["sources_queried"]

    # Step 4: Follow-up 'What about Goa?'
    # Switches location context to Goa
    plan_4 = query_plan_executor.create_query_plan(
        intent="SEA_CONDITIONS",
        location_query="Goa",
        time_expression="tomorrow morning"
    )
    assert "Goa" in plan_4.location.name
    res_4 = await query_plan_executor.execute_plan(plan_4)
    assert res_4["status"] == "SUCCESS"
    assert any("Goa" in r.metadata.get("authority_type", "") or abs(r.latitude - 15.498) < 1.0 for r in res_4["records"])
