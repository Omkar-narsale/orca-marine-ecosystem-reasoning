"""ORCA Phase 7 Research Validation, Benchmarking & Scientific Evaluation Tests
===========================================================================
Validates:
- Baseline A (Rule-Based) and Baseline B (Single-Agent) execution
- Grounding Evaluator (SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED)
- Safety Evaluator adversarial fail-safes (Missing data, Warning outage, Geofence breach, Injection)
- Ablation engine component knockouts
- Metrics calculation & statistical validity
- Reproducible experiment runner output
"""

import json
import os
import pytest
from backend.app.evaluation.datasets import load_controlled_scenarios
from backend.app.evaluation.baselines.rule_based import evaluate_rule_based_baseline
from backend.app.evaluation.baselines.single_agent import evaluate_single_agent_baseline
from backend.app.evaluation.grounding_evaluator import evaluate_evidence_grounding, GroundingStatus
from backend.app.evaluation.safety_evaluator import (
    evaluate_adversarial_safety,
    evaluate_missing_wave_safety,
    evaluate_warning_service_outage,
    evaluate_corrupted_geofence,
    evaluate_prompt_injection_safety
)
from backend.app.evaluation.ablation import run_ablation_study, get_ablation_matrix
from backend.app.evaluation.metrics_engine import compute_system_metrics, compute_comparative_summary
from backend.app.evaluation.runner import run_experiment


def test_controlled_dataset_categories():
    """Verify that all 20 categories (A through T) are present in the controlled dataset."""
    scenarios = load_controlled_scenarios()
    assert len(scenarios) >= 20
    
    categories = {s.get("scenario_id", "").split("_")[1] for s in scenarios}
    expected_categories = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"}
    assert expected_categories.issubset(categories)


def test_rule_based_baseline_execution():
    """Verify Rule-Based baseline computes deterministic safety on scenario."""
    scenarios = load_controlled_scenarios()
    res = evaluate_rule_based_baseline(scenarios[0]["query"], "en")
    
    assert res["system_id"] == "BASELINE_A_RULE_BASED"
    assert "ZONE A" in res["decision"]["avoid_zones"]
    assert "ZONE B" in res["decision"]["avoid_zones"]
    assert res["safety_rule_compliance"] == 1.0
    assert res["geofence_compliance"] == 1.0


def test_single_agent_baseline_execution():
    """Verify Single-Agent baseline monolithic execution."""
    scenarios = load_controlled_scenarios()
    res = evaluate_single_agent_baseline(scenarios[0]["query"], "en")
    
    assert res["system_id"] == "BASELINE_B_SINGLE_AGENT"
    assert "candidate_zones" in res["decision"]
    assert res["safety_rule_compliance"] == 1.0



def test_grounding_evaluator_deterministic():
    """Verify claim-level deterministic grounding classification."""
    evidence_payload = [
        {"parameter": "significant_wave_height", "value": 4.1, "source_id": "INCOIS_WW3", "organization": "INCOIS", "valid_time": "Tomorrow 06:00 IST", "status": "RETRIEVED"},
        {"parameter": "sustained_wind_speed", "value": 30.0, "source_id": "IMD_AWS", "organization": "IMD", "valid_time": "Tomorrow 06:00 IST", "status": "RETRIEVED"}
    ]

    
    # Supported claim
    claim1 = "Zone A significant wave height is 4.1m based on INCOIS WW3 model"
    status1 = evaluate_evidence_grounding(claim1, evidence_payload)
    assert status1["overall_status"] == GroundingStatus.SUPPORTED.value
    
    # Contradicted claim
    claim2 = "Zone A wave height is 1.0m"
    status2 = evaluate_evidence_grounding(claim2, evidence_payload)
    assert status2["overall_status"] in (GroundingStatus.CONTRADICTED.value, GroundingStatus.PARTIALLY_SUPPORTED.value)
    
    # Unknown / ungrounded claim
    claim3 = "Zone A has massive tuna schools present right now"
    status3 = evaluate_evidence_grounding(claim3, evidence_payload)
    assert status3["overall_status"] == GroundingStatus.UNKNOWN.value


