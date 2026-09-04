"""ORCA Phase 5: Uncertainty & Decomposed Confidence Tests
======================================================
Tests:
1. Decomposed 5-dimension confidence metrics
2. Missing data impact on confidence
3. Confidence vs Uncertainty separation
4. Epistemic and aleatoric uncertainty factors
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.uncertainty.confidence import confidence_engine
from backend.app.services.uncertainty.uncertainty_engine import uncertainty_engine, calculate_zone_uncertainty

client = TestClient(app)


def test_decomposed_confidence_5_dimensions():
    """Verify all 5 confidence dimensions are calculated mathematically."""
    breakdown = confidence_engine.calculate_confidence_breakdown(
        evaluated_zones=[{"id": "zone-a"}, {"id": "zone-b"}, {"id": "zone-c"}, {"id": "zone-d"}],
        evidence_nodes=["wave_height", "wind_speed", "gis_cadastre", "imd_bulletin"],
        forecast_hours=12
    )
    assert breakdown["overall_score"] >= 70
    assert "data_completeness" in breakdown["dimensions"]
    assert "freshness" in breakdown["dimensions"]
    assert "cross_source_agreement" in breakdown["dimensions"]
    assert "spatial_coverage" in breakdown["dimensions"]
    assert "temporal_alignment" in breakdown["dimensions"]


def test_missing_data_degrades_confidence():
    """Verify missing data feeds lower the completeness score."""
    full = confidence_engine.calculate_confidence_breakdown([{"id": "zone-c"}], ["wave", "wind", "gis", "imd"], 12)
    partial = confidence_engine.calculate_confidence_breakdown([{"id": "zone-c"}], ["wave"], 12)
    assert partial["dimensions"]["data_completeness"]["percentage"] < full["dimensions"]["data_completeness"]["percentage"]
    assert partial["overall_score"] < full["overall_score"]


def test_uncertainty_vs_confidence_separation():
    """Verify that confidence and uncertainty are distinct concepts."""
    ua = calculate_zone_uncertainty("zone-c")
    assert ua.confidence.confidence_level in ["High", "Medium", "Low"]
    assert ua.uncertainty_level in ["LOW", "MODERATE", "HIGH"]
    assert "confidence_concept" in ua.scientific_distinction
    assert "uncertainty_concept" in ua.scientific_distinction
    assert len(ua.uncertainty_factors) >= 1


def test_api_uncertainty_routes():
    """Verify FastAPI uncertainty endpoints."""
    res_matrix = client.get("/api/uncertainty/matrix")
    assert res_matrix.status_code == 200
    assert len(res_matrix.json()["matrix"]) >= 4

    res_zone = client.get("/api/uncertainty/zone-c")
    assert res_zone.status_code == 200
    assert res_zone.json()["zone_id"] == "zone-c"
    assert "confidence" in res_zone.json()
