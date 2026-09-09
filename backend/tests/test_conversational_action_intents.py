import pytest
from backend.app.agents.orchestrator import orchestrator
from backend.app.services.state.result_registry import result_registry
from backend.app.schemas.agentic import ActionIntent

pytestmark = pytest.mark.anyio

async def test_scenario_1_route_planning_and_show_on_map():
    """
    Test 1: Route Planning Query -> Follow-up "Show on map"
    Verifies that the follow-up reuses registered entities without re-fetching.
    """
    session_id = "test_sess_route_01"
    result_registry.clear_session(session_id)

    # 1. Primary Query
    res1 = await orchestrator.process_query(
        query_text="I need to travel from Mumbai to an offshore fishing spot tomorrow morning. What is the safest route and what weather should I watch out for?",
        session_id=session_id
    )
    assert res1.response_type in ("ROUTE_RESULT", "route_planning")
    assert len(res1.results) >= 1
    primary_route = res1.results[0]
    assert "Inshore Shelf Passage" in primary_route["name"] or "route_01" in primary_route.get("route_id", "")
    assert primary_route["is_recommended"] is True

    # 2. Action Query: "Show it on map"
    res2 = await orchestrator.process_query(
        query_text="Show it on map",
        session_id=session_id
    )
    assert res2.action_intent in ("SHOW_ON_MAP", ActionIntent.SHOW_ON_MAP.value)
    assert len(res2.map_actions) >= 1
    cmd = res2.map_actions[0]
    action_type = cmd.get("action") if isinstance(cmd, dict) else cmd.action
    target_id = cmd.get("target_id") if isinstance(cmd, dict) else cmd.target_id
    assert action_type == "SELECT"
    assert target_id in (primary_route.get("route_id"), primary_route.get("id"), "route_01")
    assert res2.latency_breakdown.get("tool_latency_ms", 0) == 0.0  # Zero re-fetch latency!

async def test_scenario_2_pfz_discovery_and_why():
    """
    Test 2: PFZ Discovery -> Follow-up "Why is this area recommended?"
    Verifies that the follow-up retrieves deterministic reasoning from registry.
    """
    session_id = "test_sess_pfz_02"
    result_registry.clear_session(session_id)

    # 1. Primary Query
    res1 = await orchestrator.process_query(
        query_text="Where is the nearest Potential Fishing Zone today?",
        session_id=session_id
    )
    assert res1.response_type in ("PFZ_RESULTS", "pfz_discovery")
    assert len(res1.results) >= 1
    assert res1.results[0]["distance_km"] > 0
    assert "chlorophyll_mg_m3" in res1.results[0]
    assert "sst_celsius" in res1.results[0]

    # 2. Action Query: "Why?"
    res2 = await orchestrator.process_query(
        query_text="Why is this area recommended?",
        session_id=session_id
    )
    assert res2.action_intent in ("EXPLAIN", ActionIntent.EXPLAIN.value)
    assert "thermal front" in res2.answer.lower() or "chlorophyll" in res2.answer.lower() or "gradient" in res2.answer.lower()
    assert res2.latency_breakdown.get("tool_latency_ms", 0) == 0.0

async def test_scenario_3_comparison_action():
    """
    Test 3: Route Planning -> Follow-up "Compare them"
    Verifies that comparison pair is retrieved from registered results.
    """
    session_id = "test_sess_compare_03"
    result_registry.clear_session(session_id)

    # 1. Primary Query
    await orchestrator.process_query(
        query_text="Plan a vessel route from Mumbai to offshore fishing ground",
        session_id=session_id
    )

    # 2. Action Query: "Compare them"
    res2 = await orchestrator.process_query(
        query_text="Compare them",
        session_id=session_id
    )
    assert res2.action_intent in ("COMPARE", ActionIntent.COMPARE.value)
    assert res2.response_type == "COMPARISON"
    assert "Comparison between" in res2.answer
    assert "Direct Offshore Passage" in res2.answer or "route_02" in res2.answer
    assert len(res2.results) >= 2

async def test_scenario_4_sources_action():
    """
    Test 4: Safety Assessment -> Follow-up "Where did this information come from?"
    Verifies that source explanation lists INCOIS, IMD, etc.
    """
    session_id = "test_sess_sources_04"
    result_registry.clear_session(session_id)

    # 1. Primary Query
    await orchestrator.process_query(
        query_text="Is it safe to venture into the sea tomorrow morning near Ratnagiri?",
        session_id=session_id
    )

    # 2. Action Query: "Where did this information come from?"
    res2 = await orchestrator.process_query(
        query_text="Where did this information come from?",
        session_id=session_id
    )
    assert res2.action_intent in ("SHOW_SOURCES", ActionIntent.SHOW_SOURCES.value)
    assert res2.response_type == "SOURCE_EXPLANATION"
    assert "INCOIS" in res2.answer
    assert "IMD" in res2.answer

async def test_scenario_5_refinement_closer_to_shore():
    """
    Test 5: Productivity Search -> Follow-up "Can you find an option closer to shore?"
    Verifies proximity constraint updates and returns candidate with shorter distance to coast.
    """
    session_id = "test_sess_refine_05"
    result_registry.clear_session(session_id)

    # 1. Primary Query
    res1 = await orchestrator.process_query(
        query_text="Find candidate fishing areas near Ratnagiri",
        session_id=session_id
    )
    assert res1.response_type in ("PRODUCTIVITY_RESULTS", "productivity_search")

    # 2. Refinement Query
    res2 = await orchestrator.process_query(
        query_text="Can you find an option closer to shore?",
        session_id=session_id
    )
    assert res2.response_type in ("PRODUCTIVITY_RESULTS", "productivity_search")
    assert "proximity" in res2.answer.lower() or "closer to shore" in res2.answer.lower() or res2.results[0]["distance_km"] <= 15

async def test_scenario_6_marine_conditions_telemetry():
    """
    Test 6: Marine conditions query returns waves, wind, tide, SST with source provenance.
    """
    session_id = "test_sess_cond_06"
    result_registry.clear_session(session_id)

    res = await orchestrator.process_query(
        query_text="What are the tide, weather, and sea conditions near Mumbai right now?",
        session_id=session_id
    )
    assert res.response_type == "MARINE_CONDITIONS"
    cond = res.data.get("conditions", {})
    assert "wave_height_m" in cond
    assert "wind_speed_kts" in cond
    assert "sea_surface_temp_c" in cond
    assert "tide_summary" in cond
    assert len(res.sources) >= 2

async def test_scenario_7_hazard_alert_no_false_positive():
    """
    Test 7: Hazard alert query returns explicit clean state without fabricating fake storms.
    """
    session_id = "test_sess_haz_07"
    result_registry.clear_session(session_id)

    res = await orchestrator.process_query(
        query_text="Are there any lightning or cyclone alerts for Maharashtra coast?",
        session_id=session_id
    )
    assert res.response_type == "HAZARD_ALERT"
    assert "No active official alert" in res.answer or "normal operational" in res.answer.lower()

async def test_scenario_8_multilingual_continuity():
    """
    Test 8: Multilingual continuity with Marathi query.
    """
    session_id = "test_sess_multi_08"
    result_registry.clear_session(session_id)

    res = await orchestrator.process_query(
        query_text="उद्या सकाळी समुद्रात जाणे सुरक्षित आहे का?",
        session_id=session_id,
        target_language="mr"
    )
    assert res.target_language in ("mr", "marathi")
    assert len(res.answer) > 0
    # Must retain valid status and sources
    assert len(res.sources_consulted) >= 1
