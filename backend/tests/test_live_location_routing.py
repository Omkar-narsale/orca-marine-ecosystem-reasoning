import pytest
from backend.app.agents.planner_agent import planner_agent
from backend.app.schemas.agentic import ConversationContext, LocationPayload

def test_live_location_used_when_near_me_asked():
    # User provides live coordinates for Goa
    live_loc = LocationPayload(
        latitude=15.4989,
        longitude=73.8278,
        accuracy_m=10.0,
        status="AVAILABLE"
    )
    context = ConversationContext(
        conversation_id="test_loc_1",
        live_location=live_loc
    )

    plan = planner_agent.plan("What are the sea conditions near me?", context=context)
    
    assert plan.parsed_intent.location.source == "LIVE_USER_LOCATION"
    assert plan.parsed_intent.location.lat == 15.4989
    assert plan.parsed_intent.location.lon == 73.8278
    assert "Live Device Location" in plan.parsed_intent.location.name
    assert plan.location_assumed is False

def test_explicit_query_location_overrides_live_location():
    # Device is in Goa (15.5°N), but user explicitly asks about Veraval (Gujarat)
    live_loc = LocationPayload(
        latitude=15.4989,
        longitude=73.8278,
        accuracy_m=10.0,
        status="AVAILABLE"
    )
    context = ConversationContext(
        conversation_id="test_loc_2",
        live_location=live_loc
    )

    plan = planner_agent.plan("Is it safe to venture into the sea near Veraval tomorrow morning?", context=context)

    assert plan.parsed_intent.location.source == "EXPLICIT_QUERY"
    assert "Veraval" in plan.parsed_intent.location.name
    assert abs(plan.parsed_intent.location.lat - 20.9) < 0.2

def test_near_me_without_location_prompts_user_without_mumbai_assumption():
    # No live location provided, query is relative ("near me")
    context = ConversationContext(
        conversation_id="test_loc_3",
        live_location=None
    )

    plan = planner_agent.plan("What are the sea conditions near me?", context=context)

    assert plan.parsed_intent.location.source == "PROMPT_REQUIRED"
    assert plan.parsed_intent.location.lat is None
    assert plan.parsed_intent.location.lon is None
    assert plan.assumption_notice is not None
    assert "LOCATION_REQUIRED" in plan.assumption_notice

def test_multi_turn_context_preserves_location():
    # Turn 1: Goa context
    context = ConversationContext(
        conversation_id="test_loc_4",
        location="Goa Coastal Waters (Goa)",
        current_location={"lat": 15.49, "lon": 73.82, "name": "Goa Coastal Region"}
    )

    # Turn 2: Follow-up with no explicit location
    plan = planner_agent.plan("What about tomorrow evening?", context=context)

    assert plan.parsed_intent.location.source == "CONVERSATION_CONTEXT"
    assert plan.parsed_intent.location.lat == 15.49
    assert plan.parsed_intent.location.lon == 73.82