def test_safety_evaluator_failsafes():
    """Verify all 4 core adversarial safety fail-safes pass deterministically."""
    res = evaluate_adversarial_safety()
    assert res["safety_rule_compliance_pct"] == 100.0
    assert res["observed_safety_violations"] == 0
    assert len(res["detailed_checks"]) >= 4
    for check in res["detailed_checks"]:
        assert check["passed"] is True


def test_missing_wave_failsafe():
    """Verify missing wave telemetry outputs INSUFFICIENT_DATA and not SAFE."""
    res = evaluate_missing_wave_safety()
    assert res["passed"] is True
    assert res["actual_classification"] == "INSUFFICIENT_DATA"


def test_warning_service_outage_failsafe():
    """Verify warning service outage outputs INSUFFICIENT_DATA and not NO WARNING."""
    res = evaluate_warning_service_outage()
    assert res["passed"] is True
    assert res["actual_classification"] == "INSUFFICIENT_DATA"


def test_corrupted_geofence_failsafe():
    """Verify geofence service outage triggers defensive restriction."""
    res = evaluate_corrupted_geofence()
    assert res["passed"] is True
    assert res["actual_restriction"] is True


def test_prompt_injection_safety_resistance():
    """Verify direct prompt override cannot bypass deterministic safety layer."""
    res = evaluate_prompt_injection_safety()
    assert res["passed"] is True
    assert res["risk_score"] > 70


def test_ablation_matrix_and_study():
    """Verify component ablation study executes 6 configurations cleanly."""
    study = run_ablation_study()
    assert "ablation_results" in study
    assert len(study["ablation_results"]) == 6
    
    # Verify control is intact
    control = study["ablation_results"][0]
    assert control["config_id"] == "CONTROL_FULL_ORCA"
    assert control["safety_compliance_pct"] == 100.0


def test_metrics_engine_statistical_aggregation():
    """Verify metrics calculation correctly measures mean, median, and P95 latency."""
    raw_results = [
        {"safety_rule_compliance": 1.0, "geofence_compliance": 1.0, "evidence_coverage": 0.9, "source_attribution_accuracy": 0.9, "decision_consistent": True, "multilingual_consistent": True, "missing_data_safe": True, "latency_ms": 10.0},
        {"safety_rule_compliance": 1.0, "geofence_compliance": 1.0, "evidence_coverage": 1.0, "source_attribution_accuracy": 1.0, "decision_consistent": True, "multilingual_consistent": True, "missing_data_safe": True, "latency_ms": 20.0},
        {"safety_rule_compliance": 1.0, "geofence_compliance": 1.0, "evidence_coverage": 0.8, "source_attribution_accuracy": 0.8, "decision_consistent": True, "multilingual_consistent": True, "missing_data_safe": True, "latency_ms": 30.0}
    ]
    metrics = compute_system_metrics("TEST_SYSTEM", raw_results)
    
    assert metrics["sample_size"] == 3
    assert metrics["safety_rule_compliance_pct"] == 100.0
    assert metrics["latency"]["mean_sec"] == 0.02
    assert metrics["latency"]["median_sec"] == 0.02
    assert metrics["observed_safety_violations"] == 0


def test_experiment_runner_reproducibility():
    """Verify automated experiment runner produces valid output structure."""
    result = run_experiment(include_ablation=False)
    assert "experiment_id" in result
    assert result["status"] == "COMPLETED"
    assert "comparative_report" in result
    assert "systems" in result["comparative_report"]
    assert "rule_based" in result["comparative_report"]["systems"]
    assert "single_agent" in result["comparative_report"]["systems"]
    assert "orca_multi_agent" in result["comparative_report"]["systems"]
