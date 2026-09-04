"""ORCA Phase 5: Candidate Zone Ranking & Decision Intelligence Tests
==================================================================
Tests:
1. Deterministic suitability score calculation
2. Candidate zone ranking (Top Candidate, Alternative, Excluded)
3. Hard exclusion overrides (Restricted boundary, High Hazard)
4. Multi-factor Trade-off analysis
5. Operational route corridor planning & geofence auditing
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.decision.suitability_engine import suitability_engine, calculate_suitability_score
from backend.app.services.decision.ranking_engine import rank_candidate_zones, ranking_engine
from backend.app.services.decision.tradeoff_engine import compare_zones_tradeoff
from backend.app.services.decision.route_engine import plan_route_corridor

client = TestClient(app)


def test_suitability_score_deterministic():
    """Verify suitability calculation produces expected score without false catch guarantees."""
    res = calculate_suitability_score("zone-c", risk_score=22.0, risk_level="LOW", env_indicators={"seaSurfaceTemp": "28.5°C"})
    assert res.suitability_score >= 65.0
    assert res.operational_status == "CANDIDATE"
    assert "environmental_score" in res.breakdown
    assert "safety_score" in res.breakdown


def test_restricted_zone_hard_exclusion():
    """Verify that a geofence restriction strictly excludes a zone regardless of environmental indicators."""
    res = calculate_suitability_score("zone-b", risk_score=60.0, risk_level="RESTRICTED", env_indicators={"seaSurfaceTemp": "28.5°C"}, is_restricted=True)
    assert res.suitability_score == 0
    assert res.operational_status == "EXCLUDED"


def test_candidate_ranking_engine():
    """Verify ranking order: Zone C top, Zone D alternative, Zones A and B excluded."""
    ranking = rank_candidate_zones()
    assert ranking.top_candidate is not None
    assert ranking.top_candidate.zone_id == "zone-c"
    assert ranking.top_candidate.operational_status == "TOP_CANDIDATE"
    
    assert ranking.alternative_candidate is not None
    assert ranking.alternative_candidate.zone_id == "zone-d"
    
    excluded_ids = [z.zone_id for z in ranking.excluded_zones]
    assert "zone-a" in excluded_ids
    assert "zone-b" in excluded_ids


def test_tradeoff_engine_explanation():
    """Verify trade-off comparator explains safety vs environmental factors."""
    tradeoff = compare_zones_tradeoff("zone-c", "zone-d")
    assert "zone_1" in tradeoff
    assert "zone_2" in tradeoff
    assert "recommendation" in tradeoff
    assert "ZONE C" in tradeoff["recommendation"] or "ZONE D" in tradeoff["recommendation"]


def test_operational_route_corridor():
    """Verify route corridor audits geofences and hazards along Mumbai transit."""
    route_c = plan_route_corridor(destination_zone_id="zone-c")
    assert route_c.destination_zone_id == "zone-c"
    assert route_c.corridor_status == "SAFE_TRANSIT_CORRIDOR"
    assert not route_c.has_geofence_conflict
    assert len(route_c.waypoints) >= 3

    route_b = plan_route_corridor(destination_zone_id="zone-b")
    assert route_b.corridor_status == "RESTRICTED_CORRIDOR"
    assert route_b.has_geofence_conflict


def test_api_decision_endpoints():
    """Verify FastAPI decision routes."""
    res_rank = client.get("/api/decision/rank")
    assert res_rank.status_code == 200
    data = res_rank.json()
    assert data["top_candidate"]["code"] == "ZONE C"
    assert len(data["ranked_candidates"]) >= 2

    res_zone = client.get("/api/decision/zone-c")
    assert res_zone.status_code == 200
    assert res_zone.json()["zone_id"] == "zone-c"

    res_tradeoff = client.get("/api/decision/tradeoff/compare?zone_a=zone-c&zone_b=zone-d")
    assert res_tradeoff.status_code == 200

    res_route = client.post("/api/decision/route", json={"destination_zone_id": "zone-c"})
    assert res_route.status_code == 200
    assert "waypoints" in res_route.json()
