import pytest
import asyncio
from backend.app.agents.planner_agent import planner_agent
from backend.app.agents.ocean_agent import ocean_agent
from backend.app.agents.weather_agent import weather_agent
from backend.app.agents.geospatial_agent import geospatial_agent
from backend.app.agents.risk_agent import risk_agent
from backend.app.agents.synthesis_agent import synthesis_agent
from backend.app.schemas.agentic import ConversationContext

def test_planner_agent_intent_and_tools():
    plan = planner_agent.plan("Which fishing zones should be avoided tomorrow morning?")
    assert plan.intent == "marine_safety"
    assert "ocean" in plan.required_agents
    assert "weather" in plan.required_agents
    assert "geospatial" in plan.required_agents
    assert "get_wave_forecast" in plan.required_tools
    assert "get_coastal_winds" in plan.required_tools
    assert plan.time_window["is_forecast"] is True

def test_planner_agent_geofence_intent():
    plan = planner_agent.plan("Is Zone B restricted by naval anchorage?")
    assert plan.intent == "geofence_check"
    assert "geospatial" in plan.required_agents
    assert "check_zone_geofences" in plan.required_tools

def test_planner_agent_multilingual_marathi():
    plan = planner_agent.plan("उद्या मुंबई जवळ मासेमारीसाठी कोणते क्षेत्र चांगले आहे?")
    assert plan.detected_language == "Marathi"

def test_ocean_agent_execution():
    res = asyncio.run(ocean_agent.run(required_tools=["get_wave_forecast", "get_sst"], bounds={}))
    assert res["status"] == "COMPLETE"
    assert len(res["records"]) > 0
    assert len(res["findings"]) > 0
    assert res["trace_step"].agentName == "Ocean Agent"

def test_weather_agent_execution():
    res = asyncio.run(weather_agent.run(required_tools=["get_coastal_winds", "get_marine_warnings"]))
    assert res["status"] == "COMPLETE"
    assert len(res["records"]) > 0
    assert res["trace_step"].agentName == "Weather & Hazard Agent"

def test_geospatial_agent_execution():
    res = asyncio.run(geospatial_agent.run(required_tools=["check_zone_geofences"], target_zone_id="zone-b"))
    assert res["status"] == "COMPLETE"
    assert res["geofence_evaluations"]["zone-b"]["restricted"] is True

def test_risk_agent_execution():
    ocean_res = asyncio.run(ocean_agent.run(required_tools=["get_wave_forecast"], bounds={}))
    weather_res = asyncio.run(weather_agent.run(required_tools=["get_coastal_winds", "get_marine_warnings"]))
    geo_res = asyncio.run(geospatial_agent.run(required_tools=["check_zone_geofences"]))

    risk_res = asyncio.run(risk_agent.run(
        ocean_records=ocean_res["records"],
        weather_records=weather_res["records"],
        geofence_map=geo_res["geofence_evaluations"]
    ))

    assert risk_res["status"] == "COMPLETE"
    assert len(risk_res["evaluated_zones"]) == 4
    assert len(risk_res["evidence_nodes"]) > 0
    assert risk_res["confidence_score"] >= 60

def test_synthesis_agent_execution():
    plan = planner_agent.plan("Which fishing zones should be avoided tomorrow?")
    ocean_res = asyncio.run(ocean_agent.run(required_tools=["get_wave_forecast"], bounds={}))
    weather_res = asyncio.run(weather_agent.run(required_tools=["get_coastal_winds", "get_marine_warnings"]))
    geo_res = asyncio.run(geospatial_agent.run(required_tools=["check_zone_geofences"]))

    risk_res = asyncio.run(risk_agent.run(
        ocean_records=ocean_res["records"],
        weather_records=weather_res["records"],
        geofence_map=geo_res["geofence_evaluations"],
        time_window=plan.time_window
    ))

    synth_res = asyncio.run(synthesis_agent.synthesize(
        query="Which fishing zones should be avoided tomorrow?",
        plan=plan,
        evaluated_zones=risk_res["evaluated_zones"],
        suitability_results=risk_res["suitability_results"],
        evidence_nodes=risk_res["evidence_nodes"],
        confidence_meta={"score": risk_res["confidence_score"], "level": risk_res["confidence_level"]},
        missing_data_flags=[],
        source_disagreements=[]
    ))

    assert synth_res["status"] == "COMPLETE"
    assert len(synth_res["zonesToAvoid"]) >= 1
    assert len(synth_res["potentialZones"]) >= 1
    assert "ORCA" in synth_res["summary"]
