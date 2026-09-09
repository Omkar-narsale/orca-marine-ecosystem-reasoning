"""
Integration & Regression Test Suite for ORCA Conversational Marine Intelligence.
Tests all 8 canonical user intent queries and multi-turn conversational follow-up sequences.
"""

import pytest
import asyncio
from backend.app.schemas.agentic import QueryIntent, ResponseType, ConversationContext
from backend.app.agents.planner_agent import planner_agent
from backend.app.agents.context_resolver import context_resolver
from backend.app.agents.orchestrator import orchestrator, SESSION_CONTEXT_CACHE

# ---------------------------------------------------------
# 1. TEST ALL 8 CANONICAL INTENT CLASSIFICATIONS
# ---------------------------------------------------------

def test_q1_pfz_discovery_intent():
    """Q1: 'Where is the nearest Potential Fishing Zone today?' -> PFZ_DISCOVERY"""
    q = "Where is the nearest Potential Fishing Zone today?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("PFZ_DISCOVERY", QueryIntent.PFZ_DISCOVERY.value)
    assert "PFZ_ADVISORY" in plan.parsed_intent.parameters

def test_q2_marine_safety_intent():
    """Q2: 'Is it safe to venture into the sea tomorrow morning?' -> MARINE_SAFETY"""
    q = "Is it safe to venture into the sea tomorrow morning?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("MARINE_SAFETY", QueryIntent.MARINE_SAFETY.value)
    assert "WAVE_FORECAST" in plan.parsed_intent.parameters

def test_q3_marine_conditions_intent():
    """Q3: 'What are the tide, weather, and sea conditions near my fishing location?' -> MARINE_CONDITIONS"""
    q = "What are the tide, weather, and sea conditions near my fishing location?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("MARINE_CONDITIONS", QueryIntent.MARINE_CONDITIONS.value)
    assert "TIDE" in plan.parsed_intent.parameters or "WAVE_HEIGHT" in plan.parsed_intent.parameters

def test_q4_hazard_alert_intent():
    """Q4: 'Are there any lightning or cyclone alerts in my area?' -> HAZARD_ALERT"""
    q = "Are there any lightning or cyclone alerts in my area?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("HAZARD_ALERT", QueryIntent.HAZARD_ALERT.value)
    assert "IMD_NOWCAST" in plan.parsed_intent.parameters or "IMD_CYCLONE_TRACK" in plan.parsed_intent.parameters

def test_q5_productivity_search_intent():
    """Q5: 'Which regions show high chlorophyll concentration and favourable sea surface temperature?' -> PRODUCTIVITY_SEARCH"""
    q = "Which regions show high chlorophyll concentration and favourable sea surface temperature?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("PRODUCTIVITY_SEARCH", QueryIntent.PRODUCTIVITY_SEARCH.value)
    assert "CHLOROPHYLL" in plan.parsed_intent.parameters

def test_q6_route_planning_intent():
    """Q6: 'What is the safest route for a fishing vessel considering weather and sea-state conditions?' -> ROUTE_PLANNING"""
    q = "What is the safest route for a fishing vessel considering weather and sea-state conditions?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("ROUTE_PLANNING", QueryIntent.ROUTE_PLANNING.value)
    assert "GIS_ROUTE" in plan.parsed_intent.parameters

def test_q7_productivity_analysis_intent():
    """Q7: 'Why has fish productivity declined in a particular coastal region?' -> PRODUCTIVITY_ANALYSIS"""
    q = "Why has fish productivity declined in a particular coastal region?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("PRODUCTIVITY_ANALYSIS", QueryIntent.PRODUCTIVITY_ANALYSIS.value)
    assert "HISTORICAL_CHLOROPHYLL" in plan.parsed_intent.parameters

def test_q8_risk_avoidance_intent():
    """Q8: 'Which fishing zones should be avoided due to hazardous marine conditions or geofencing restrictions?' -> RISK_AVOIDANCE"""
    q = "Which fishing zones should be avoided due to hazardous marine conditions or geofencing restrictions?"
    plan = planner_agent.plan(q)
    assert plan.intent in ("RISK_AVOIDANCE", QueryIntent.RISK_AVOIDANCE.value)
    assert "WAVE_HAZARDS" in plan.parsed_intent.parameters or "NAVAL_GEOFENCES" in plan.parsed_intent.parameters

