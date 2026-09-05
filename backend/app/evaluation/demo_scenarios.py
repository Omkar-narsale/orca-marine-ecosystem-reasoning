"""
ORCA Phase 6 Reproducible SIH Demonstration Scenarios.

Predefined benchmark scenarios executing actual scientific data,
recorded inputs, and deterministic rule outcomes.
"""

from typing import List, Dict, Any

DEMO_SCENARIOS = [
    {
        "id": "DEMO_SCENARIO_01",
        "step": 1,
        "title": "General Marine Avoidance & Decision Identification",
        "query": "Which fishing zones should be avoided tomorrow morning?",
        "expected_intent": "marine_safety",
        "expected_avoid_zones": ["ZONE A", "ZONE B"],
        "expected_candidate_zones": ["ZONE C"],
        "expected_primary_hazards": {
            "ZONE A": "Significant wave height (4.1m) and squall warning (31kt)",
            "ZONE B": "Mumbai Harbor Naval Anchorage restricted geofence"
        },
        "expected_risk_classifications": {
            "zone-a": "HIGH_RISK",
            "zone-b": "RESTRICTED",
            "zone-c": "SUITABLE_CANDIDATE",
            "zone-d": "CAUTION"
        }
    },
    {
        "id": "DEMO_SCENARIO_02",
        "step": 2,
        "title": "Zone-Specific Hazard Explanation (Zone A)",
        "query": "Why is Zone A risky?",
        "expected_intent": "marine_hazard",
        "target_zone": "zone-a",
        "expected_factors": ["significant_wave_height", "surface_wind_10m", "marine_warning"],
        "expected_risk_range": (70, 95),
        "expected_status": "HIGH_RISK"
    },
    {
        "id": "DEMO_SCENARIO_03",
        "step": 3,
        "title": "Geospatial Boundary & Cadastral Verification (Zone B)",
        "query": "Is Zone B restricted?",
        "expected_intent": "geofence_check",
        "target_zone": "zone-b",
        "expected_restriction": True,
        "expected_authority": "Indian Navy / Mumbai Port Authority",
        "expected_status": "RESTRICTED"
    },
    {
        "id": "DEMO_SCENARIO_04",
        "step": 4,
        "title": "Fishing Suitability & Top Candidate Zone Identification",
        "query": "Which zone is the best candidate for fishing tomorrow?",
        "expected_intent": "fishing_suitability",
        "top_candidate": "ZONE C",
        "expected_suitability_range": (65, 85),
        "expected_risk_range": (15, 30),
        "expected_status": "SUITABLE_CANDIDATE"
    },
    {
        "id": "DEMO_SCENARIO_05",
        "step": 5,
        "title": "Multi-Zone Trade-Off & Risk Comparison",
        "query": "Compare Zone A and Zone C.",
        "expected_intent": "risk_comparison",
        "compare_zones": ["zone-a", "zone-c"],
        "safer_zone": "zone-c",
        "rationale_keywords": ["wave", "risk", "suitability"]
    },
    {
        "id": "DEMO_SCENARIO_06",
        "step": 6,
        "title": "Sensitivity Modeling & What-If Wave Surge",
        "query": "What happens if wave height increases by 1.5m?",
        "expected_intent": "what_if_scenario",
        "simulation_parameter": "wave_height",
        "delta": 1.5,
        "expected_impact": "Increases operational risk score and degrades suitability"
    },
    {
        "id": "DEMO_SCENARIO_07",
        "step": 7,
        "title": "Statutory Marine Warning Sector Filtering",
        "query": "Which zones are affected by marine warnings?",
        "expected_intent": "marine_hazard",
        "affected_zones": ["ZONE A"],
        "source": "IMD Marine Division"
    },
    {
        "id": "DEMO_SCENARIO_08",
        "step": 8,
        "title": "Navigable & Accessible Candidate Ground Filtering",
        "query": "Show me the safest accessible candidate zones.",
        "expected_intent": "marine_safety",
        "candidate_zones": ["ZONE C", "ZONE D"]
    },
    {
        "id": "DEMO_SCENARIO_09",
        "step": 9,
        "title": "Data Provenance & Source Evidence Audit",
        "query": "Which source supports this recommendation?",
        "expected_intent": "source_evidence",
        "required_sources": ["INCOIS", "IMD", "MOSDAC", "GIS Cadastre"]
    },
    {
        "id": "DEMO_SCENARIO_10",
        "step": 10,
        "title": "Operational Marine Intelligence Brief Generation",
        "query": "Give me a marine brief for tomorrow morning.",
        "expected_intent": "marine_safety",
        "report_type": "marine_brief",
        "disclaimer_required": "This report is decision support, not a guarantee of fish presence, safe navigation, or legal authorization."
    }
]

def get_demo_scenario(scenario_id_or_step: Any) -> Dict[str, Any]:
    """Retrieves a predefined demo scenario by ID or step index."""
    for s in DEMO_SCENARIOS:
        if s["id"] == scenario_id_or_step or s["step"] == scenario_id_or_step:
            return s
    return DEMO_SCENARIOS[0]
