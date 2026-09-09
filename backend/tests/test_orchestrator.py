import pytest
import asyncio
from backend.app.agents.orchestrator import orchestrator
from backend.app.schemas.agentic import ConversationContext

def test_orchestrator_primary_query(mock_pipeline_data):
    response = asyncio.run(orchestrator.run("Which fishing zones should be avoided tomorrow morning?"))
    
    assert response.query == "Which fishing zones should be avoided tomorrow morning?"
    assert response.intent.lower() in ("marine_safety", "risk_avoidance")
    assert len(response.agentTrace) >= 5 # 6 collaborative agent steps
    assert len(response.zonesToAvoid) >= 2
    assert len(response.potentialZones) >= 1
    assert response.confidenceScore >= 70
    assert len(response.evidenceGraph) > 0
    assert response.executionTimeMs > 0

def test_orchestrator_why_zone_a_risky(mock_pipeline_data):
    response = asyncio.run(orchestrator.run("Why is Zone A risky?"))
    assert response.intent == "zone_analysis"
    assert response.focusedZoneId == "zone-a"
    assert len(response.zonesToAvoid) >= 1
    # Check Zone A risk factors
    zone_a = next((z for z in response.all_zones if z["id"] == "zone-a"), None)
    assert zone_a is not None
    assert zone_a["riskScore"] >= 75
    assert len(zone_a["factors"]) >= 2

def test_orchestrator_geofence_query():
    response = asyncio.run(orchestrator.run("Is Zone B restricted?"))
    assert response.intent == "geofence_check"
    assert response.focusedZoneId == "zone-b"
    zone_b = next((z for z in response.all_zones if z["id"] == "zone-b"), None)
    assert zone_b is not None
    assert zone_b["conditions"]["isRestricted"] is True

def test_orchestrator_multiturn_conversation():
    session_id = "test_user_session_101"
    
    # Turn 1
    resp1 = asyncio.run(orchestrator.run("What are the marine conditions near Mumbai tomorrow?", session_id=session_id))
    assert resp1.intent == "marine_safety" or resp1.intent == "marine_forecast"

    # Turn 2 (Contextual follow-up)
    resp2 = asyncio.run(orchestrator.run("What about fishing?", session_id=session_id))
    assert resp2.intent == "fishing_suitability"
    assert "Mumbai" in resp2.location or "Maharashtra" in resp2.location