# ---------------------------------------------------------
# 2. END-TO-END ORCHESTRATOR EXECUTION FOR CANONICAL QUERIES
# ---------------------------------------------------------

@pytest.mark.anyio
async def test_e2e_pfz_discovery():
    """Tests PFZ query produces PFZ_RESULTS with advisory locations and offshore distances."""
    res = await orchestrator.run(query="Where is the nearest Potential Fishing Zone today?", session_id="test_pfz_session")
    assert res.response_type == ResponseType.PFZ_RESULTS.value
    assert len(res.results) > 0
    assert "km offshore" in res.answer or "PFZ" in res.answer
    assert res.map.get("show_map") is True
    assert len(res.why_reasons) > 0

@pytest.mark.anyio
async def test_e2e_marine_conditions():
    """Tests marine conditions query returns structured weather/wave/tide telemetry."""
    res = await orchestrator.run(query="What are the tide, weather, and sea conditions near my fishing location?", session_id="test_cond_session")
    assert res.response_type == ResponseType.MARINE_CONDITIONS.value
    assert "conditions" in res.data
    conds = res.data["conditions"]
    assert "wave_height_m" in conds
    assert "wind_speed_kts" in conds
    assert "tide_summary" in conds

@pytest.mark.anyio
async def test_e2e_hazard_alerts():
    """Tests hazard query returns active alerts or explicit negative confirmation."""
    res = await orchestrator.run(query="Are there any lightning or cyclone alerts in my area?", session_id="test_haz_session")
    assert res.response_type == ResponseType.HAZARD_ALERT.value
    assert "No active official alert was found" in res.answer or len(res.data.get("alerts", [])) > 0
    assert "No danger exists" not in res.answer

@pytest.mark.anyio
async def test_e2e_route_planning():
    """Tests route query returns route options and navigation explanations."""
    res = await orchestrator.run(query="What is the safest route for a fishing vessel considering weather and sea-state conditions?", session_id="test_route_session")
    assert res.response_type == ResponseType.ROUTE_RESULT.value
    assert len(res.results) >= 2
    assert any(r["is_recommended"] for r in res.results)
    assert res.map.get("show_map") is True

@pytest.mark.anyio
async def test_e2e_productivity_analysis():
    """Tests productivity analysis returns scientific time series trends."""
    res = await orchestrator.run(query="Why has fish productivity declined in a particular coastal region?", session_id="test_prod_ana_session")
    assert res.response_type == ResponseType.PRODUCTIVITY_ANALYSIS.value
    assert "timeseries" in res.data
    assert "contributing_factors" in res.data
    assert len(res.data["timeseries"]) > 0

# ---------------------------------------------------------
# 3. MULTI-TURN CONVERSATIONAL SEQUENCE
# ---------------------------------------------------------

@pytest.mark.anyio
async def test_multiturn_conversational_flow():
    """
    Tests 5-turn conversational sequence:
    Turn 1: 'Is it safe to go fishing tomorrow?'
    Turn 2: 'What about the waves?'
    Turn 3: 'And the wind?'
    Turn 4: 'Find me a better area.'
    Turn 5: 'Closer to shore.'
    """
    session = "multi_turn_flow_session_01"
    
    # Turn 1
    t1 = await orchestrator.run("Is it safe to go fishing tomorrow?", session_id=session)
    assert t1.response_type in (ResponseType.SAFETY_ASSESSMENT.value, "SAFETY_ASSESSMENT")
    
    # Turn 2: Follow-up on waves
    t2 = await orchestrator.run("What about the waves?", session_id=session)
    assert t2.response_type == ResponseType.MARINE_CONDITIONS.value
    assert "wave" in t2.answer.lower()
    
    # Turn 3: Follow-up on wind
    t3 = await orchestrator.run("And the wind?", session_id=session)
    assert t3.response_type == ResponseType.MARINE_CONDITIONS.value
    assert "wind" in t3.answer.lower()
    
    # Turn 4: Switch to candidate search
    t4 = await orchestrator.run("Find me a better area.", session_id=session)
    assert t4.response_type == ResponseType.PRODUCTIVITY_RESULTS.value
    assert len(t4.results) > 0
    
    # Turn 5: Proximity constraint
    t5 = await orchestrator.run("Closer to shore.", session_id=session)
    assert t5.response_type == ResponseType.PRODUCTIVITY_RESULTS.value
    assert "PROXIMITY_TO_SHORE" in t5.follow_up_context.get("active_constraints", [])
