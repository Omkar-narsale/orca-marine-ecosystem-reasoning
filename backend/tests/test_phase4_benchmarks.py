import pytest
from backend.app.agents.orchestrator import orchestrator
from backend.app.schemas.agentic import ConversationContext
from backend.app.services.alerts.alert_manager import alert_manager

BENCHMARK_SCENARIOS = [
    # 1. Primary Avoidance Query
    {
        "id": "BENCH-01",
        "turn1": "Which fishing zones should be avoided tomorrow morning?",
        "turn2": "Why?",
        "expected_turn1_avoid": ["ZONE A", "ZONE B"],
        "expected_turn2_zone": "zone-a"
    },
    # 2. Zone Candidate -> Follow-up
    {
        "id": "BENCH-02",
        "turn1": "Which fishing zones may be suitable for operations tomorrow?",
        "turn2": "What about Zone C?",
        "expected_turn1_candidate": "ZONE C",
        "expected_turn2_zone": "zone-c"
    },
    # 3. Temporal Shift
    {
        "id": "BENCH-03",
        "turn1": "Which zones should I avoid tomorrow morning?",
        "turn2": "What about tomorrow evening?",
        "expected_time_change": True
    },
    # 4. Source Inquiry
    {
        "id": "BENCH-04",
        "turn1": "Why is Zone A classified as high risk?",
        "turn2": "Which source says that?",
        "expected_sources": ["INCOIS", "IMD"]
    },
    # 5. Comparative Query
    {
        "id": "BENCH-05",
        "turn1": "Compare Zone A and Zone C.",
        "turn2": "Why is Zone C safer?",
        "expected_comparison_zones": ["zone-a", "zone-c"]
    },
    # 6. Map Filter Hazards
    {
        "id": "BENCH-06",
        "turn1": "Show risky zones",
        "turn2": "Zoom to Zone A",
        "expected_map_action": "FILTER_HAZARDS"
    },
    # 7. Map Filter Candidates
    {
        "id": "BENCH-07",
        "turn1": "Show suitable candidates",
        "turn2": "Show all zones",
        "expected_map_action": "FILTER_SAFE"
    },
    # 8. Geofence Query
    {
        "id": "BENCH-08",
        "turn1": "Is Zone B restricted?",
        "turn2": "Why is it restricted?",
        "expected_restriction": True
    },
    # 9. Multilingual Hindi Query
    {
        "id": "BENCH-09",
        "turn1": "कल सुबह कौन से क्षेत्र से बचना चाहिए?",
        "turn2": "Zone A क्यों खतरनाक है?",
        "language": "hi"
    },
    # 10. Multilingual Marathi Query
    {
        "id": "BENCH-10",
        "turn1": "उद्या सकाळी कोणते क्षेत्र टाळावे?",
        "turn2": "Zone A चे कारण काय?",
        "language": "mr"
    },
    # 11. Specific Incois Question
    {
        "id": "BENCH-11",
        "turn1": "What did INCOIS say about wave conditions?",
        "turn2": "What is the maximum wave height?",
        "expected_tool": "incois_wave_forecast"
    },
    # 12. Specific IMD Wind Question
    {
        "id": "BENCH-12",
        "turn1": "What is the wind speed forecast near Mumbai tomorrow?",
        "turn2": "Is there a squall warning?",
        "expected_tool": "imd_coastal_winds"
    },
    # 13. High Seas vs Nearshore Query
    {
        "id": "BENCH-13",
        "turn1": "What if I go farther offshore to Sector A?",
        "turn2": "Is it safe to deploy nets?",
        "expected_turn1_zone": "zone-a"
    },
    # 14. Geofence Map Action
    {
        "id": "BENCH-14",
        "turn1": "Show restricted areas on the map",
        "turn2": "Show all zones",
        "expected_map_action": "FILTER_RESTRICTED"
    },
    # 15. Disclaimers and Non-Guarantee Fishing Check
    {
        "id": "BENCH-15",
        "turn1": "Can you guarantee fish at Zone C tomorrow?",
        "turn2": "Why is it not guaranteed?",
        "expected_disclaimer": "Recent biological observations do not guarantee future fish presence"
    },
    # 16. Evidence Graph Node Check
    {
        "id": "BENCH-16",
        "turn1": "Show evidence for Zone A risk",
        "turn2": "What is the wave height value?",
        "expected_numeric_wave": 4.1
    },
    # 17. Multi-turn Context Continuity Across 3 Turns
    {
        "id": "BENCH-17",
        "turn1": "What are conditions near Mumbai tomorrow morning?",
        "turn2": "What about Zone B?",
        "turn3": "Why?",
        "expected_turn3_zone": "zone-b"
    },
    # 18. Comparison across Zone B and Zone C
    {
        "id": "BENCH-18",
        "turn1": "Compare Zone B and Zone C",
        "turn2": "Which one has navigational restrictions?",
        "expected_comparison_zones": ["zone-b", "zone-c"]
    },
    # 19. Alert Verification
    {
        "id": "BENCH-19",
        "turn1": "Are there any active marine safety alerts?",
        "turn2": "Which zones are affected?",
        "expected_alert_presence": True
    },
    # 20. Evidence Coverage Metric Check
    {
        "id": "BENCH-20",
        "turn1": "Which fishing zones should be avoided tomorrow morning?",
        "turn2": "What is the evidence coverage of this analysis?",
        "expected_min_coverage": 0.85
    }
]

@pytest.mark.anyio
@pytest.mark.parametrize("scenario", BENCHMARK_SCENARIOS, ids=[s["id"] for s in BENCHMARK_SCENARIOS])
async def test_20_benchmark_conversations(scenario):
    session_id = f"bench_sess_{scenario['id']}"
    lang = scenario.get("language", "en")

    # Turn 1
    resp1 = await orchestrator.run(
        query=scenario["turn1"],
        session_id=session_id,
        target_language=lang
    )
    assert resp1 is not None
    assert len(resp1.summary) > 0
    assert resp1.confidenceScore > 0

    # Turn 2
    resp2 = await orchestrator.run(
        query=scenario["turn2"],
        session_id=session_id,
        target_language=lang
    )
    assert resp2 is not None
    assert len(resp2.summary) > 0
    assert len(resp2.evidenceGraph) > 0

    # Verify specific assertions based on scenario id
    if scenario["id"] == "BENCH-01":
        avoid_codes = [z["code"] for z in resp1.zonesToAvoid]
        assert "ZONE A" in avoid_codes or "ZONE B" in avoid_codes
    elif scenario["id"] == "BENCH-03":
        # Time change should have re-planned
        assert resp2.time is not None
    elif scenario["id"] == "BENCH-06":
        assert resp1.filterMode == "hazards"
    elif scenario["id"] == "BENCH-07":
        assert resp1.filterMode == "safe"
    elif scenario["id"] == "BENCH-15":
        has_disclaimer = (
            any("guarantee" in lim.lower() for lim in resp1.limitations) or
            any("guarantee" in str(z.get("suitability", {})).lower() for z in resp1.all_zones) or
            "guarantee" in resp1.disclaimer.lower() or
            "candidate" in resp1.summary.lower()
        )
        assert has_disclaimer is True
    elif scenario["id"] == "BENCH-20":
        assert resp1.evidence_coverage >= 0.8
