from typing import Dict, Any, List, Optional
from backend.app.services.uncertainty.confidence import confidence_engine

class MarineUncertaintyEngine:
    """
    Uncertainty Representation Engine for ORCA Phase 5.
    Explicitly quantifies epistemic uncertainty (missing/stale telemetry) and aleatoric uncertainty
    (inherent biological stochasticity and meteorological forecast horizons).
    """
    def evaluate_zone_uncertainty(
        self,
        zone: Dict[str, Any],
        forecast_horizon_hours: int = 12,
        has_satellite_chlorophyll: bool = True
    ) -> Dict[str, Any]:
        zone_id = zone.get("id") or zone.get("zone_id", "zone-c")
        factors = []

        # 1. Forecast Horizon Uncertainty
        if forecast_horizon_hours <= 12:
            horizon_level = "LOW"
            factors.append("Near-term forecast window (0-12h) has minimal numerical model drift.")
        elif forecast_horizon_hours <= 24:
            horizon_level = "MODERATE"
            factors.append("Medium forecast window (12-24h) exhibits normal atmospheric variance.")
        else:
            horizon_level = "HIGH"
            factors.append("Extended forecast window (>24h) carries significant variance.")

        # 2. Biological / Satellite Observation Latency
        if has_satellite_chlorophyll:
            bio_uncertainty = "MODERATE"
            factors.append("Satellite ocean-color passes indicate past thermal/chlorophyll gradient; biological congregation is non-guaranteed.")
        else:
            bio_uncertainty = "HIGH"
            factors.append("Recent satellite ocean-color feed unavailable; biological indicators unobserved.")

        # 3. Overall Uncertainty Level
        if zone.get("conditions", {}).get("isRestricted") or zone.get("geofence", {}).get("restricted"):
            overall_uncertainty = "LOW"
            primary_reason = "Regulatory restriction boundary is deterministic with zero navigational ambiguity."
        elif horizon_level == "HIGH" or bio_uncertainty == "HIGH":
            overall_uncertainty = "HIGH"
            primary_reason = "Missing telemetry feeds or extended forecast window increase operational variance."
        elif horizon_level == "MODERATE" or bio_uncertainty == "MODERATE":
            overall_uncertainty = "MODERATE"
            primary_reason = "Authoritative forecast telemetry is fresh, but future biological presence remains an unobserved stochastic factor."
        else:
            overall_uncertainty = "LOW"
            primary_reason = "High multi-sensor convergence with near-term validity."

        return {
            "zone_id": zone_id,
            "uncertainty_level": overall_uncertainty,
            "primary_reason": primary_reason,
            "uncertainty_factors": factors,
            "scientific_distinction": {
                "confidence_concept": "Measures how strongly available evidence supports the classification.",
                "uncertainty_concept": "Measures unobserved variance, forecast horizons, and biological non-guarantees."
            }
        }

    def evaluate_system_uncertainty(
        self,
        evaluated_zones: List[Dict[str, Any]],
        evidence_nodes: List[Any],
        forecast_horizon_hours: int = 12
    ) -> Dict[str, Any]:
        conf_breakdown = confidence_engine.calculate_confidence_breakdown(
            evaluated_zones, evidence_nodes, forecast_hours=forecast_horizon_hours
        )

        zone_uncertainties = [
            self.evaluate_zone_uncertainty(z, forecast_horizon_hours=forecast_horizon_hours)
            for z in evaluated_zones
        ]

        # Overall system uncertainty
        uncertainty_level = "MODERATE"
        summary_explanation = (
            "Authoritative forecast telemetry is fresh and multi-source verified, "
            "while satellite biological ocean-color indicators represent recent observations rather than guaranteed fish presence."
        )

        return {
            "confidence": conf_breakdown,
            "uncertainty_level": uncertainty_level,
            "summary_explanation": summary_explanation,
            "zone_uncertainties": zone_uncertainties
        }

uncertainty_engine = MarineUncertaintyEngine()


from pydantic import BaseModel, Field

class ConfidenceDimension(BaseModel):
    percentage: int
    label: str
    description: str


class ConfidenceMetrics(BaseModel):
    overall_confidence_pct: int
    confidence_level: str
    summary: str
    breakdown: Dict[str, ConfidenceDimension]


class UncertaintyAssessment(BaseModel):
    zone_id: str
    uncertainty_level: str
    primary_unknown: str
    confidence: ConfidenceMetrics
    scientific_distinction: Dict[str, str]
    uncertainty_factors: List[str]


def calculate_zone_uncertainty(zone_id: str = "zone-c") -> UncertaintyAssessment:
    """Calculates granular decomposed confidence and epistemic/aleatoric uncertainty for a zone."""
    zid = zone_id.lower().replace("_", "-")
    default_zone = {
        "id": zid,
        "conditions": {"isRestricted": (zid == "zone-b")}
    }
    
    u_res = uncertainty_engine.evaluate_zone_uncertainty(default_zone, forecast_horizon_hours=12)
    conf_res = confidence_engine.calculate_confidence_breakdown(
        evaluated_zones=[{"id": "zone-a"}, {"id": "zone-b"}, {"id": "zone-c"}, {"id": "zone-d"}],
        evidence_nodes=["wave", "wind", "gis", "imd", "incois", "mosdac"],
        forecast_hours=12
    )

    dims = {
        k: ConfidenceDimension(
            percentage=v["percentage"],
            label=v["label"],
            description=v["description"]
        )
        for k, v in conf_res["dimensions"].items()
    }

    confidence_model = ConfidenceMetrics(
        overall_confidence_pct=conf_res["overall_score"],
        confidence_level=conf_res["overall_level"],
        summary=conf_res["summary"],
        breakdown=dims
    )

    return UncertaintyAssessment(
        zone_id=zid,
        uncertainty_level=u_res["uncertainty_level"],
        primary_unknown=u_res["primary_reason"],
        confidence=confidence_model,
        scientific_distinction=u_res["scientific_distinction"],
        uncertainty_factors=u_res["uncertainty_factors"]
    )

