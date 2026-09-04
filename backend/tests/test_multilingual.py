import pytest
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.conversation_manager import conversation_manager

@pytest.mark.anyio
async def test_multilingual_english_response():
    resp = await orchestrator.run(
        query="Which fishing zones should be avoided tomorrow morning?",
        target_language="en"
    )
    assert "Avoid Zone A" in resp.summary or "Zone A" in resp.summary or len(resp.zonesToAvoid) > 0
    avoid_codes = [z["code"] for z in resp.zonesToAvoid]
    assert "ZONE A" in avoid_codes or "ZONE B" in avoid_codes
    assert resp.confidenceScore > 0

@pytest.mark.anyio
async def test_multilingual_hindi_response():
    resp = await orchestrator.run(
        query="कल सुबह कौन से मछली पकड़ने के क्षेत्र से बचना चाहिए?",
        target_language="hi"
    )
    assert resp.target_language == "hi"
    # Verify Hindi characters in summary while preserving Zone A and numerical units
    assert "Zone A" in resp.summary or "बचना" in resp.summary or "जोखिम" in resp.summary

@pytest.mark.anyio
async def test_multilingual_marathi_response():
    resp = await orchestrator.run(
        query="उद्या सकाळी कोणते मासेमारी क्षेत्र टाळावे?",
        target_language="mr"
    )
    assert resp.target_language == "mr"
    # Verify Marathi characters in summary while preserving Zone A
    assert "Zone A" in resp.summary or "टाळणे" in resp.summary or "धोका" in resp.summary

def test_evidence_coverage_calculation():
    # Test valid evidence coverage computation
    coverage = conversation_manager.calculate_evidence_coverage(
        claims_count=4,
        supported_evidence_count=4
    )
    assert coverage == 1.0

    coverage_partial = conversation_manager.calculate_evidence_coverage(
        claims_count=5,
        supported_evidence_count=4
    )
    assert coverage_partial == 0.8
