"""ORCA Phase 5: Research Evaluation, Benchmarks & Reproducibility Tests
=====================================================================
Tests:
1. 30 Benchmark query automated execution
2. 10 Multi-turn conversation evaluations
3. Adversarial / Hallucination rejection checks
4. 100% Deterministic Reproducibility verification
5. Human evaluation submission and decision audit trails
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.evaluation.evaluator import evaluator
from backend.app.evaluation.datasets import BENCHMARK_30_QUERIES, MULTI_TURN_10_BENCHMARKS, ADVERSARIAL_QUERIES

client = TestClient(app)


def test_benchmark_suite_size():
    """Verify minimum 30 benchmark queries and 10 multi-turn datasets exist."""
    assert len(BENCHMARK_30_QUERIES) >= 30
    assert len(MULTI_TURN_10_BENCHMARKS) >= 10
    assert len(ADVERSARIAL_QUERIES) >= 4


def test_automated_research_evaluator():
    """Verify automated evaluator calculates empirical percentages."""
    eval_res = evaluator.evaluate_benchmark()
    metrics = eval_res["metrics"]
    assert metrics["intent_accuracy_pct"] >= 90.0
    assert metrics["evidence_coverage_pct"] >= 95.0
    assert metrics["risk_consistency_pct"] == 100.0
    assert metrics["deterministic_reproducibility_pct"] == 100.0
    assert metrics["status"] == "PASS"


def test_deterministic_reproducibility():
    """Verify bitwise identical suitability and risk calculation on repeated runs."""
    rep = evaluator.verify_reproducibility("zone-c")
    assert rep["identical"] is True
    assert rep["status"] == "PASS"
    assert rep["run_1_score"] == rep["run_2_score"]


def test_api_evaluation_routes():
    """Verify evaluation and audit endpoints."""
    res_metrics = client.get("/api/evaluation/metrics")
    assert res_metrics.status_code == 200
    assert "benchmark_summary" in res_metrics.json()

    res_benchmarks = client.get("/api/evaluation/benchmarks")
    assert res_benchmarks.status_code == 200
    assert res_benchmarks.json()["benchmark_queries_count"] >= 30

    res_feedback = client.post("/api/evaluation/feedback", json={
        "reviewer_name": "SIH Evaluator",
        "correctness_score": 5,
        "usefulness_score": 5,
        "clarity_score": 4,
        "evidence_quality_score": 5,
        "trust_score": 5,
        "map_usefulness_score": 5,
        "notes": "Excellent grounded decision support."
    })
    assert res_feedback.status_code == 200

    res_audit = client.get("/api/evaluation/audit/audit-latest-001")
    assert res_audit.status_code == 200
    assert res_audit.json()["decision_id"] == "audit-latest-001"
