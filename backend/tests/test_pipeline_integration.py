import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.risk.pipeline import run_deterministic_analysis

client = TestClient(app)

def test_full_pipeline_primary_query(mock_pipeline_data):
    """
    Test primary SIH 2026 Phase 2.2 demo query:
    'Which fishing zones should be avoided tomorrow?'
    """
    res = asyncio.run(run_deterministic_analysis("Which fishing zones should be avoided tomorrow?"))
    
    assert res["query"] == "Which fishing zones should be avoided tomorrow?"
    assert len(res["zonesToAvoid"]) >= 1
    assert len(res["potentialZones"]) >= 1

    # Check Zone A in avoid
    zone_a = next((z for z in res["zonesToAvoid"] if z["id"] == "zone-a"), None)
    assert zone_a is not None
    assert zone_a["status"] == "high_risk"
    assert zone_a["riskScore"] >= 75
    assert len(zone_a["factors"]) >= 2

    # Check Zone B in avoid due to geofence
    zone_b = next((z for z in res["zonesToAvoid"] if z["id"] == "zone-b"), None)
    assert zone_b is not None
    assert zone_b["status"] == "restricted"
    assert zone_b["conditions"]["isRestricted"] is True

    # Check Zone C in potential
    zone_c = next((z for z in res["potentialZones"] if z["id"] == "zone-c"), None)
    assert zone_c is not None
    assert zone_c["status"] == "suitable_candidate" or zone_c["status"] == "suitable"
    assert zone_c["riskScore"] < 40

    # Ensure prototype geometry disclaimer is attached
    assert "Prototype" in zone_a["geometry_type"]

def test_api_zones_endpoint():
    response = client.get("/api/zones")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert any(z["zone_id"] == "zone-a" for z in data)
    assert any(z["zone_id"] == "zone-b" for z in data)

def test_api_zones_risk_summary(mock_pipeline_data):
    response = client.get("/api/zones/risk-summary?time_window=tomorrow%20morning")
    assert response.status_code == 200
    data = response.json()
    assert "requested_window" in data
    assert data["total_zones"] == 4
    assert data["avoid_count"] >= 2
    assert data["candidate_count"] >= 1

def test_api_geofences():
    response = client.get("/api/geofences")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_api_marine_hazards():
    response = client.get("/api/marine/hazards")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "hazards" in data

def test_api_marine_suitability():
    response = client.get("/api/marine/suitability")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4

def test_api_query_analyze_post():
    response = client.post("/api/query/analyze", json={"query": "Which fishing zones should be avoided tomorrow?"})
    assert response.status_code == 200
    data = response.json()
    assert "zonesToAvoid" in data
    assert "potentialZones" in data
    assert "summary" in data
