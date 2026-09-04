"""ORCA Phase 5: What-If Scenario Reasoning Tests
==============================================
Tests:
1. Controlled hypothetical parameter modifications (Wave +m, Wind +kt)
2. Pristine baseline preservation
3. Clear 'SIMULATED SCENARIO' labeling
4. High hazard scenario exclusion override
5. Scenario reset functionality
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.decision.scenario_engine import (
    run_what_if_scenario,
    reset_scenario_baseline,
    ScenarioRunRequest
)

client = TestClient(app)


def test_wave_increase_scenario():
    """Verify +1.0m wave increases risk and reduces suitability."""
    req = ScenarioRunRequest(wave_delta_m=1.0, target_zone_id="zone-c")
    res = run_what_if_scenario(req)
    
    assert res.is_simulation is True
    assert "SIMULATED SCENARIO" in res.scenario_label
    assert res.baseline_comparison.simulated_risk > res.baseline_comparison.baseline_risk
    assert res.baseline_comparison.simulated_suitability <= res.baseline_comparison.baseline_suitability
    assert "+" in res.baseline_comparison.risk_delta


def test_critical_wave_excludes_zone():
    """Verify severe simulated wave (+3.0m) flips zone to EXCLUDED."""
    req = ScenarioRunRequest(wave_delta_m=3.0, target_zone_id="zone-c")
    res = run_what_if_scenario(req)
    assert res.baseline_comparison.simulated_status == "EXCLUDED"
    assert res.baseline_comparison.simulated_risk >= 60.0


def test_scenario_reset_restores_baseline():
    """Verify scenario reset returns pristine baseline state."""
    reset_data = reset_scenario_baseline()
    assert reset_data["status"] == "BASELINE_RESTORED"
    assert len(reset_data["baseline_zones"]) == 4


def test_api_scenario_endpoints():
    """Verify scenario REST endpoints."""
    res_run = client.post("/api/scenario/run", json={"wave_delta_m": 1.0, "target_zone_id": "zone-c"})
    assert res_run.status_code == 200
    data = res_run.json()
    assert data["is_simulation"] is True
    assert "baseline_comparison" in data

    res_reset = client.post("/api/scenario/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["status"] == "BASELINE_RESTORED"
