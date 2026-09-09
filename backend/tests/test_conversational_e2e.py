import pytest
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.conversation_manager import conversation_manager

@pytest.mark.anyio
async def test_e2e_conversational_flow_1_avoidance_and_why():
    """TEST 1: Avoidance inquiry followed by 'Why?' preserves context."""
    session_id = "test_e2e_avoid_why"
    
    # Turn 1
    resp1 = await orchestrator.run(
        query="Which fishing zones should I avoid tomorrow morning?",
        session_id=session_id,
        target_language="en"
    )
    assert resp1 is not None
    avoid_ids = [z["id"] for z in resp1.zonesToAvoid]
    assert "zone-a" in avoid_ids or "zone-b" in avoid_ids
    
    # Turn 2: Follow-up 'Why?'
    resp2 = await orchestrator.run(
        query="Why?",
        session_id=session_id,
        target_language="en"
    )
    assert resp2 is not None
    assert len(resp2.summary) > 0
    # Should explain avoidance rationale for previously avoided zone
    assert "Zone A" in resp2.summary or "Zone B" in resp2.summary or "risk" in resp2.summary.lower()

@pytest.mark.anyio
async def test_e2e_conversational_flow_2_compare_and_extend():
    """TEST 2: Compare Zone A and C, then inquire about Zone D."""
    session_id = "test_e2e_compare_extend"
    
    # Turn 1: Compare A and C
    resp1 = await orchestrator.run(
        query="Compare Zone A and Zone C.",
        session_id=session_id,
        target_language="en"
    )
    assert resp1 is not None
    assert "Zone A" in resp1.summary and "Zone C" in resp1.summary
    
    # Turn 2: What about Zone D?
    resp2 = await orchestrator.run(
        query="What about Zone D?",
        session_id=session_id,
        target_language="en"
    )
    assert resp2 is not None
    assert "Zone D" in resp2.summary or resp2.focusedZoneId == "zone-d"

@pytest.mark.anyio
async def test_e2e_conversational_flow_3_candidate_exclusion():
    """TEST 3: Find fishing candidate, then ask for another option."""
    session_id = "test_e2e_candidate_exclusion"
    
    # Turn 1: Candidate search
    resp1 = await orchestrator.run(
        query="Find a fishing candidate.",
        session_id=session_id,
        target_language="en"
    )
    assert resp1 is not None
    assert len(resp1.potentialZones) > 0
    top_candidate_1 = resp1.potentialZones[0]["id"]
    
    # Turn 2: Another option
    resp2 = await orchestrator.run(
        query="Give me another one.",
        session_id=session_id,
        target_language="en"
    )
    assert resp2 is not None
    # Candidate list should exclude or re-rank away from top_candidate_1
    if len(resp2.potentialZones) > 0:
        assert resp2.potentialZones[0]["id"] != top_candidate_1 or resp2.focusedZoneId != top_candidate_1

@pytest.mark.anyio
async def test_e2e_conversational_flow_4_proximity_rerank():
    """TEST 4: Near-shore candidate query re-ranks by distanceCoastKm."""
    session_id = "test_e2e_proximity"
    
    resp = await orchestrator.run(
        query="Find something closer to shore.",
        session_id=session_id,
        target_language="en"
    )
    assert resp is not None
    assert resp.filterMode in ("safe", "all")
    if len(resp.potentialZones) > 1:
        dists = [z.get("distanceCoastKm", 999) for z in resp.potentialZones]
        assert dists == sorted(dists)

@pytest.mark.anyio
async def test_e2e_conversational_flow_5_restricted_zones():
    """TEST 5: Restriction query isolates geofenced zones."""
    session_id = "test_e2e_restricted"
    
    resp = await orchestrator.run(
        query="Show restricted zones.",
        session_id=session_id,
        target_language="en"
    )
    assert resp is not None
    assert resp.filterMode == "restricted"
    assert resp.focusedZoneId == "zone-b"

@pytest.mark.anyio
async def test_e2e_conversational_flow_6_weather_then_wind():
    """TEST 6: 'What are the waves?' then 'What about wind?' preserves context."""
    session_id = "test_e2e_weather_wind"
    
    # Turn 1: Waves
    resp1 = await orchestrator.run(
        query="What are the waves tomorrow?",
        session_id=session_id,
        target_language="en"
    )
    assert resp1 is not None
    
    # Turn 2: Wind
    resp2 = await orchestrator.run(
        query="What about wind?",
        session_id=session_id,
        target_language="en"
    )
    assert resp2 is not None
    assert resp2.location == resp1.location

@pytest.mark.anyio
async def test_e2e_conversational_flow_7_new_chat_state_isolation():
    """TEST 7: New chat session produces independent isolated state."""
    session_1 = "test_e2e_session_A"
    session_2 = "test_e2e_session_B"
    
    await orchestrator.run(query="Why should I avoid Zone A?", session_id=session_1)
    hist1 = conversation_manager.get_conversation_history(session_1)
    assert len(hist1) >= 2
    
    hist2 = conversation_manager.get_conversation_history(session_2)
    assert len(hist2) == 0

@pytest.mark.anyio
async def test_e2e_conversational_flow_8_hindi_multilingual():
    """TEST 8: Hindi query and Hindi follow-up produce Hindi responses."""
    session_id = "test_e2e_hindi"
    
    resp1 = await orchestrator.run(
        query="कल सुबह कौन से मछली पकड़ने के क्षेत्र से बचना चाहिए?",
        session_id=session_id,
        target_language="hi"
    )
    assert resp1 is not None
    assert resp1.target_language == "hi"
    assert any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in resp1.summary)
    
    resp2 = await orchestrator.run(
        query="जोन ए से क्यों बचें?",
        session_id=session_id,
        target_language="hi"
    )
    assert resp2 is not None
    assert any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in resp2.summary)

@pytest.mark.anyio
async def test_e2e_conversational_flow_9_marathi_multilingual():
    """TEST 9: Marathi query and follow-up produce Marathi responses."""
    session_id = "test_e2e_marathi"
    
    resp1 = await orchestrator.run(
        query="उद्या सकाळी कोणते मासेमारी क्षेत्र टाळावे?",
        session_id=session_id,
        target_language="mr"
    )
    assert resp1 is not None
    assert resp1.target_language == "mr"
    assert any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in resp1.summary)

@pytest.mark.anyio
async def test_e2e_conversational_flow_10_no_false_safety_guarantees():
    """TEST 10: 'Is Zone C safe?' never returns guaranteed safety claim."""
    session_id = "test_e2e_safety_check"
    
    resp = await orchestrator.run(
        query="Is Zone C safe?",
        session_id=session_id,
        target_language="en"
    )
    assert resp is not None
    summary_lower = resp.summary.lower()
    assert "guarantee" not in summary_lower or "not a guarantee" in summary_lower or "candidate" in summary_lower or "subject to" in summary_lower
    # Must NOT claim absolute guarantee
    assert "guaranteed safe" not in summary_lower
    assert "100% safe" not in summary_lower
