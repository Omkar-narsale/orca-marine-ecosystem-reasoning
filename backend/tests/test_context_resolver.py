import pytest
from backend.app.agents.context_resolver import context_resolver
from backend.app.schemas.agentic import ConversationContext

def test_resolve_map_commands():
    res1 = context_resolver.resolve_context("Show risky zones")
    assert res1["is_map_command"] is True
    assert res1["filter_mode"] == "hazards"

    res2 = context_resolver.resolve_context("Show suitable candidates")
    assert res2["is_map_command"] is True
    assert res2["filter_mode"] == "safe"

    res3 = context_resolver.resolve_context("Show restricted areas")
    assert res3["is_map_command"] is True
    assert res3["filter_mode"] == "restricted"

    res4 = context_resolver.resolve_context("Zoom to Zone A")
    assert res4["is_map_command"] is True
    assert res4["resolved_zone_id"] == "zone-a"

def test_resolve_why_follow_up():
    ctx = ConversationContext(
        conversation_id="test_sess",
        previous_query="Which zones should be avoided tomorrow morning?",
        previous_intent="marine_safety",
        active_zone_id="zone-a",
        time_window="Tomorrow Morning",
        location="Maharashtra Coastal Region"
    )

    res = context_resolver.resolve_context("Why?", context=ctx)
    assert res["resolved_intent"] == "zone_analysis"
    assert res["resolved_zone_id"] == "zone-a"

def test_resolve_zone_switch_follow_up():
    ctx = ConversationContext(
        conversation_id="test_sess",
        previous_query="Which zones should be avoided tomorrow morning?",
        previous_intent="marine_safety",
        active_zone_id="zone-a",
        time_window="Tomorrow Morning",
        location="Maharashtra Coastal Region"
    )

    res = context_resolver.resolve_context("What about Zone C?", context=ctx)
    assert res["resolved_zone_id"] == "zone-c"

def test_resolve_temporal_shift_follow_up():
    ctx = ConversationContext(
        conversation_id="test_sess",
        previous_query="Which zones should be avoided tomorrow morning?",
        previous_intent="marine_safety",
        active_zone_id="zone-a",
        time_window="Tomorrow Morning",
        location="Maharashtra Coastal Region"
    )

    res = context_resolver.resolve_context("What about tomorrow evening?", context=ctx)
    assert res["time_changed"] is True
    assert res["new_time_query"] == "What about tomorrow evening?"

def test_resolve_source_inquiry():
    ctx = ConversationContext(
        conversation_id="test_sess",
        previous_query="Why is Zone A risky?",
        previous_intent="zone_analysis",
        active_zone_id="zone-a"
    )

    res = context_resolver.resolve_context("Which source says that?", context=ctx)
    assert res["is_source_query"] is True
    assert res["resolved_intent"] == "source_evidence"
    assert res["resolved_zone_id"] == "zone-a"

def test_resolve_risk_comparison():
    res = context_resolver.resolve_context("Compare Zone A and Zone C")
    assert res["resolved_intent"] == "risk_comparison"
    assert "zone-a" in res["resolved_compare_zone_ids"]
    assert "zone-c" in res["resolved_compare_zone_ids"]
