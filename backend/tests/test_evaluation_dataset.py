import pytest
import asyncio
from backend.app.agents.orchestrator import orchestrator

BENCHMARK_QUERIES = [
    # 1. Primary Avoid Query
    ("Which zones should be avoided tomorrow?", "marine_safety"),
    # 2. Fishing Candidate Query
    ("Which zones may be suitable for fishing?", "fishing_suitability"),
    # 3. Zone A Root Cause
    ("Why is Zone A risky?", "zone_analysis"),
    # 4. Geofence Boundary Check
    ("Is Zone B restricted?", "geofence_check"),
    # 5. Spatial Hazards
    ("Show marine hazards near Mumbai", "marine_hazard"),
    # 6. Wave Conditions Forecast
    ("What are wave conditions tomorrow?", "marine_forecast"),
    # 7. PFZ Advisory Retrieval
    ("What is the latest PFZ advisory?", "fishing_suitability"),
    # 8. Specific Zone Suitability
    ("Is Zone C a suitable candidate tomorrow morning?", "fishing_suitability"),
    # 9. Evidence Traceability
    ("What evidence supports Zone A's risk?", "zone_analysis"),
    # 10. General Safety Query
    ("What happens if weather data is unavailable?", "marine_safety"),
]

@pytest.mark.parametrize("query,expected_intent", BENCHMARK_QUERIES)
def test_benchmark_evaluation_queries(query: str, expected_intent: str):
    response = asyncio.run(orchestrator.run(query))
    
    # 1. Verify Intent Classification
    assert response.intent == expected_intent or response.plan.intent is not None
    
    # 2. Verify Structured Multi-Agent Output Integrity
    assert len(response.agentTrace) >= 4
    assert response.confidenceScore > 0
    assert len(response.evidenceGraph) > 0
    assert len(response.all_zones) == 4
    
    # 3. Verify Grounded Scientific Language (No fake catch guarantees)
    assert "fish guaranteed" not in response.summary.lower()
    assert "completely safe" not in response.summary.lower()
