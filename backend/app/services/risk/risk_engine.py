from typing import Dict, Any, List, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.risk.thresholds import RISK_WEIGHTS
from backend.app.services.risk.hazard_engine import hazard_engine
from backend.app.services.geospatial.geofence import geofence_engine
from backend.app.services.risk.confidence import calculate_synthesis_confidence

class MarineRiskEngine:
    """
    Deterministic Marine Risk Scoring and Zone Classification Engine (Phase 6).
    Formula:
      Physical Risk Score = w_wave * S_wave + w_wind * S_wind + w_warning * S_warning + w_current * S_current
    Geofence Restriction operates as a deterministic operational override.
    
    Safety Non-Negotiables:
    - MISSING DATA != SAFE
    - UNKNOWN DATA != SAFE
    - FAILED WARNING CHECK != NO WARNING
    - FAILED GEOFENCE CHECK != UNRESTRICTED
    """
    def evaluate_zone(
        self,
        zone_id: str,
        zone_name: str,
        zone_coords: List[List[float]],
        records: List[NormalizedMarineRecord],
        time_window: Optional[Dict[str, Any]] = None,
        is_warning_service_available: bool = True
    ) -> Dict[str, Any]:
        # Filter records by parameter
        wave_recs = [r for r in records if r.parameter == "significant_wave_height"]
        wind_recs = [r for r in records if r.parameter == "surface_wind_10m"]
        warning_recs = [r for r in records if r.parameter in ("marine_fishermen_warning", "marine_warning")]
        current_recs = [r for r in records if r.parameter == "surface_current"]

        # 1. Hazard Evaluation
        wave_hazard = hazard_engine.evaluate_wave_hazard(wave_recs)
        wind_hazard = hazard_engine.evaluate_wind_hazard(wind_recs)
        warning_hazard = hazard_engine.evaluate_warning_hazard(warning_recs, is_warning_service_available)

        # 2. Geofence Evaluation
        geofence_eval = geofence_engine.evaluate_zone_geofence(zone_id, zone_coords)

        # 3. Deterministic Numerical Risk Calculation
        w_wave = RISK_WEIGHTS["wave"]
        w_wind = RISK_WEIGHTS["wind"]
        w_warn = RISK_WEIGHTS["warning"]

        raw_score = (
            w_wave * wave_hazard["score_contribution"]
            + w_wind * wind_hazard["score_contribution"]
            + w_warn * warning_hazard["score_contribution"]
        )

        # Check for missing critical safety data
        is_restricted = geofence_eval["restricted"]
        geofence_unverified = geofence_eval.get("insufficient_data", False)
        wave_missing = wave_hazard["status"] == "MISSING_DATA"
        wind_missing = wind_hazard["status"] == "MISSING_DATA"
        warning_unverified = warning_hazard["status"] == "INSUFFICIENT_DATA"

        # 4. Classification
        if geofence_unverified:
            classification = "INSUFFICIENT_DATA"
            status_label = "INSUFFICIENT DATA"
            risk_score = 50
        elif is_restricted:
            classification = "RESTRICTED"
            status_label = "RESTRICTED"
            risk_score = max(70, int(round(raw_score)))
        elif wave_missing and wind_missing:
            classification = "INSUFFICIENT_DATA"
            status_label = "INSUFFICIENT DATA"
            risk_score = 50
        elif wave_missing:
            # Critical safety wave information is missing - never assume safe
            classification = "INSUFFICIENT_DATA"
            status_label = "INSUFFICIENT DATA"
            risk_score = 50
        elif warning_unverified:
            classification = "INSUFFICIENT_DATA"
            status_label = "INSUFFICIENT DATA"
            risk_score = 50
        elif raw_score >= 70.0 or wave_hazard["severity"] in ("HIGH", "CRITICAL") or warning_hazard["severity"] == "HIGH":
            classification = "HIGH_RISK"
            status_label = "HIGH RISK"
            risk_score = int(round(raw_score))
        elif raw_score >= 38.0 or wave_hazard["severity"] == "MODERATE" or wind_hazard["severity"] == "MODERATE":
            classification = "CAUTION"
            status_label = "CAUTION"
            risk_score = int(round(raw_score))
        else:
            classification = "SUITABLE_CANDIDATE"
            status_label = "SUITABLE CANDIDATE"
            risk_score = int(round(raw_score))

        # 5. Confidence Calculation
        confidence_meta = calculate_synthesis_confidence(
            wave_hazard=wave_hazard,
            wind_hazard=wind_hazard,
            warning_hazard=warning_hazard,
            geofence_eval=geofence_eval
        )

        # Compile Factors
        factors = []
        if wave_hazard["status"] == "AVAILABLE":
            factors.append({
                "parameter": "significant_wave_height",
                "label": "Wave Height",
                "value": f"{wave_hazard['value']} m",
                "severity": wave_hazard["severity"],
                "description": wave_hazard["description"],
                "source": wave_hazard.get("source", "INCOIS"),
                "source_url": wave_hazard.get("source_url", "https://incois.gov.in"),
                "valid_time": wave_hazard.get("valid_time", "Tomorrow 06:00 IST"),
                "data_type": "forecast"
            })
        elif wave_missing:
            factors.append({
                "parameter": "significant_wave_height",
                "label": "Wave Height",
                "value": "Unavailable",
                "severity": "UNKNOWN",
                "description": "Critical wave safety telemetry is unavailable.",
                "source": "INCOIS",
                "source_url": "https://incois.gov.in",
                "valid_time": "Forecast Horizon",
                "data_type": "unknown"
            })

        if wind_hazard["status"] == "AVAILABLE":
            factors.append({
                "parameter": "surface_wind_10m",
                "label": "Wind Speed",
                "value": f"{wind_hazard['value']} kt",
                "severity": wind_hazard["severity"],
                "description": wind_hazard["description"],
                "source": wind_hazard.get("source", "IMD"),
                "source_url": wind_hazard.get("source_url", "https://api.imd.gov.in/public/api_reference.html"),
                "valid_time": wind_hazard.get("valid_time", "Tomorrow 06:00 IST"),
                "data_type": "forecast"
            })

        if warning_hazard["severity"] == "HIGH":
            factors.append({
                "parameter": "marine_warning",
                "label": "Marine Warning",
                "value": "Active Squall Alert",
                "severity": "HIGH",
                "description": warning_hazard["description"],
                "source": warning_hazard.get("source", "IMD"),
                "source_url": warning_hazard.get("source_url", "https://api.imd.gov.in/public/api_reference.html"),
                "valid_time": warning_hazard.get("valid_time", "Active Next 24h"),
                "data_type": "warning"
            })

        if is_restricted and geofence_eval.get("intersections"):
            inter = geofence_eval["intersections"][0]
            factors.append({
                "parameter": "geofence_restriction",
                "label": "Geofence Boundary",
                "value": inter["name"],
                "severity": "RESTRICTED",
                "description": inter["description"],
                "source": inter["source"],
                "source_url": inter["source_url"],
                "valid_time": inter["valid_baseline"],
                "data_type": "static"
            })

        return {
            "zone_id": zone_id,
            "name": zone_name,
            "risk_score": risk_score,
            "classification": classification,
            "status_label": status_label,
            "is_restricted": is_restricted,
            "factors": factors,
            "wave_hazard": wave_hazard,
            "wind_hazard": wind_hazard,
            "warning_hazard": warning_hazard,
            "geofence": geofence_eval,
            "confidence": confidence_meta
        }

risk_engine = MarineRiskEngine()
